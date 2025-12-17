"""Seed data script for initial setup"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import Base
from app.models import (
    Branch, User, ProductCategory, Product,
    Supplier, ExpenseCategory, OnlinePlatform
)
from app.api.deps import get_password_hash


def seed_database():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing_branch = db.query(Branch).first()
        if existing_branch:
            print("Database already seeded. Skipping...")
            return

        # Branch
        branch = Branch(
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
            branch_id=branch.id,
            email="admin@cigkofte.com",
            password_hash=get_password_hash("admin123"),
            name="Okan Yucel",
            role="owner",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(admin_user)
        print(f"Created user: {admin_user.email}")

        # Product Categories
        categories = [
            {"name": "Cig Kofte", "display_order": 1},
            {"name": "Icecekler", "display_order": 2},
            {"name": "Sos & Ekstra", "display_order": 3},
            {"name": "Tatlilar", "display_order": 4},
        ]
        category_map = {}
        for cat_data in categories:
            cat = ProductCategory(**cat_data, is_active=True)
            db.add(cat)
            db.flush()
            category_map[cat.name] = cat.id
        print(f"Created {len(categories)} product categories")

        # Products
        products = [
            # Cig Kofte
            {"name": "Durum", "price": Decimal("45.00"), "category_id": category_map["Cig Kofte"], "display_order": 1},
            {"name": "Porsiyon", "price": Decimal("35.00"), "category_id": category_map["Cig Kofte"], "display_order": 2},
            {"name": "Tombik", "price": Decimal("55.00"), "category_id": category_map["Cig Kofte"], "display_order": 3},
            {"name": "Cocuk Porsiyon", "price": Decimal("25.00"), "category_id": category_map["Cig Kofte"], "display_order": 4},
            {"name": "Tam Ekmek", "price": Decimal("120.00"), "category_id": category_map["Cig Kofte"], "display_order": 5},
            {"name": "Yarim Ekmek", "price": Decimal("70.00"), "category_id": category_map["Cig Kofte"], "display_order": 6},
            {"name": "Aile Boyu", "price": Decimal("180.00"), "category_id": category_map["Cig Kofte"], "display_order": 7},
            {"name": "Lavas (Tek)", "price": Decimal("5.00"), "category_id": category_map["Cig Kofte"], "display_order": 8},
            # Icecekler
            {"name": "Ayran", "price": Decimal("15.00"), "category_id": category_map["Icecekler"], "display_order": 1},
            {"name": "Kola", "price": Decimal("20.00"), "category_id": category_map["Icecekler"], "display_order": 2},
            {"name": "Fanta", "price": Decimal("20.00"), "category_id": category_map["Icecekler"], "display_order": 3},
            {"name": "Salgam", "price": Decimal("18.00"), "category_id": category_map["Icecekler"], "display_order": 4},
            {"name": "Su (0.5L)", "price": Decimal("8.00"), "category_id": category_map["Icecekler"], "display_order": 5},
            {"name": "Su (1L)", "price": Decimal("12.00"), "category_id": category_map["Icecekler"], "display_order": 6},
            # Sos & Ekstra
            {"name": "Nar Eksisi", "price": Decimal("5.00"), "category_id": category_map["Sos & Ekstra"], "display_order": 1},
            {"name": "Acili Sos", "price": Decimal("5.00"), "category_id": category_map["Sos & Ekstra"], "display_order": 2},
            {"name": "Marul", "price": Decimal("3.00"), "category_id": category_map["Sos & Ekstra"], "display_order": 3},
            {"name": "Turp", "price": Decimal("3.00"), "category_id": category_map["Sos & Ekstra"], "display_order": 4},
            # Tatlilar
            {"name": "Kunefe", "price": Decimal("65.00"), "category_id": category_map["Tatlilar"], "display_order": 1},
            {"name": "Sutlac", "price": Decimal("35.00"), "category_id": category_map["Tatlilar"], "display_order": 2},
        ]
        for prod_data in products:
            prod = Product(**prod_data, is_active=True)
            db.add(prod)
        print(f"Created {len(products)} products")

        # Suppliers
        suppliers = [
            {"name": "Cinar Lavas", "phone": "0532 111 2233", "branch_id": branch.id},
            {"name": "Metro Market", "phone": "0533 222 3344", "branch_id": branch.id},
            {"name": "Manav Ahmet", "phone": "0534 333 4455", "branch_id": branch.id},
            {"name": "Kasap Mehmet", "phone": "0535 444 5566", "branch_id": branch.id},
            {"name": "Isot Deposu", "phone": "0536 555 6677", "branch_id": branch.id},
        ]
        for sup_data in suppliers:
            sup = Supplier(**sup_data, is_active=True)
            db.add(sup)
        print(f"Created {len(suppliers)} suppliers")

        # Expense Categories
        expense_categories = [
            {"name": "Kira", "is_fixed": True, "display_order": 1},
            {"name": "Elektrik", "is_fixed": False, "display_order": 2},
            {"name": "Su", "is_fixed": False, "display_order": 3},
            {"name": "Dogalgaz", "is_fixed": False, "display_order": 4},
            {"name": "Internet", "is_fixed": True, "display_order": 5},
            {"name": "Arac Yakit", "is_fixed": False, "display_order": 6},
            {"name": "Arac Bakim", "is_fixed": False, "display_order": 7},
            {"name": "Personel Yemek", "is_fixed": False, "display_order": 8},
            {"name": "Temizlik Malzemesi", "is_fixed": False, "display_order": 9},
            {"name": "Diger", "is_fixed": False, "display_order": 10},
        ]
        for cat_data in expense_categories:
            cat = ExpenseCategory(**cat_data)
            db.add(cat)
        print(f"Created {len(expense_categories)} expense categories")

        # Online Platforms
        online_platforms = [
            {"name": "Trendyol", "display_order": 1},
            {"name": "Getir", "display_order": 2},
            {"name": "Yemek Sepeti", "display_order": 3},
            {"name": "Migros Yemek", "display_order": 4},
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
