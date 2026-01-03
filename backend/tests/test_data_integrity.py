"""
Data Integrity Tests for User Context Requirements (P0.40 Extended)

Following P0.40 TDD: Data operations must have test coverage.
These tests verify the integrity patterns that prevent 422 "Sube bulunamadi" errors.

Reference: Session 2026-01-03, 422 error fix
Pattern: User must have organization_id AND branch_id for API access.
"""
import pytest
from sqlalchemy.orm import Session

from app.models import User, Organization, Branch, UserBranch


class TestUserContextPattern:
    """
    Test the user context pattern that prevents 422 errors.

    Pattern: Users need organization_id + branch_id for API endpoints to work.
    Without this context, endpoints return "Sube bulunamadi".
    """

    def test_user_with_full_context_can_be_created(self, db: Session):
        """User with org/branch context should be valid"""
        # Create organization first
        org = Organization(name="Test Org", code="TESTORG", is_active=True)
        db.add(org)
        db.flush()  # Get ID

        # Create branch linked to organization
        branch = Branch(
            name="Test Branch",
            code="TESTBRANCH",
            organization_id=org.id,
            is_active=True
        )
        db.add(branch)
        db.flush()

        # Create user with full context
        user = User(
            email="contextuser@test.com",
            password_hash="dummy",
            name="Context User",
            organization_id=org.id,
            branch_id=branch.id,
            is_active=True
        )
        db.add(user)
        db.commit()

        # Verify context integrity
        queried_user = db.query(User).filter(User.email == "contextuser@test.com").first()
        assert queried_user is not None
        assert queried_user.organization_id is not None, "User must have organization"
        assert queried_user.branch_id is not None, "User must have branch"
        assert queried_user.organization_id == org.id
        assert queried_user.branch_id == branch.id

    def test_user_without_branch_is_detected(self, db: Session):
        """Detect users missing branch_id (would cause 422)"""
        org = Organization(name="No Branch Org", code="NOBRANCHORG", is_active=True)
        db.add(org)
        db.flush()

        # User without branch - this is the problematic pattern
        user_no_branch = User(
            email="nobranch@test.com",
            password_hash="dummy",
            name="No Branch User",
            organization_id=org.id,
            branch_id=None,  # MISSING - would cause 422!
            is_active=True
        )
        db.add(user_no_branch)
        db.commit()

        # Query pattern to detect this issue
        users_without_branch = db.query(User).filter(
            User.branch_id.is_(None),
            User.is_active == True
        ).all()

        # This assertion documents the problem pattern
        assert len(users_without_branch) > 0, "Test setup should have user without branch"

        # In production, this query should return 0 for healthy state
        # (excluding system accounts like healthcheck)

    def test_user_without_organization_is_detected(self, db: Session):
        """Detect users missing organization_id"""
        # User without organization - also problematic
        user_no_org = User(
            email="noorg@test.com",
            password_hash="dummy",
            name="No Org User",
            organization_id=None,  # MISSING
            branch_id=None,
            is_active=True
        )
        db.add(user_no_org)
        db.commit()

        users_without_org = db.query(User).filter(
            User.organization_id.is_(None),
            User.is_active == True
        ).all()

        # Includes both our new user and the fixture test user
        assert len(users_without_org) >= 1

    def test_branch_must_link_to_organization(self, db: Session):
        """Branch should belong to an organization for proper context"""
        org = Organization(name="Parent Org", code="PARENTORG", is_active=True)
        db.add(org)
        db.flush()

        branch = Branch(
            name="Linked Branch",
            code="LINKEDBRANCH",
            organization_id=org.id,
            is_active=True
        )
        db.add(branch)
        db.commit()

        queried_branch = db.query(Branch).filter(Branch.code == "LINKEDBRANCH").first()
        assert queried_branch.organization_id == org.id, "Branch should link to organization"

    def test_user_branch_matches_organization(self, db: Session):
        """User's branch should belong to user's organization (integrity check)"""
        org = Organization(name="Match Org", code="MATCHORG", is_active=True)
        db.add(org)
        db.flush()

        branch = Branch(
            name="Match Branch",
            code="MATCHBRANCH",
            organization_id=org.id,
            is_active=True
        )
        db.add(branch)
        db.flush()

        user = User(
            email="matchuser@test.com",
            password_hash="dummy",
            name="Match User",
            organization_id=org.id,
            branch_id=branch.id,
            is_active=True
        )
        db.add(user)
        db.commit()

        # Integrity check: user's branch should belong to user's organization
        user = db.query(User).filter(User.email == "matchuser@test.com").first()
        branch = db.query(Branch).filter(Branch.id == user.branch_id).first()

        assert branch.organization_id == user.organization_id, \
            "User's branch must belong to user's organization"


class TestBaseDataIntegrity:
    """Test that base data structures are correct"""

    def test_organization_can_be_created_with_minimum_fields(self, db: Session):
        """Organization requires name and code"""
        org = Organization(name="Min Org", code="MINORG")
        db.add(org)
        db.commit()

        saved = db.query(Organization).filter(Organization.code == "MINORG").first()
        assert saved is not None
        assert saved.is_active == True  # Default value

    def test_branch_can_be_created_with_minimum_fields(self, db: Session):
        """Branch requires name and code (organization optional for legacy)"""
        branch = Branch(name="Min Branch", code="MINBRANCH")
        db.add(branch)
        db.commit()

        saved = db.query(Branch).filter(Branch.code == "MINBRANCH").first()
        assert saved is not None
        assert saved.is_active == True  # Default value

    def test_user_branch_relationship(self, db: Session):
        """UserBranch table correctly links users to branches"""
        # Use existing fixture data
        user = db.query(User).filter(User.email == "test@example.com").first()

        user_branches = db.query(UserBranch).filter(UserBranch.user_id == user.id).all()
        assert len(user_branches) >= 1, "Test user should have at least one branch"

        # Verify the relationship integrity
        for ub in user_branches:
            branch = db.query(Branch).filter(Branch.id == ub.branch_id).first()
            assert branch is not None, "UserBranch should reference valid branch"


class TestHealthCheckUserPattern:
    """Test health check user pattern (P0.42)"""

    def test_health_check_user_can_be_created(self, db: Session):
        """Health check user pattern should work"""
        org = Organization(name="Health Org", code="HEALTHORG", is_active=True)
        db.add(org)
        db.flush()

        branch = Branch(
            name="Health Branch",
            code="HEALTHBRANCH",
            organization_id=org.id,
            is_active=True
        )
        db.add(branch)
        db.flush()

        health_user = User(
            email="healthcheck@internal.system",
            password_hash="dummy",
            name="Health Check User",
            role="health_check",
            organization_id=org.id,
            branch_id=branch.id,
            is_active=True
        )
        db.add(health_user)
        db.commit()

        saved = db.query(User).filter(User.email == "healthcheck@internal.system").first()
        assert saved is not None
        assert saved.role == "health_check"
        assert saved.is_active == True
