"""Seed data script for initial setup"""
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import Base
from app.models import (
    Organization, Branch, User, Supplier, ExpenseCategory,
    OnlinePlatform, PurchaseProductGroup
)
from app.api.deps import get_password_hash


def seed_database():
    # Fix DATABASE_URL for psycopg3 compatibility
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing_org = db.query(Organization).first()
        if existing_org:
            print("Database already seeded. Skipping...")
            return

        # Organization
        org = Organization(
            name="Cigkofteci Bey",
            code="CKB",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(org)
        db.flush()
        print(f"Created organization: {org.name}")

        # Branch
        branch = Branch(
            organization_id=org.id,
            name="Kadikoy Subesi",
            code="KDK",
            address="Kadikoy, Istanbul",
            phone="0216 555 1234",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(branch)
        db.flush()
        print(f"Created branch: {branch.name}")

        # User (admin)
        admin_user = User(
            organization_id=org.id,
            branch_id=branch.id,
            email="admin@cigkofte.com",
            password_hash=get_password_hash("admin123"),
            name="Okan Yucel",
            role="owner",
            is_active=True,
            is_super_admin=True,
            auth_provider="email",
            created_at=datetime.utcnow()
        )
        db.add(admin_user)
        db.flush()
        print(f"Created user: {admin_user.email}")

        # Suppliers
        suppliers = [
            {"name": "Cinar Lavas", "phone": "0532 111 2233", "branch_id": branch.id},
            {"name": "Metro Market", "phone": "0533 222 3344", "branch_id": branch.id},
            {"name": "Manav Ahmet", "phone": "0534 333 4455", "branch_id": branch.id},
        ]
        for sup_data in suppliers:
            sup = Supplier(**sup_data, is_active=True)
            db.add(sup)
        print(f"Created {len(suppliers)} suppliers")

        # Purchase Product Groups
        groups = [
            {"name": "Manav", "display_order": 1},
            {"name": "Lavas", "display_order": 2},
            {"name": "Kuru Gida", "display_order": 3},
            {"name": "Baharat", "display_order": 4},
        ]
        for grp_data in groups:
            grp = PurchaseProductGroup(**grp_data, is_active=True)
            db.add(grp)
        print(f"Created {len(groups)} purchase product groups")

        # Expense Categories
        expense_categories = [
            {"name": "Kira", "is_fixed": True, "display_order": 1},
            {"name": "Elektrik", "is_fixed": False, "display_order": 2},
            {"name": "Su", "is_fixed": False, "display_order": 3},
            {"name": "Dogalgaz", "is_fixed": False, "display_order": 4},
            {"name": "Internet", "is_fixed": True, "display_order": 5},
            {"name": "Personel Yemek", "is_fixed": False, "display_order": 6},
            {"name": "Diger", "is_fixed": False, "display_order": 7},
        ]
        for cat_data in expense_categories:
            cat = ExpenseCategory(**cat_data)
            db.add(cat)
        print(f"Created {len(expense_categories)} expense categories")

        # Online Platforms (with system channels)
        online_platforms = [
            {"name": "Salon", "channel_type": "pos_salon", "is_system": True, "display_order": 1},
            {"name": "Telefon Paket", "channel_type": "pos_telefon", "is_system": True, "display_order": 2},
            {"name": "Trendyol", "channel_type": "online", "is_system": False, "display_order": 3},
            {"name": "Getir", "channel_type": "online", "is_system": False, "display_order": 4},
            {"name": "Yemek Sepeti", "channel_type": "online", "is_system": False, "display_order": 5},
        ]
        for platform_data in online_platforms:
            platform = OnlinePlatform(**platform_data, is_active=True)
            db.add(platform)
        print(f"Created {len(online_platforms)} online platforms")

        db.commit()
        print("\nSeed completed successfully!")
        print(f"\nLogin credentials:")
        print(f"  Email: admin@cigkofte.com")
        print(f"  Password: admin123")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
