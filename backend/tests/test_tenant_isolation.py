"""
Tests for multi-tenant isolation using tenant fixtures.

Verifies that:
- Multiple tenants are properly isolated
- Cross-tenant access is prevented
- Super admin can access all tenants
"""
import pytest
from sqlalchemy import Column, Integer, String

from app.database import Base
from app.models.mixins import TenantMixin
from tests.fixtures.tenant_fixtures import (
    multi_tenant_db,
    tenant1_context,
    tenant2_context,
    super_admin_context,
    tenant_isolation_helper,
    TenantIsolationHelper,
)


class TenantScopedRecord(TenantMixin, Base):
    """Test model for tenant isolation testing"""
    __tablename__ = "test_tenant_scoped_records"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))


class TestTenantFixtures:
    """Test that tenant fixtures are set up correctly"""

    def test_multi_tenant_db_creates_two_orgs(self, multi_tenant_db):
        """Should create 2 organizations"""
        from app.models import Organization
        orgs = multi_tenant_db.query(Organization).all()
        assert len(orgs) == 2
        assert orgs[0].name == "Tenant One Inc"
        assert orgs[1].name == "Tenant Two Corp"

    def test_tenant_contexts_have_correct_ids(self, tenant1_context, tenant2_context):
        """Tenant contexts should have correct IDs"""
        assert tenant1_context["tenant_id"] == 1
        assert tenant1_context["org_id"] == 1
        assert tenant1_context["branch_id"] == 1

        assert tenant2_context["tenant_id"] == 2
        assert tenant2_context["org_id"] == 2
        assert tenant2_context["branch_id"] == 2

    def test_users_belong_to_correct_orgs(self, tenant1_context, tenant2_context):
        """Users should belong to their respective organizations"""
        user1 = tenant1_context["user"]
        user2 = tenant2_context["user"]

        assert user1.organization_id == 1
        assert user2.organization_id == 2
        assert user1.email == "user1@tenant1.com"
        assert user2.email == "user2@tenant2.com"

    def test_super_admin_flag(self, super_admin_context):
        """Super admin should be flagged correctly"""
        admin = super_admin_context["user"]
        assert admin.is_super_admin is True
        assert super_admin_context["can_access_all"] is True


class TestTenantIsolation:
    """Test tenant isolation with TenantMixin models"""

    def test_records_have_tenant_id(self, multi_tenant_db):
        """Records using TenantMixin should have tenant_id"""
        # Create the test table
        TenantScopedRecord.__table__.create(multi_tenant_db.get_bind(), checkfirst=True)

        record = TenantScopedRecord(name="Test", tenant_id=1)
        multi_tenant_db.add(record)
        multi_tenant_db.commit()

        assert record.tenant_id == 1

    def test_query_by_tenant_returns_only_that_tenant(self, multi_tenant_db):
        """Querying by tenant_id should return only that tenant's records"""
        TenantScopedRecord.__table__.create(multi_tenant_db.get_bind(), checkfirst=True)

        # Create records for both tenants
        t1_record = TenantScopedRecord(name="Tenant 1 Record", tenant_id=1)
        t2_record = TenantScopedRecord(name="Tenant 2 Record", tenant_id=2)
        multi_tenant_db.add_all([t1_record, t2_record])
        multi_tenant_db.commit()

        # Query for tenant 1
        tenant1_records = multi_tenant_db.query(TenantScopedRecord).filter(
            TenantScopedRecord.tenant_id == 1
        ).all()

        assert len(tenant1_records) == 1
        assert tenant1_records[0].name == "Tenant 1 Record"
        assert tenant1_records[0].tenant_id == 1

    def test_no_cross_tenant_leakage(self, multi_tenant_db, tenant_isolation_helper):
        """Records from one tenant should not leak to another"""
        TenantScopedRecord.__table__.create(multi_tenant_db.get_bind(), checkfirst=True)

        # Create multiple records per tenant
        for i in range(3):
            multi_tenant_db.add(TenantScopedRecord(name=f"T1-{i}", tenant_id=1))
            multi_tenant_db.add(TenantScopedRecord(name=f"T2-{i}", tenant_id=2))
        multi_tenant_db.commit()

        tenant_isolation_helper.assert_no_cross_tenant_access(
            TenantScopedRecord,
            tenant1_id=1,
            tenant2_id=2
        )


class TestTenantIsolationHelper:
    """Test the TenantIsolationHelper utility"""

    def test_assert_record_belongs_to_tenant_passes(self, multi_tenant_db):
        """Should pass when record has correct tenant_id"""
        TenantScopedRecord.__table__.create(multi_tenant_db.get_bind(), checkfirst=True)

        record = TenantScopedRecord(name="Test", tenant_id=1)
        multi_tenant_db.add(record)
        multi_tenant_db.commit()

        helper = TenantIsolationHelper(multi_tenant_db)
        helper.assert_record_belongs_to_tenant(record, 1)  # Should not raise

    def test_assert_record_belongs_to_tenant_fails(self, multi_tenant_db):
        """Should fail when record has wrong tenant_id"""
        TenantScopedRecord.__table__.create(multi_tenant_db.get_bind(), checkfirst=True)

        record = TenantScopedRecord(name="Test", tenant_id=1)
        multi_tenant_db.add(record)
        multi_tenant_db.commit()

        helper = TenantIsolationHelper(multi_tenant_db)
        with pytest.raises(AssertionError):
            helper.assert_record_belongs_to_tenant(record, 2)  # Wrong tenant
