"""Seed data script for initial setup"""
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import Base
from app.models import (
    Organization, Branch, User, Supplier, ExpenseCategory,
    OnlinePlatform, PurchaseProductGroup, PurchaseProduct
)
from app.api.deps import get_password_hash


def add_missing_data(db):
    """Add missing products and categories to existing database"""
    groups_with_products = {
        "Manav": [
            "Marul", "Nane", "Maydanoz", "Roka", "Tere", "Kivircik", "Aysberk",
            "Mor Lahana", "Havuc", "Turp", "Limon", "Reyhan", "Karpuz", "Patates",
            "Salatalik", "Yesil Sogan", "Soyulmus Sogan", "Sarimsak"
        ],
        "Lavas": ["Fabrika Lavas", "Muhammet Lavas", "Cinar Lavas"],
        "Kuru Gida": [
            "Esmer Bulgur", "Yemeklik Bulgur", "Pirinc", "Nohut", "Mercimek",
            "Makarna", "Kuru Fasulye", "Mor Isot", "Siyah Isot", "Cavusoglu",
            "Sos Isot", "Sos Baharati", "Baharat", "Tuz Mix", "Tat Salca",
            "Biber Salca", "Tuz", "Seker", "Nar Eksisi", "Zeytin Yag",
            "Aycicek Yag", "Cips", "Karanfil", "Cay", "Ketcap"
        ],
        "Tursu": ["Biber Tursusu", "Karisik Tursu"],
        "Icecek": [
            "Salgam", "Soda", "Su 330", "Damacana Su", "Eker Ayran",
            "Gazoz", "Yogurt", "Markasiz Su"
        ],
        "Ambalaj": [
            "Durum Kagit", "Durum Poset", "Plastik Catal", "Plastik Bardak",
            "Plastik Bicak", "Strec Buyuk", "Strec Kucuk", "Termal Rulo",
            "Pos Rulo", "Kurdan", "Kolonya", "Seffaf Eldiven", "Pudrali Eldiven",
            "Islak Mendil", "Baskili Poset", "Pipet", "Cop Poseti", "Catal Kilifi",
            "Cop Sitik", "Masa Pecetesi", "Et", "Kagit Havlu", "Tuvalet Kagit",
            "Z Pecete", "250 Gr Vakum Torbasi", "5 Kg Vakum Torbasi", "Terazi Etiketi"
        ],
        "Sizdirmazlar": [
            "250 Gr Susi", "250 Gr Yesillik", "500 Gr Kofte", "500 Gr Yesillik",
            "1 Kg Yesil Kap", "Tursu Kabi", "330 Pet Sise", "50 Gr Sos"
        ],
        "Temizlik": [
            "Domestos", "Yuzey Temizleyici", "Cif", "Sari Guc", "Kopuk Sabun",
            "Sivi Bulasik Elde", "Sivi Bulasik Makina", "Genel Temizlik", "Kirec Coz"
        ],
        "Tasinmazlar": [
            "Buyuk Boy Tepsi", "Kucuk Boy Tepsi", "Sosluk", "Kayik Tabak Genis",
            "Kayik Tabak Dar", "Su Bardagi", "Metal Catal", "Metal Bicak",
            "Sos Bidonu", "Plastik Kuvet", "Koli Bant", "Vilada Ucu", "Mop Ucu",
            "Mob", "Cam Bezi", "3 Lu Set", "Siyah Eldiven", "Cam Sil",
            "Koftelik Et", "Gurler Temizlik", "Saklama Kabi", "Etiket", "Sarf Malzeme"
        ],
    }

    added_count = 0
    for idx, (group_name, products) in enumerate(groups_with_products.items(), 1):
        # Check if group exists
        grp = db.query(PurchaseProductGroup).filter(PurchaseProductGroup.name == group_name).first()
        if not grp:
            grp = PurchaseProductGroup(name=group_name, display_order=idx, is_active=True)
            db.add(grp)
            db.flush()
            print(f"  Created group: {group_name}")

        # Add products for this group
        for prod_idx, prod_name in enumerate(products, 1):
            existing_prod = db.query(PurchaseProduct).filter(
                PurchaseProduct.group_id == grp.id,
                PurchaseProduct.name == prod_name
            ).first()
            if not existing_prod:
                prod = PurchaseProduct(
                    group_id=grp.id,
                    name=prod_name,
                    default_unit="kg",
                    display_order=prod_idx,
                    is_active=True
                )
                db.add(prod)
                added_count += 1

    db.commit()
    print(f"Added {added_count} missing products")


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
        # Check if admin user exists
        existing_user = db.query(User).filter(User.email == "admin@cigkofte.com").first()

        if existing_user:
            print("Admin user exists, checking for missing data...")
            # Still run to add any missing products/categories
            add_missing_data(db)
            return

        # If no admin user, seed the database (clean slate or partial data)
        print("No admin user found, seeding database...")

        # Organization - check if exists
        org = db.query(Organization).filter(Organization.code == "CKB").first()
        if not org:
            org = Organization(
                name="Cigkofteci Bey",
                code="CKB",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(org)
            db.flush()
            print(f"Created organization: {org.name}")
        else:
            print(f"Using existing organization: {org.name}")

        # Branch - check if exists
        branch = db.query(Branch).filter(Branch.code == "KDK").first()
        if not branch:
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
        else:
            print(f"Using existing branch: {branch.name}")

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

        # Purchase Product Groups and Products - use same data as add_missing_data
        add_missing_data(db)
        print("Created purchase product groups with products")

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
