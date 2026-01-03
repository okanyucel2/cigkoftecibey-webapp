
import pytest
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.api.deps import get_current_user, get_branch_context
from app.models import User, Branch, UserBranch

# Use in-memory SQLite for speed and safety
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Create a fresh database for each test case.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Pre-populate required data (User, Branch)
    user = User(
        id=1, 
        email="test@example.com", 
        password_hash="hash", 
        is_active=True,
        is_super_admin=True,
        name="Test User"
    )
    branch = Branch(id=1, name="Test Branch", code="TEST", city="Istanbul", is_active=True)
    user_branch = UserBranch(user_id=1, branch_id=1, is_default=True, role="owner")
    
    session.add(user)
    session.add(branch)
    session.add(user_branch)
    session.commit()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    FastAPI TestClient with overridden dependencies.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    
    # No auth override needed if we get a valid token, OR we can override get_current_user
    # For integration testing, it's often better to login properly.
    # But for unit testing logic, overriding is faster.
    # Let's override auth for simplicity in this first harness.
    
    from app.api.deps import BranchContext
    
    def override_get_branch_context():
        # Return hardcoded mock to avoid DB session complexity in overrides
        user = User(id=1, email="test@example.com", is_super_admin=True, name="Test User")
        branch = Branch(id=1, name="Test Branch", city="Istanbul")
        return BranchContext(
            user=user,
            current_branch_id=1,
            current_branch=branch,
            accessible_branches=[branch],
            is_super_admin=True
        )

    app.dependency_overrides[get_branch_context] = override_get_branch_context

    def override_get_current_user():
        # Return super_admin user for testing protected endpoints
        return User(id=1, email="test@example.com", is_super_admin=True, name="Test User")

    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()
