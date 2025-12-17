"""Seed purchase product groups and products"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import PurchaseProductGroup, PurchaseProduct

PRODUCT_GROUPS = [
    {
        "name": "MANAV GRUBU",
        "display_order": 1,
        "products": [
            {"name": "MARUL", "default_unit": "kg"},
            {"name": "NANE", "default_unit": "kg"},
            {"name": "MAYDANOZ", "default_unit": "kg"},
            {"name": "ROKA", "default_unit": "kg"},
            {"name": "TERE", "default_unit": "kg"},
            {"name": "KIVIRCIK", "default_unit": "kg"},
            {"name": "AYSBERG", "default_unit": "kg"},
            {"name": "MOR LAHANA", "default_unit": "kg"},
            {"name": "HAVUC", "default_unit": "kg"},
            {"name": "TURP", "default_unit": "kg"},
            {"name": "LIMON", "default_unit": "kg"},
            {"name": "REYHAN", "default_unit": "kg"},
            {"name": "KARPUZ", "default_unit": "kg"},
            {"name": "PATATES", "default_unit": "kg"},
            {"name": "SALATALIK", "default_unit": "kg"},
            {"name": "YESIL SOGAN", "default_unit": "kg"},
            {"name": "SOYULMUS SOGAN", "default_unit": "kg"},
            {"name": "SARIMSAK", "default_unit": "kg"},
        ]
    },
    {
        "name": "LAVAS GRUBU",
        "display_order": 2,
        "products": [
            {"name": "LAVAS", "default_unit": "adet"},
        ]
    },
    {
        "name": "KURU GIDA",
        "display_order": 3,
        "products": [
            {"name": "ESMER BULGUR", "default_unit": "kg"},
            {"name": "YEMEKLIK BULGUR", "default_unit": "kg"},
            {"name": "PIRINC", "default_unit": "kg"},
            {"name": "NOHUT", "default_unit": "kg"},
            {"name": "MERCIMEK", "default_unit": "kg"},
            {"name": "MAKARNA", "default_unit": "kg"},
            {"name": "KURU FASULYE", "default_unit": "kg"},
            {"name": "MOR ISOT", "default_unit": "kg"},
            {"name": "SIYAH ISOT", "default_unit": "kg"},
            {"name": "CAVUSOGLU", "default_unit": "kg"},
            {"name": "SOS ISOT", "default_unit": "kg"},
            {"name": "SOS BAHARATI", "default_unit": "kg"},
            {"name": "BAHARAT", "default_unit": "kg"},
            {"name": "TUZ MIX", "default_unit": "kg"},
            {"name": "TAT SALCA", "default_unit": "kg"},
            {"name": "BIBER SALCA", "default_unit": "kg"},
            {"name": "TUZ", "default_unit": "kg"},
            {"name": "SEKER", "default_unit": "kg"},
            {"name": "NAR EKSISI", "default_unit": "lt"},
            {"name": "ZEYTIN YAG", "default_unit": "lt"},
            {"name": "AYCICEK YAG", "default_unit": "lt"},
            {"name": "CIPS", "default_unit": "adet"},
            {"name": "KARANFIL", "default_unit": "kg"},
            {"name": "CAY", "default_unit": "kg"},
            {"name": "KETCAP", "default_unit": "adet"},
        ]
    },
    {
        "name": "TURSU GRUBU",
        "display_order": 4,
        "products": [
            {"name": "BIBER TURSUSU", "default_unit": "kg"},
            {"name": "KARISIK TURSU", "default_unit": "kg"},
        ]
    },
    {
        "name": "ICECEK GRUBU",
        "display_order": 5,
        "products": [
            {"name": "SALGAM", "default_unit": "adet"},
            {"name": "SODA", "default_unit": "adet"},
            {"name": "SU 330", "default_unit": "adet"},
            {"name": "DAMACANA SU", "default_unit": "adet"},
            {"name": "EKER AYRAN", "default_unit": "adet"},
            {"name": "GAZOZ", "default_unit": "adet"},
            {"name": "YOGURT", "default_unit": "kg"},
            {"name": "MARKASIZ SU", "default_unit": "adet"},
        ]
    },
    {
        "name": "AMBALAJ GRUBU",
        "display_order": 6,
        "products": [
            {"name": "DURUM KAGIT", "default_unit": "adet"},
            {"name": "DURUM POSET", "default_unit": "adet"},
            {"name": "PLASTIK CATAL", "default_unit": "adet"},
            {"name": "PLASTIK BARDAK", "default_unit": "adet"},
            {"name": "PLASTIK BICAK", "default_unit": "adet"},
            {"name": "STREC BUYUK", "default_unit": "adet"},
            {"name": "STREC KUCUK", "default_unit": "adet"},
            {"name": "TERMAL RULO", "default_unit": "adet"},
            {"name": "POS RULO", "default_unit": "adet"},
            {"name": "KURDAN", "default_unit": "adet"},
            {"name": "KOLONYA", "default_unit": "adet"},
            {"name": "SEFFAF ELDIVEN", "default_unit": "kutu"},
            {"name": "PUDRALI ELDIVEN", "default_unit": "kutu"},
            {"name": "ISLAK MENDIL", "default_unit": "adet"},
            {"name": "BASKILI POSET", "default_unit": "adet"},
            {"name": "PIPET", "default_unit": "adet"},
            {"name": "COP POSETI", "default_unit": "adet"},
            {"name": "CATAL KILIFI", "default_unit": "adet"},
            {"name": "COP SITIK", "default_unit": "adet"},
            {"name": "MASA PECETESI", "default_unit": "adet"},
            {"name": "KAGIT HAVLU", "default_unit": "adet"},
            {"name": "TUVALET KAGIT", "default_unit": "adet"},
            {"name": "Z PECETE", "default_unit": "adet"},
            {"name": "250 GR VAKUM TORBASI", "default_unit": "adet"},
            {"name": "5 KG VAKUM TORBASI", "default_unit": "adet"},
            {"name": "TERAZI ETIKETI", "default_unit": "adet"},
        ]
    },
    {
        "name": "SIZDIRMAZLAR GRUBU",
        "display_order": 7,
        "products": [
            {"name": "250 GR SUSI", "default_unit": "adet"},
            {"name": "250 GR YESILLIK", "default_unit": "adet"},
            {"name": "500 GR KOFTE", "default_unit": "adet"},
            {"name": "500 GR YESILLIK", "default_unit": "adet"},
            {"name": "1 KG YESIL KAP", "default_unit": "adet"},
            {"name": "TURSU KABI", "default_unit": "adet"},
            {"name": "330 PET SISE", "default_unit": "adet"},
            {"name": "50 GR SOS", "default_unit": "adet"},
        ]
    },
    {
        "name": "TEMIZLIK GRUBU",
        "display_order": 8,
        "products": [
            {"name": "DOMESTOS", "default_unit": "adet"},
            {"name": "YUZEY TEMIZLEYICI", "default_unit": "adet"},
            {"name": "CIF", "default_unit": "adet"},
            {"name": "SARI GUC", "default_unit": "adet"},
            {"name": "KOPUK SABUN", "default_unit": "adet"},
            {"name": "SIVI BULASIK ELDE", "default_unit": "adet"},
            {"name": "SIVI BULASIK MAKINA", "default_unit": "adet"},
            {"name": "GENEL TEMIZLIK", "default_unit": "adet"},
            {"name": "KIREC COZ", "default_unit": "adet"},
        ]
    },
    {
        "name": "TASINMAZLAR GRUBU",
        "display_order": 9,
        "products": [
            {"name": "BUYUK BOY TEPSI", "default_unit": "adet"},
            {"name": "KUCUK BOY TEPSI", "default_unit": "adet"},
            {"name": "SOSLUK", "default_unit": "adet"},
            {"name": "KAYIK TABAK GENIS", "default_unit": "adet"},
            {"name": "KAYIK TABAK DAR", "default_unit": "adet"},
            {"name": "SU BARDAGI", "default_unit": "adet"},
            {"name": "METAL CATAL", "default_unit": "adet"},
            {"name": "METAL BICAK", "default_unit": "adet"},
            {"name": "SOS BIDONU", "default_unit": "adet"},
            {"name": "PLASTIK KUVET", "default_unit": "adet"},
            {"name": "KOLI BANT", "default_unit": "adet"},
            {"name": "VILADA UCU", "default_unit": "adet"},
            {"name": "MOP UCU", "default_unit": "adet"},
            {"name": "MOB", "default_unit": "adet"},
            {"name": "CAM BEZI", "default_unit": "adet"},
            {"name": "3 LU SET", "default_unit": "adet"},
            {"name": "SIYAH ELDIVEN", "default_unit": "kutu"},
            {"name": "CAM SIL", "default_unit": "adet"},
            {"name": "KOFTELI ET", "default_unit": "kg"},
            {"name": "GURLER TEMIZLIK", "default_unit": "adet"},
            {"name": "SAKLAMA KABI", "default_unit": "adet"},
            {"name": "ETIKET", "default_unit": "adet"},
            {"name": "SARF MALZEME", "default_unit": "adet"},
        ]
    },
]


def seed_purchase_products():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.query(PurchaseProductGroup).first()
        if existing:
            print("Purchase products already seeded. Skipping...")
            return

        total_products = 0
        for group_data in PRODUCT_GROUPS:
            products = group_data.pop("products")
            group = PurchaseProductGroup(**group_data, is_active=True)
            db.add(group)
            db.flush()

            for i, prod_data in enumerate(products):
                prod = PurchaseProduct(
                    group_id=group.id,
                    name=prod_data["name"],
                    default_unit=prod_data["default_unit"],
                    display_order=i + 1,
                    is_active=True
                )
                db.add(prod)
                total_products += 1

            print(f"Created group: {group.name} ({len(products)} products)")

        db.commit()
        print(f"\nSeed completed! Created {len(PRODUCT_GROUPS)} groups, {total_products} products.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_purchase_products()
