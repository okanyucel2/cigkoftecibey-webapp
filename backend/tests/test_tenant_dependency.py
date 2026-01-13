"""
Tests for get_current_tenant dependency - Multi-tenant context extraction.

TDD: RED -> GREEN -> REFACTOR
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant, TenantContext


class TestGetCurrentTenant:
    """Test suite for get_current_tenant dependency"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        db = MagicMock(spec=Session)
        db.execute = MagicMock()
        return db

    @pytest.fixture
    def mock_user(self):
        """Mock user with organization"""
        user = Mock()
        user.id = 1
        user.organization_id = 42
        user.is_super_admin = False
        return user

    def test_tenant_from_user_organization(self, mock_db, mock_user):
        """Should extract tenant_id from user's organization"""
        # Simulate request with no headers/params
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.query_params = {}

        result = get_current_tenant(
            request=mock_request,
            db=mock_db,
            user=mock_user
        )

        assert result.tenant_id == 42
        assert result.source == "user"

    def test_tenant_from_header(self, mock_db, mock_user):
        """Should extract tenant_id from X-Tenant-ID header (dev/API use)"""
        mock_request = Mock()
        mock_request.headers = {"x-tenant-id": "99"}
        mock_request.query_params = {}

        # Super admin can use any tenant via header
        mock_user.is_super_admin = True

        result = get_current_tenant(
            request=mock_request,
            db=mock_db,
            user=mock_user
        )

        assert result.tenant_id == 99
        assert result.source == "header"

    def test_tenant_from_query_param(self, mock_db, mock_user):
        """Should extract tenant_id from ?tenant= query param (dev only)"""
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.query_params = {"tenant": "77"}

        # Super admin can use query param
        mock_user.is_super_admin = True

        result = get_current_tenant(
            request=mock_request,
            db=mock_db,
            user=mock_user
        )

        assert result.tenant_id == 77
        assert result.source == "query"

    def test_priority_user_over_header(self, mock_db, mock_user):
        """Non-super-admin should use their organization, ignoring header"""
        mock_request = Mock()
        mock_request.headers = {"x-tenant-id": "99"}
        mock_request.query_params = {}

        # Regular user - should use their org, not header
        mock_user.is_super_admin = False

        result = get_current_tenant(
            request=mock_request,
            db=mock_db,
            user=mock_user
        )

        # Regular user always uses their organization
        assert result.tenant_id == 42
        assert result.source == "user"

    def test_missing_tenant_raises_error(self, mock_db):
        """Should raise HTTPException if no tenant context available"""
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.query_params = {}

        # User without organization
        mock_user = Mock()
        mock_user.id = 1
        mock_user.organization_id = None
        mock_user.is_super_admin = False

        with pytest.raises(HTTPException) as exc_info:
            get_current_tenant(
                request=mock_request,
                db=mock_db,
                user=mock_user
            )

        assert exc_info.value.status_code == 400
        assert "Tenant" in exc_info.value.detail

    def test_sets_postgres_session_variable(self, mock_db, mock_user):
        """Should set app.current_tenant PostgreSQL session variable"""
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.query_params = {}

        get_current_tenant(
            request=mock_request,
            db=mock_db,
            user=mock_user
        )

        # Verify execute was called with set_config
        mock_db.execute.assert_called_once()
        call_args = mock_db.execute.call_args
        sql_text = str(call_args[0][0])
        assert "set_config" in sql_text
        assert "app.current_tenant" in sql_text

    def test_set_config_is_transaction_scoped(self, mock_db, mock_user):
        """
        CRITICAL: set_config must use 'true' (transaction-scoped), not 'false' (session-scoped).

        With 'false': Config persists across transactions → connection pool leak
        With 'true': Config resets at transaction end → proper isolation
        """
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.query_params = {}

        get_current_tenant(
            request=mock_request,
            db=mock_db,
            user=mock_user
        )

        # Verify the SQL uses 'true' for transaction-scoped config
        call_args = mock_db.execute.call_args
        sql_text = str(call_args[0][0])
        # The third parameter to set_config must be 'true' for transaction scope
        assert "true" in sql_text.lower(), \
            "set_config must use 'true' (transaction-scoped) to prevent connection pool leak"

    def test_tenant_context_dataclass(self, mock_db, mock_user):
        """TenantContext should contain all required fields"""
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.query_params = {}

        result = get_current_tenant(
            request=mock_request,
            db=mock_db,
            user=mock_user
        )

        assert hasattr(result, 'tenant_id')
        assert hasattr(result, 'source')
        assert hasattr(result, 'user')
        assert result.user == mock_user


    def test_tenant_override_logs_warning(self, mock_db, mock_user):
        """Should log warning when super admin uses X-Tenant-ID header"""
        mock_request = Mock()
        mock_request.headers = {"x-tenant-id": "99"}
        mock_request.query_params = {}
        mock_user.is_super_admin = True
        mock_user.email = "admin@test.com"

        with patch('app.api.deps.logger') as mock_logger:
            get_current_tenant(
                request=mock_request,
                db=mock_db,
                user=mock_user
            )

            # Verify warning was logged
            mock_logger.warning.assert_called_once()
            call_args = str(mock_logger.warning.call_args)
            assert "tenant" in call_args.lower() or "override" in call_args.lower()

    def test_super_admin_sets_bypass_flag(self, mock_db, mock_user):
        """Super admin should set app.is_superuser flag for RLS bypass"""
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.query_params = {}
        mock_user.is_super_admin = True

        get_current_tenant(
            request=mock_request,
            db=mock_db,
            user=mock_user
        )

        # Verify set_config was called twice (tenant + superuser flag)
        assert mock_db.execute.call_count == 2
        # Check the SQL text of each call
        sql_texts = [str(c[0][0]) for c in mock_db.execute.call_args_list]
        assert any('is_superuser' in sql for sql in sql_texts), \
            f"Super admin should set app.is_superuser flag for RLS bypass. Got: {sql_texts}"

    def test_regular_user_no_bypass_flag(self, mock_db, mock_user):
        """Regular user should NOT set app.is_superuser flag"""
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.query_params = {}
        mock_user.is_super_admin = False

        get_current_tenant(
            request=mock_request,
            db=mock_db,
            user=mock_user
        )

        # Verify set_config was called only once (tenant only, no superuser)
        assert mock_db.execute.call_count == 1
        call_text = str(mock_db.execute.call_args)
        assert 'is_superuser' not in call_text


class TestTenantContextDataclass:
    """Test TenantContext dataclass"""

    def test_tenant_context_creation(self):
        """Should create TenantContext with required fields"""
        mock_user = Mock()
        mock_user.id = 1

        ctx = TenantContext(
            tenant_id=42,
            source="user",
            user=mock_user
        )

        assert ctx.tenant_id == 42
        assert ctx.source == "user"
        assert ctx.user == mock_user
