"""
Tests for /api/users endpoint

TDD: Written to reproduce 500 error when user has branch_id=NULL
Reference: Session 2026-01-03, P0.45 violation incident
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, Branch, UserBranch


class TestUsersEndpoint:
    """Test GET /api/users handles users with NULL branch_id"""

    def test_get_users_with_null_branch_id_does_not_500(self, client: TestClient, db: Session):
        """
        Regression test: Users with branch_id=NULL should not cause 500 error.

        Root cause: UserWithBranchesResponse had `branch_id: int` (non-nullable)
        but database allows NULL for users without primary branch.

        Fix: Make branch_id Optional[int] in response schema.
        """
        # Create a user with NULL branch_id (this is valid in the data model)
        user_with_null_branch = User(
            email="nullbranch@test.com",
            password_hash="dummyhash",
            name="Null Branch User",
            role="owner",
            branch_id=None,  # This is what causes the 500
            organization_id=None,
            is_active=True,
            is_super_admin=False
        )
        db.add(user_with_null_branch)
        db.commit()

        # GET /api/users should return 200, not 500
        # Note: The test client has override that makes current user super_admin
        response = client.get("/api/users")

        # This assertion will FAIL before the fix (currently returns 500)
        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}: {response.text}"

    def test_get_users_with_valid_branch_id_works(self, client: TestClient, db: Session):
        """Verify normal case still works: user with valid branch_id"""
        # Create branch
        branch = Branch(name="Test Branch 2", code="TESTB2", is_active=True)
        db.add(branch)
        db.flush()

        # Create user with valid branch_id
        user = User(
            email="validbranch@test.com",
            password_hash="dummyhash",
            name="Valid Branch User",
            role="owner",
            branch_id=branch.id,
            is_active=True,
            is_super_admin=False
        )
        db.add(user)

        # Also add to user_branches for full relationship
        db.commit()
        db.flush()

        user_branch = UserBranch(
            user_id=user.id,
            branch_id=branch.id,
            role="owner",
            is_default=True
        )
        db.add(user_branch)
        db.commit()

        response = client.get("/api/users")

        assert response.status_code == 200
        data = response.json()

        # Find our test user in the response
        test_user = next((u for u in data if u["email"] == "validbranch@test.com"), None)
        assert test_user is not None
        assert test_user["branch_id"] == branch.id

    def test_get_users_returns_null_branch_id_correctly(self, client: TestClient, db: Session):
        """After fix, users with NULL branch_id should have null in response"""
        # Create a user with NULL branch_id
        user = User(
            email="nullresponse@test.com",
            password_hash="dummyhash",
            name="Null Response User",
            role="owner",
            branch_id=None,
            is_active=True,
            is_super_admin=False
        )
        db.add(user)
        db.commit()

        response = client.get("/api/users")
        assert response.status_code == 200

        data = response.json()
        test_user = next((u for u in data if u["email"] == "nullresponse@test.com"), None)
        assert test_user is not None
        assert test_user["branch_id"] is None, \
            "Users with NULL branch_id should return null in JSON"
