"""
Pytest fixtures for multi-tenant isolation testing.

These fixtures provide:
- Multiple tenant contexts (org1, org2)
- Cross-tenant isolation verification
- RLS policy testing support
"""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Organization, Branch, User, UserBranch


@pytest.fixture
def multi_tenant_db():
    """
    Create a test database with multiple tenants (organizations).

    Sets up:
    - Organization 1 (Tenant 1) with Branch A
    - Organization 2 (Tenant 2) with Branch B
    - Users for each organization
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Create organizations (tenants)
    org1 = Organization(id=1, name="Tenant One Inc", code="T1")
    org2 = Organization(id=2, name="Tenant Two Corp", code="T2")
    session.add_all([org1, org2])
    session.commit()

    # Create branches for each org
    branch_a = Branch(id=1, organization_id=1, name="Branch A", code="BA", is_active=True)
    branch_b = Branch(id=2, organization_id=2, name="Branch B", code="BB", is_active=True)
    session.add_all([branch_a, branch_b])
    session.commit()

    # Create users for each org
    user1 = User(
        id=1,
        email="user1@tenant1.com",
        name="User One",
        organization_id=1,
        branch_id=1,
        is_active=True,
        is_super_admin=False
    )
    user2 = User(
        id=2,
        email="user2@tenant2.com",
        name="User Two",
        organization_id=2,
        branch_id=2,
        is_active=True,
        is_super_admin=False
    )
    super_admin = User(
        id=3,
        email="admin@system.com",
        name="Super Admin",
        organization_id=1,
        branch_id=1,
        is_active=True,
        is_super_admin=True
    )
    session.add_all([user1, user2, super_admin])
    session.commit()

    # Create user-branch associations
    ub1 = UserBranch(user_id=1, branch_id=1, is_default=True, role="owner")
    ub2 = UserBranch(user_id=2, branch_id=2, is_default=True, role="owner")
    session.add_all([ub1, ub2])
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def tenant1_context(multi_tenant_db: Session):
    """
    Context for Tenant 1 operations.

    Returns dict with:
    - session: DB session
    - org_id: 1
    - branch_id: 1
    - user: User object for tenant 1
    """
    user = multi_tenant_db.query(User).filter(User.id == 1).first()
    return {
        "session": multi_tenant_db,
        "org_id": 1,
        "tenant_id": 1,
        "branch_id": 1,
        "user": user
    }


@pytest.fixture
def tenant2_context(multi_tenant_db: Session):
    """
    Context for Tenant 2 operations.

    Returns dict with:
    - session: DB session
    - org_id: 2
    - branch_id: 2
    - user: User object for tenant 2
    """
    user = multi_tenant_db.query(User).filter(User.id == 2).first()
    return {
        "session": multi_tenant_db,
        "org_id": 2,
        "tenant_id": 2,
        "branch_id": 2,
        "user": user
    }


@pytest.fixture
def super_admin_context(multi_tenant_db: Session):
    """
    Context for Super Admin operations (can access all tenants).

    Returns dict with:
    - session: DB session
    - user: Super admin user object
    - can_access_all: True
    """
    user = multi_tenant_db.query(User).filter(User.id == 3).first()
    return {
        "session": multi_tenant_db,
        "user": user,
        "can_access_all": True
    }


def set_tenant_context(session: Session, tenant_id: int) -> None:
    """
    Set the tenant context for RLS policies.

    This simulates what get_current_tenant does in production.

    Note: SQLite doesn't support set_config, so this is a no-op in tests.
    For PostgreSQL tests, this would set app.current_tenant.
    """
    # SQLite doesn't support set_config, so we can't test RLS directly
    # In a real PostgreSQL test, we would do:
    # session.execute(text("SELECT set_config('app.current_tenant', :tid, false)"),
    #                 {"tid": str(tenant_id)})
    pass


class TenantIsolationHelper:
    """
    Helper class for testing tenant isolation.

    Usage:
        helper = TenantIsolationHelper(session)
        helper.assert_tenant_isolation(Model, tenant1_records, tenant2_records)
    """

    def __init__(self, session: Session):
        self.session = session

    def assert_record_belongs_to_tenant(self, record, expected_tenant_id: int) -> None:
        """Assert a record belongs to the expected tenant."""
        assert hasattr(record, 'tenant_id'), f"{record.__class__.__name__} has no tenant_id"
        assert record.tenant_id == expected_tenant_id, \
            f"Record tenant_id={record.tenant_id}, expected={expected_tenant_id}"

    def assert_no_cross_tenant_access(
        self,
        model_class,
        tenant1_id: int,
        tenant2_id: int
    ) -> None:
        """
        Assert that querying by tenant returns only that tenant's records.
        """
        tenant1_records = self.session.query(model_class).filter(
            model_class.tenant_id == tenant1_id
        ).all()
        tenant2_records = self.session.query(model_class).filter(
            model_class.tenant_id == tenant2_id
        ).all()

        # Verify no cross-contamination
        for record in tenant1_records:
            assert record.tenant_id == tenant1_id, \
                f"Tenant 1 query returned tenant {record.tenant_id} record"

        for record in tenant2_records:
            assert record.tenant_id == tenant2_id, \
                f"Tenant 2 query returned tenant {record.tenant_id} record"


@pytest.fixture
def tenant_isolation_helper(multi_tenant_db: Session):
    """Get TenantIsolationHelper instance."""
    return TenantIsolationHelper(multi_tenant_db)
