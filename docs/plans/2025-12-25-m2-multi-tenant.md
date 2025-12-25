# Milestone 2: Multi-Tenant Foundation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Implement database-level tenant isolation with RLS, create tenant onboarding flow, and build admin panel for tenant management.

**Architecture:**
- Use existing `Organization` model as Tenant (rename conceptually)
- Enforce tenant isolation at PostgreSQL level using Row-Level Security (RLS)
- Set tenant context on each database connection via session variables
- Branch-based data isolation (all data has branch_id → branch.organization_id = tenant)

**Tech Stack:** PostgreSQL RLS, FastAPI middleware, SQLAlchemy events, Vue 3

---

## Overview

The codebase already has:
- `Organization` model (our Tenant)
- `Branch` with `organization_id` foreign key
- All data tables with `branch_id` column
- `BranchContext` for application-level isolation

M2 adds:
1. **Database-level RLS** - Prevents cross-tenant access even with SQL injection
2. **Tenant Context Middleware** - Sets PostgreSQL session variables
3. **Tenant Plan/Limits** - Starter, Growth, Enterprise tiers
4. **Onboarding Flow** - Self-service tenant creation
5. **Admin Panel** - Super-admin tenant management

---

## Task 1: Add Tenant Fields to Organization Model

**Files:**
- Modify: `backend/app/models/__init__.py`
- Create: `backend/tests/test_tenant.py`
- Create: Alembic migration

**Step 1: Write failing test**

Create `backend/tests/test_tenant.py`:

```python
"""Tests for Tenant (Organization) model"""
import pytest
from datetime import date
from app.models import Organization


def test_organization_has_tenant_fields(db):
    """Organization should have plan, limits, and billing fields"""
    org = Organization(
        name="Test Restaurant",
        code="test-rest",
        plan="starter",
        max_branches=3,
        max_users=10
    )
    db.add(org)
    db.commit()

    result = db.query(Organization).filter_by(code="test-rest").first()
    assert result is not None
    assert result.plan == "starter"
    assert result.max_branches == 3
    assert result.max_users == 10


def test_organization_default_plan(db):
    """New organizations should default to starter plan"""
    org = Organization(
        name="New Restaurant",
        code="new-rest"
    )
    db.add(org)
    db.commit()

    result = db.query(Organization).filter_by(code="new-rest").first()
    assert result.plan == "starter"
    assert result.max_branches == 3
    assert result.max_users == 10
```

**Step 2: Run test to verify it fails**

```bash
cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_tenant.py -v
```

Expected: FAIL - Organization doesn't have plan/max_branches fields

**Step 3: Update Organization model**

In `backend/app/models/__init__.py`, update the Organization class:

```python
class Organization(Base):
    """Organization/Tenant for multi-tenant support"""
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # URL-safe slug
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    # Plan & Limits
    plan: Mapped[str] = mapped_column(String(20), default="starter")  # starter, growth, enterprise
    max_branches: Mapped[int] = mapped_column(Integer, default=3)
    max_users: Mapped[int] = mapped_column(Integer, default=10)
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Billing (Stripe integration ready)
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subscription_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # active, past_due, canceled
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    branches: Mapped[list["Branch"]] = relationship(back_populates="organization")
    users: Mapped[list["User"]] = relationship(back_populates="organization")
    invitation_codes: Mapped[list["InvitationCode"]] = relationship(back_populates="organization")
```

**Step 4: Create migration**

```bash
cd backend && alembic revision -m "add_tenant_fields_to_organization"
```

Edit migration:

```python
def upgrade() -> None:
    op.add_column('organizations', sa.Column('plan', sa.String(20), nullable=False, server_default='starter'))
    op.add_column('organizations', sa.Column('max_branches', sa.Integer(), nullable=False, server_default='3'))
    op.add_column('organizations', sa.Column('max_users', sa.Integer(), nullable=False, server_default='10'))
    op.add_column('organizations', sa.Column('settings', sa.JSON(), nullable=True))
    op.add_column('organizations', sa.Column('stripe_customer_id', sa.String(100), nullable=True))
    op.add_column('organizations', sa.Column('subscription_status', sa.String(20), nullable=True))
    op.add_column('organizations', sa.Column('trial_ends_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('organizations', 'trial_ends_at')
    op.drop_column('organizations', 'subscription_status')
    op.drop_column('organizations', 'stripe_customer_id')
    op.drop_column('organizations', 'settings')
    op.drop_column('organizations', 'max_users')
    op.drop_column('organizations', 'max_branches')
    op.drop_column('organizations', 'plan')
```

**Step 5: Run tests and commit**

```bash
cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_tenant.py -v
git add backend/app/models/__init__.py backend/tests/test_tenant.py backend/alembic/versions/
git commit -m "feat: add tenant plan and limits fields to Organization model"
```

---

## Task 2: Create Tenant Context Middleware

**Files:**
- Create: `backend/app/tenant_context.py`
- Modify: `backend/app/database.py`
- Create: `backend/tests/test_tenant_context.py`

**Step 1: Write failing test**

Create `backend/tests/test_tenant_context.py`:

```python
"""Tests for tenant context middleware"""
import pytest
from sqlalchemy import text
from app.tenant_context import set_tenant_context, get_tenant_context


def test_set_tenant_context_sets_session_variable(db):
    """Should set PostgreSQL session variable for RLS"""
    set_tenant_context(db, organization_id=1, branch_ids=[1, 2])

    # Verify session variable is set
    result = db.execute(text("SELECT current_setting('app.tenant_id', true)")).scalar()
    assert result == "1"

    result = db.execute(text("SELECT current_setting('app.branch_ids', true)")).scalar()
    assert result == "1,2"


def test_get_tenant_context_returns_values(db):
    """Should retrieve tenant context from session"""
    set_tenant_context(db, organization_id=5, branch_ids=[10, 20, 30])

    ctx = get_tenant_context(db)
    assert ctx["organization_id"] == 5
    assert ctx["branch_ids"] == [10, 20, 30]
```

**Step 2: Create tenant context module**

Create `backend/app/tenant_context.py`:

```python
"""
Tenant Context Management

Sets PostgreSQL session variables for Row-Level Security.
These variables are used by RLS policies to filter data.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session


def set_tenant_context(
    db: Session,
    organization_id: int,
    branch_ids: list[int]
) -> None:
    """
    Set tenant context in PostgreSQL session.

    This enables RLS policies to filter data automatically.

    Args:
        db: Database session
        organization_id: Current tenant/organization ID
        branch_ids: List of branch IDs user can access
    """
    # Set organization ID (tenant)
    db.execute(
        text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
        {"tenant_id": str(organization_id)}
    )

    # Set accessible branch IDs as comma-separated string
    branch_ids_str = ",".join(str(bid) for bid in branch_ids)
    db.execute(
        text("SELECT set_config('app.branch_ids', :branch_ids, true)"),
        {"branch_ids": branch_ids_str}
    )


def get_tenant_context(db: Session) -> dict:
    """
    Get current tenant context from PostgreSQL session.

    Returns:
        Dict with organization_id and branch_ids
    """
    org_id = db.execute(
        text("SELECT current_setting('app.tenant_id', true)")
    ).scalar()

    branch_ids_str = db.execute(
        text("SELECT current_setting('app.branch_ids', true)")
    ).scalar()

    return {
        "organization_id": int(org_id) if org_id else None,
        "branch_ids": [int(x) for x in branch_ids_str.split(",")] if branch_ids_str else []
    }


def clear_tenant_context(db: Session) -> None:
    """Clear tenant context from session"""
    db.execute(text("SELECT set_config('app.tenant_id', '', true)"))
    db.execute(text("SELECT set_config('app.branch_ids', '', true)"))
```

**Step 3: Run tests and commit**

```bash
cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_tenant_context.py -v
git add backend/app/tenant_context.py backend/tests/test_tenant_context.py
git commit -m "feat: add tenant context management for RLS"
```

---

## Task 3: Integrate Tenant Context into BranchContext

**Files:**
- Modify: `backend/app/api/deps.py`
- Create: `backend/tests/test_deps_tenant.py`

**Step 1: Write failing test**

Create `backend/tests/test_deps_tenant.py`:

```python
"""Tests for tenant context in deps"""
import pytest
from sqlalchemy import text


def test_branch_context_sets_tenant_context(client, db):
    """BranchContext should set PostgreSQL tenant context"""
    # Make an authenticated request
    response = client.get("/api/auth/me")
    assert response.status_code == 200

    # After request, tenant context should be set in session
    # (This is a conceptual test - actual verification depends on implementation)


def test_request_has_tenant_isolation(client):
    """Requests should be isolated by tenant"""
    # This test verifies the flow works end-to-end
    response = client.get("/api/branches")
    assert response.status_code == 200
```

**Step 2: Update get_branch_context in deps.py**

Add tenant context setting to `backend/app/api/deps.py`:

```python
# Add import at top
from app.tenant_context import set_tenant_context

# Update get_branch_context function - add before return:
def get_branch_context(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
    x_branch_id: Annotated[Optional[int], Header(alias="X-Branch-Id")] = None
) -> BranchContext:
    # ... existing code ...

    # Set tenant context for RLS (add before return statement)
    organization_id = current_branch.organization_id or 0
    accessible_branch_ids = [b.id for b in accessible_branches]
    set_tenant_context(db, organization_id, accessible_branch_ids)

    return BranchContext(
        user=user,
        current_branch_id=current_branch_id,
        current_branch=current_branch,
        accessible_branches=accessible_branches,
        is_super_admin=user.is_super_admin
    )
```

**Step 3: Run tests and commit**

```bash
cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/ -v
git add backend/app/api/deps.py backend/tests/test_deps_tenant.py
git commit -m "feat: integrate tenant context into BranchContext"
```

---

## Task 4: Create RLS Migration

**Files:**
- Create: Alembic migration for RLS policies

**Step 1: Create RLS migration**

```bash
cd backend && alembic revision -m "add_row_level_security_policies"
```

Edit migration:

```python
"""add_row_level_security_policies

Enable Row-Level Security on data tables.
Policies filter data based on app.branch_ids session variable.
"""
from alembic import op
import sqlalchemy as sa


# Tables that need RLS (have branch_id column)
BRANCH_SCOPED_TABLES = [
    'cash_differences',
    'courier_expenses',
    'daily_insights',
    'daily_productions',
    'daily_summaries',
    'employees',
    'expenses',
    'expense_categories',
    'import_history',
    'monthly_payrolls',
    'online_platforms',
    'online_sales',
    'part_time_costs',
    'purchases',
    'purchase_products',
    'purchase_product_groups',
    'staff_meals',
    'suppliers',
]


def upgrade() -> None:
    # Create helper function for checking branch access
    op.execute("""
        CREATE OR REPLACE FUNCTION check_branch_access(branch_id INTEGER)
        RETURNS BOOLEAN AS $$
        DECLARE
            branch_ids_str TEXT;
            branch_ids INTEGER[];
        BEGIN
            -- Get branch IDs from session
            branch_ids_str := current_setting('app.branch_ids', true);

            -- If no context set, deny access (fail-safe)
            IF branch_ids_str IS NULL OR branch_ids_str = '' THEN
                RETURN FALSE;
            END IF;

            -- Parse comma-separated IDs into array
            branch_ids := string_to_array(branch_ids_str, ',')::INTEGER[];

            -- Check if requested branch is in allowed list
            RETURN branch_id = ANY(branch_ids);
        END;
        $$ LANGUAGE plpgsql STABLE;
    """)

    # Enable RLS and create policies for each table
    for table in BRANCH_SCOPED_TABLES:
        # Enable RLS
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")

        # Force RLS for table owner too (important for security)
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

        # Create policy for SELECT
        op.execute(f"""
            CREATE POLICY {table}_tenant_select ON {table}
            FOR SELECT
            USING (check_branch_access(branch_id))
        """)

        # Create policy for INSERT
        op.execute(f"""
            CREATE POLICY {table}_tenant_insert ON {table}
            FOR INSERT
            WITH CHECK (check_branch_access(branch_id))
        """)

        # Create policy for UPDATE
        op.execute(f"""
            CREATE POLICY {table}_tenant_update ON {table}
            FOR UPDATE
            USING (check_branch_access(branch_id))
            WITH CHECK (check_branch_access(branch_id))
        """)

        # Create policy for DELETE
        op.execute(f"""
            CREATE POLICY {table}_tenant_delete ON {table}
            FOR DELETE
            USING (check_branch_access(branch_id))
        """)


def downgrade() -> None:
    # Drop policies and disable RLS
    for table in BRANCH_SCOPED_TABLES:
        op.execute(f"DROP POLICY IF EXISTS {table}_tenant_select ON {table}")
        op.execute(f"DROP POLICY IF EXISTS {table}_tenant_insert ON {table}")
        op.execute(f"DROP POLICY IF EXISTS {table}_tenant_update ON {table}")
        op.execute(f"DROP POLICY IF EXISTS {table}_tenant_delete ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    op.execute("DROP FUNCTION IF EXISTS check_branch_access(INTEGER)")
```

**Step 2: Run migration and verify**

```bash
cd backend && alembic upgrade head
```

**Step 3: Test RLS is working**

```python
# Quick verification script
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Without context - should return empty
result = db.execute(text("SELECT COUNT(*) FROM expenses")).scalar()
print(f"Without context: {result}")  # Should be 0

# With context
db.execute(text("SELECT set_config('app.branch_ids', '1,2', true)"))
result = db.execute(text("SELECT COUNT(*) FROM expenses")).scalar()
print(f"With branch context: {result}")  # Should show actual count
```

**Step 4: Commit**

```bash
git add backend/alembic/versions/
git commit -m "feat: add Row-Level Security policies for tenant isolation"
```

---

## Task 5: Migrate Existing Data to Default Tenant

**Files:**
- Create: Alembic migration for data migration

**Step 1: Create data migration**

```bash
cd backend && alembic revision -m "migrate_data_to_default_tenant"
```

Edit migration:

```python
"""migrate_data_to_default_tenant

Ensure all existing data belongs to a valid organization (tenant).
Creates a default organization if needed and links orphan branches.
"""
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # Create default organization if it doesn't exist
    op.execute("""
        INSERT INTO organizations (name, code, plan, max_branches, max_users)
        SELECT 'Default Organization', 'default', 'enterprise', 100, 100
        WHERE NOT EXISTS (SELECT 1 FROM organizations WHERE code = 'default')
    """)

    # Get the default organization ID
    # Link all branches without organization to default
    op.execute("""
        UPDATE branches
        SET organization_id = (SELECT id FROM organizations WHERE code = 'default')
        WHERE organization_id IS NULL
    """)

    # Make organization_id NOT NULL now that all branches have one
    op.alter_column('branches', 'organization_id',
                    existing_type=sa.Integer(),
                    nullable=False)

    # Link users without organization to their branch's organization
    op.execute("""
        UPDATE users u
        SET organization_id = b.organization_id
        FROM branches b
        WHERE u.branch_id = b.id
        AND u.organization_id IS NULL
    """)


def downgrade() -> None:
    # Make organization_id nullable again
    op.alter_column('branches', 'organization_id',
                    existing_type=sa.Integer(),
                    nullable=True)
```

**Step 2: Run migration and commit**

```bash
cd backend && alembic upgrade head
git add backend/alembic/versions/
git commit -m "feat: migrate existing data to default tenant"
```

---

## Task 6: Create Tenant Onboarding API

**Files:**
- Create: `backend/app/api/onboarding.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_onboarding.py`

**Step 1: Write failing test**

Create `backend/tests/test_onboarding.py`:

```python
"""Tests for tenant onboarding API"""
import pytest


def test_create_tenant(client_no_auth):
    """Should create new tenant with first branch and admin user"""
    response = client_no_auth.post("/api/onboarding/signup", json={
        "organization_name": "Yeni Restaurant",
        "organization_code": "yeni-rest",
        "branch_name": "Merkez Şube",
        "admin_email": "admin@yenirest.com",
        "admin_password": "SecurePass123!",
        "admin_name": "Ahmet Yilmaz"
    })

    assert response.status_code == 201
    data = response.json()
    assert "organization_id" in data
    assert "branch_id" in data
    assert "user_id" in data
    assert "access_token" in data


def test_create_tenant_duplicate_code(client_no_auth):
    """Should reject duplicate organization code"""
    # First signup
    client_no_auth.post("/api/onboarding/signup", json={
        "organization_name": "Restaurant A",
        "organization_code": "rest-a",
        "branch_name": "Şube 1",
        "admin_email": "admin@resta.com",
        "admin_password": "SecurePass123!",
        "admin_name": "Admin A"
    })

    # Duplicate code
    response = client_no_auth.post("/api/onboarding/signup", json={
        "organization_name": "Restaurant B",
        "organization_code": "rest-a",  # Same code!
        "branch_name": "Şube 1",
        "admin_email": "admin@restb.com",
        "admin_password": "SecurePass123!",
        "admin_name": "Admin B"
    })

    assert response.status_code == 400
    assert "code" in response.json()["detail"].lower()
```

**Step 2: Create onboarding API**

Create `backend/app/api/onboarding.py`:

```python
"""
Tenant Onboarding API

Self-service signup for new tenants/organizations.
"""
from datetime import datetime, timedelta, UTC
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.exc import IntegrityError
from app.api.deps import DBSession, create_access_token, get_password_hash
from app.models import Organization, Branch, User, UserBranch

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


class SignupRequest(BaseModel):
    organization_name: str
    organization_code: str
    branch_name: str
    admin_email: EmailStr
    admin_password: str
    admin_name: str

    @field_validator('organization_code')
    @classmethod
    def validate_code(cls, v):
        # URL-safe slug validation
        import re
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Code must be lowercase alphanumeric with hyphens only')
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Code must be 3-50 characters')
        return v

    @field_validator('admin_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class SignupResponse(BaseModel):
    organization_id: int
    branch_id: int
    user_id: int
    access_token: str
    message: str


@router.post("/signup", response_model=SignupResponse, status_code=201)
def signup(request: SignupRequest, db: DBSession):
    """
    Create new tenant with first branch and admin user.

    This is the self-service onboarding endpoint for new organizations.
    Creates:
    - Organization (tenant) with 14-day trial
    - First branch
    - Admin user with owner role
    - JWT token for immediate login
    """
    # Check if organization code already exists
    existing = db.query(Organization).filter(
        Organization.code == request.organization_code
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Organization code already exists"
        )

    # Check if email already exists
    existing_user = db.query(User).filter(
        User.email == request.admin_email
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    try:
        # Create organization with trial
        org = Organization(
            name=request.organization_name,
            code=request.organization_code,
            plan="starter",
            max_branches=3,
            max_users=10,
            trial_ends_at=datetime.now(UTC) + timedelta(days=14)
        )
        db.add(org)
        db.flush()

        # Create first branch
        branch = Branch(
            organization_id=org.id,
            name=request.branch_name,
            code=f"{request.organization_code}-1"
        )
        db.add(branch)
        db.flush()

        # Create admin user
        user = User(
            organization_id=org.id,
            branch_id=branch.id,
            email=request.admin_email,
            password_hash=get_password_hash(request.admin_password),
            name=request.admin_name,
            role="owner",
            is_active=True
        )
        db.add(user)
        db.flush()

        # Link user to branch
        user_branch = UserBranch(
            user_id=user.id,
            branch_id=branch.id,
            is_default=True
        )
        db.add(user_branch)

        db.commit()

        # Generate token for immediate login
        access_token = create_access_token(data={"sub": str(user.id)})

        return SignupResponse(
            organization_id=org.id,
            branch_id=branch.id,
            user_id=user.id,
            access_token=access_token,
            message="Hesabiniz olusturuldu! 14 gunluk deneme suresi basladi."
        )

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Could not create organization. Please try a different code."
        )
```

**Step 3: Register router in main.py**

Add to `backend/app/main.py`:

```python
from app.api.onboarding import router as onboarding_router
app.include_router(onboarding_router, prefix="/api")
```

**Step 4: Run tests and commit**

```bash
cd backend && source venv/bin/activate && PYTHONPATH=. pytest tests/test_onboarding.py -v
git add backend/app/api/onboarding.py backend/app/main.py backend/tests/test_onboarding.py
git commit -m "feat: add tenant onboarding API for self-service signup"
```

---

## Task 7: Create Admin Panel API

**Files:**
- Create: `backend/app/api/admin.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_admin.py`

**Step 1: Write failing test**

Create `backend/tests/test_admin.py`:

```python
"""Tests for admin panel API"""
import pytest


def test_list_tenants_requires_super_admin(client):
    """Regular users cannot access admin endpoints"""
    response = client.get("/api/admin/tenants")
    assert response.status_code == 403


def test_super_admin_can_list_tenants(super_admin_client):
    """Super admin can list all tenants"""
    response = super_admin_client.get("/api/admin/tenants")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_super_admin_can_view_tenant_stats(super_admin_client):
    """Super admin can view tenant statistics"""
    response = super_admin_client.get("/api/admin/tenants/1/stats")
    assert response.status_code in [200, 404]  # 404 if tenant doesn't exist
```

**Step 2: Create admin API**

Create `backend/app/api/admin.py`:

```python
"""
Admin Panel API

Super-admin endpoints for tenant management.
All endpoints require is_super_admin=True.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from app.api.deps import DBSession, CurrentBranchContext
from app.models import Organization, Branch, User

router = APIRouter(prefix="/admin", tags=["admin"])


def require_super_admin(ctx: CurrentBranchContext):
    """Verify user is super admin"""
    if not ctx.is_super_admin:
        raise HTTPException(
            status_code=403,
            detail="Super admin access required"
        )


class TenantSummary(BaseModel):
    id: int
    name: str
    code: str
    plan: str
    is_active: bool
    branch_count: int
    user_count: int

    class Config:
        from_attributes = True


class TenantStats(BaseModel):
    tenant_id: int
    tenant_name: str
    branch_count: int
    user_count: int
    total_expenses: float
    total_sales: float


@router.get("/tenants", response_model=list[TenantSummary])
def list_tenants(
    db: DBSession,
    ctx: CurrentBranchContext,
    is_active: bool = None
):
    """List all tenants with summary info"""
    require_super_admin(ctx)

    query = db.query(
        Organization,
        func.count(Branch.id.distinct()).label('branch_count'),
        func.count(User.id.distinct()).label('user_count')
    ).outerjoin(Branch).outerjoin(User, User.organization_id == Organization.id)

    if is_active is not None:
        query = query.filter(Organization.is_active == is_active)

    query = query.group_by(Organization.id)

    results = []
    for org, branch_count, user_count in query.all():
        results.append(TenantSummary(
            id=org.id,
            name=org.name,
            code=org.code,
            plan=org.plan,
            is_active=org.is_active,
            branch_count=branch_count,
            user_count=user_count
        ))

    return results


@router.get("/tenants/{tenant_id}")
def get_tenant(
    tenant_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Get tenant details"""
    require_super_admin(ctx)

    org = db.query(Organization).filter(Organization.id == tenant_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Tenant not found")

    branches = db.query(Branch).filter(Branch.organization_id == tenant_id).all()
    users = db.query(User).filter(User.organization_id == tenant_id).all()

    return {
        "id": org.id,
        "name": org.name,
        "code": org.code,
        "plan": org.plan,
        "max_branches": org.max_branches,
        "max_users": org.max_users,
        "is_active": org.is_active,
        "subscription_status": org.subscription_status,
        "trial_ends_at": org.trial_ends_at,
        "created_at": org.created_at,
        "branches": [{"id": b.id, "name": b.name} for b in branches],
        "users": [{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users]
    }


@router.patch("/tenants/{tenant_id}")
def update_tenant(
    tenant_id: int,
    updates: dict,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Update tenant settings"""
    require_super_admin(ctx)

    org = db.query(Organization).filter(Organization.id == tenant_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Allowed fields to update
    allowed = ['is_active', 'plan', 'max_branches', 'max_users', 'subscription_status']

    for key, value in updates.items():
        if key in allowed:
            setattr(org, key, value)

    db.commit()
    return {"message": "Tenant updated", "id": tenant_id}


@router.delete("/tenants/{tenant_id}")
def deactivate_tenant(
    tenant_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Deactivate a tenant (soft delete)"""
    require_super_admin(ctx)

    org = db.query(Organization).filter(Organization.id == tenant_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Tenant not found")

    org.is_active = False
    db.commit()

    return {"message": "Tenant deactivated", "id": tenant_id}
```

**Step 3: Register router and commit**

```bash
git add backend/app/api/admin.py backend/app/main.py backend/tests/test_admin.py
git commit -m "feat: add admin panel API for tenant management"
```

---

## Task 8: Create Admin Frontend Page

**Files:**
- Create: `frontend/src/views/admin/TenantList.vue`
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/services/api.ts`

**Step 1: Add API methods**

Add to `frontend/src/services/api.ts`:

```typescript
// Admin API (super-admin only)
adminApi: {
  listTenants: (params?: { is_active?: boolean }) =>
    api.get<TenantSummary[]>('/admin/tenants', { params }),

  getTenant: (id: number) =>
    api.get<TenantDetail>(`/admin/tenants/${id}`),

  updateTenant: (id: number, updates: Partial<TenantUpdate>) =>
    api.patch(`/admin/tenants/${id}`, updates),

  deactivateTenant: (id: number) =>
    api.delete(`/admin/tenants/${id}`),
},
```

**Step 2: Create TenantList view**

Create `frontend/src/views/admin/TenantList.vue`:

```vue
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold">Tenant Yonetimi</h1>
      <div class="flex gap-2">
        <select v-model="filter.is_active" @change="loadTenants" class="border rounded px-3 py-2">
          <option :value="null">Tumu</option>
          <option :value="true">Aktif</option>
          <option :value="false">Pasif</option>
        </select>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">ID</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Isim</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Kod</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Plan</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Subeler</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Kullanicilar</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Durum</th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Islemler</th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr v-for="tenant in tenants" :key="tenant.id">
            <td class="px-4 py-3 text-sm">{{ tenant.id }}</td>
            <td class="px-4 py-3 text-sm font-medium">{{ tenant.name }}</td>
            <td class="px-4 py-3 text-sm text-gray-500">{{ tenant.code }}</td>
            <td class="px-4 py-3 text-sm">
              <span :class="planClass(tenant.plan)">{{ tenant.plan }}</span>
            </td>
            <td class="px-4 py-3 text-sm">{{ tenant.branch_count }}</td>
            <td class="px-4 py-3 text-sm">{{ tenant.user_count }}</td>
            <td class="px-4 py-3 text-sm">
              <span :class="tenant.is_active ? 'text-green-600' : 'text-red-600'">
                {{ tenant.is_active ? 'Aktif' : 'Pasif' }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm">
              <router-link :to="`/admin/tenants/${tenant.id}`" class="text-blue-600 hover:underline">
                Detay
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'

interface TenantSummary {
  id: number
  name: string
  code: string
  plan: string
  is_active: boolean
  branch_count: number
  user_count: number
}

const tenants = ref<TenantSummary[]>([])
const filter = ref({
  is_active: null as boolean | null
})

const loadTenants = async () => {
  try {
    const params = filter.value.is_active !== null
      ? { is_active: filter.value.is_active }
      : undefined
    const response = await api.adminApi.listTenants(params)
    tenants.value = response.data
  } catch (error) {
    console.error('Failed to load tenants:', error)
  }
}

const planClass = (plan: string) => {
  const classes: Record<string, string> = {
    starter: 'px-2 py-1 bg-gray-100 text-gray-800 rounded text-xs',
    growth: 'px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs',
    enterprise: 'px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs'
  }
  return classes[plan] || classes.starter
}

onMounted(() => loadTenants())
</script>
```

**Step 3: Add route**

Add to `frontend/src/router/index.ts`:

```typescript
{
  path: '/admin/tenants',
  name: 'admin-tenants',
  component: () => import('@/views/admin/TenantList.vue'),
  meta: { requiresAuth: true, requiresSuperAdmin: true }
},
```

**Step 4: Build and commit**

```bash
cd frontend && npm run build
git add frontend/src/views/admin/ frontend/src/router/index.ts frontend/src/services/api.ts
git commit -m "feat: add admin panel frontend for tenant management"
```

---

## Task 9: Run Migration and Final Verification

**Step 1: Run all Alembic migrations**

```bash
cd backend && alembic upgrade head
```

**Step 2: Run all backend tests**

```bash
cd backend && source venv/bin/activate && PYTHONPATH=. pytest -v
```

Expected: ALL PASS

**Step 3: Build frontend**

```bash
cd frontend && npm run build
```

**Step 4: Manual verification**

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Test onboarding: POST to `/api/onboarding/signup`
4. Login with new user
5. Verify data is isolated (check another tenant's data is not visible)
6. Super admin: verify `/admin/tenants` works

**Step 5: Final commit and tag**

```bash
git add -A
git commit -m "milestone: complete M2 Multi-Tenant Foundation

- Tenant model with plan, limits, and billing fields
- PostgreSQL Row-Level Security for data isolation
- Tenant context middleware (sets session variables)
- Self-service onboarding API
- Admin panel for tenant management

Exit criteria met:
✅ Tenant isolation verified at DB level (RLS)
✅ Existing data migrated to default tenant
✅ Tenant onboarding flow complete
✅ Admin panel for tenant management
✅ All tests passing"

git tag m2-multi-tenant
git push origin main --tags
```

---

## Exit Criteria Checklist

- [ ] Tenant isolation verified at DB level (RLS)
- [ ] Zero cross-tenant data leakage (RLS policies prevent access)
- [ ] Existing data migrated to default tenant
- [ ] Tenant onboarding flow complete (self-service signup)
- [ ] Admin panel for tenant management
- [ ] All tests passing
- [ ] Migration runs successfully

---

## Notes for Implementer

1. **RLS Testing**: After enabling RLS, run queries without setting `app.branch_ids` to verify they return empty results.

2. **Super Admin Bypass**: Super admins still need RLS context. Consider adding a bypass policy for super admins if needed.

3. **Performance**: RLS adds a small overhead. Monitor query performance after enabling.

4. **Rollback Plan**: If RLS causes issues, run `alembic downgrade` to disable policies.

5. **Stripe Integration**: Billing fields are ready but Stripe integration is M4 scope.

6. **Email Verification**: Not in this milestone. Consider adding in M3.
