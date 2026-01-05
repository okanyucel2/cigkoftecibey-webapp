"""
Tests for TenantMixin - Multi-tenant infrastructure foundation.

TDD: RED -> GREEN -> REFACTOR
"""
import pytest
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Organization
from app.models.mixins import TenantMixin


class TenantScopedModel(TenantMixin, Base):
    """Test model using TenantMixin"""
    __tablename__ = "test_tenant_scoped"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))


@pytest.fixture
def tenant_db():
    """Create isolated test database with tenant tables"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables including organizations
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Create test organizations
    org1 = Organization(id=1, name="Test Org", code="TEST1")
    org2 = Organization(id=2, name="Other Org", code="TEST2")
    session.add_all([org1, org2])
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


class TestTenantMixin:
    """Test suite for TenantMixin"""

    def test_mixin_adds_tenant_id_column(self, tenant_db: Session):
        """TenantMixin should add tenant_id column to model"""
        # Check that TenantScopedModel has tenant_id attribute
        assert hasattr(TenantScopedModel, 'tenant_id')

        # Check column exists in table
        columns = [c.name for c in TenantScopedModel.__table__.columns]
        assert 'tenant_id' in columns

    def test_tenant_id_is_indexed(self, tenant_db: Session):
        """tenant_id should have an index for query performance"""
        tenant_id_col = TenantScopedModel.__table__.c.tenant_id
        assert tenant_id_col.index is True or any(
            idx for idx in TenantScopedModel.__table__.indexes
            if 'tenant_id' in [c.name for c in idx.columns]
        )

    def test_tenant_id_references_organizations(self, tenant_db: Session):
        """tenant_id should be a ForeignKey to organizations.id"""
        tenant_id_col = TenantScopedModel.__table__.c.tenant_id
        fks = list(tenant_id_col.foreign_keys)
        assert len(fks) == 1
        assert 'organizations.id' in str(fks[0].target_fullname)

    def test_can_create_record_with_tenant_id(self, tenant_db: Session):
        """Should be able to create records with tenant_id"""
        record = TenantScopedModel(name="Test Record", tenant_id=1)
        tenant_db.add(record)
        tenant_db.commit()

        assert record.id is not None
        assert record.tenant_id == 1

    def test_tenant_id_nullable_for_phase1(self, tenant_db: Session):
        """Phase 1: tenant_id should be nullable for gradual migration"""
        tenant_id_col = TenantScopedModel.__table__.c.tenant_id
        # In Phase 1, nullable=True for gradual migration
        # After Phase 2, this will become nullable=False
        assert tenant_id_col.nullable is True

    def test_records_isolated_by_tenant(self, tenant_db: Session):
        """Records from different tenants should be distinguishable"""
        # Create records for two different tenants
        record1 = TenantScopedModel(name="Tenant 1 Record", tenant_id=1)
        record2 = TenantScopedModel(name="Tenant 2 Record", tenant_id=2)
        tenant_db.add_all([record1, record2])
        tenant_db.commit()

        # Query by tenant
        tenant1_records = tenant_db.query(TenantScopedModel).filter(
            TenantScopedModel.tenant_id == 1
        ).all()
        tenant2_records = tenant_db.query(TenantScopedModel).filter(
            TenantScopedModel.tenant_id == 2
        ).all()

        assert len(tenant1_records) == 1
        assert len(tenant2_records) == 1
        assert tenant1_records[0].name == "Tenant 1 Record"
        assert tenant2_records[0].name == "Tenant 2 Record"
