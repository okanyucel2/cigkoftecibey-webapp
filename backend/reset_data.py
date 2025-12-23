"""Reset transactional data while keeping master data (users, branches, products, categories)"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import (
    # Transactional data (will be deleted)
    DailySummary, Purchase, PurchaseItem, Expense, DailyProduction,
    StaffMeal, OnlineSale, MonthlyPayroll, PartTimeCost, CourierExpense, DailyInsight,
    # Master data (will be kept)
    Organization, Branch, User, Supplier, ExpenseCategory,
    OnlinePlatform, PurchaseProductGroup, PurchaseProduct, Employee,
    InvitationCode, InvitationCodeUse, UserBranch
)


def reset_transactional_data(include_employees=False):
    """
    Tum transactional verileri siler, master verileri korur.

    Silinen veriler:
    - Satis kayitlari (OnlineSale)
    - Mal alimlari (Purchase, PurchaseItem)
    - Giderler (Expense)
    - Uretim kayitlari (DailyProduction)
    - Personel yemekleri (StaffMeal)
    - Bordro kayitlari (MonthlyPayroll)
    - Part-time giderleri (PartTimeCost)
    - Kurye giderleri (CourierExpense)
    - Gunluk ozetler (DailySummary)
    - AI icgoruleri (DailyInsight)

    Korunan veriler:
    - Organizasyonlar, Subeler
    - Kullanicilar
    - Tedarikciler
    - Gider kategorileri
    - Satis platformlari
    - Urun gruplari ve urunler
    - Personel kartlari (opsiyonel)
    - Davet kodlari

    Args:
        include_employees: True ise personel kartlarini da siler
    """
    # Fix DATABASE_URL for psycopg3 compatibility
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("=" * 50)
        print("VERI SIFIRLAMA SCRIPTI")
        print("=" * 50)
        print()

        # Count before deletion
        counts = {
            "OnlineSale": db.query(OnlineSale).count(),
            "Purchase": db.query(Purchase).count(),
            "PurchaseItem": db.query(PurchaseItem).count(),
            "Expense": db.query(Expense).count(),
            "DailyProduction": db.query(DailyProduction).count(),
            "StaffMeal": db.query(StaffMeal).count(),
            "MonthlyPayroll": db.query(MonthlyPayroll).count(),
            "PartTimeCost": db.query(PartTimeCost).count(),
            "CourierExpense": db.query(CourierExpense).count(),
            "DailySummary": db.query(DailySummary).count(),
            "DailyInsight": db.query(DailyInsight).count(),
        }

        if include_employees:
            counts["Employee"] = db.query(Employee).count()

        print("Silinecek kayit sayilari:")
        for table, count in counts.items():
            print(f"  {table}: {count}")
        print()

        # Delete in correct order (foreign key dependencies)
        print("Silme islemi basliyor...")

        # 1. Delete items first (FK to parent tables)
        deleted = db.query(PurchaseItem).delete()
        print(f"  PurchaseItem: {deleted} kayit silindi")

        # 2. Delete main transactional tables
        deleted = db.query(OnlineSale).delete()
        print(f"  OnlineSale: {deleted} kayit silindi")

        deleted = db.query(Purchase).delete()
        print(f"  Purchase: {deleted} kayit silindi")

        deleted = db.query(Expense).delete()
        print(f"  Expense: {deleted} kayit silindi")

        deleted = db.query(DailyProduction).delete()
        print(f"  DailyProduction: {deleted} kayit silindi")

        deleted = db.query(StaffMeal).delete()
        print(f"  StaffMeal: {deleted} kayit silindi")

        deleted = db.query(MonthlyPayroll).delete()
        print(f"  MonthlyPayroll: {deleted} kayit silindi")

        deleted = db.query(PartTimeCost).delete()
        print(f"  PartTimeCost: {deleted} kayit silindi")

        deleted = db.query(CourierExpense).delete()
        print(f"  CourierExpense: {deleted} kayit silindi")

        deleted = db.query(DailySummary).delete()
        print(f"  DailySummary: {deleted} kayit silindi")

        deleted = db.query(DailyInsight).delete()
        print(f"  DailyInsight: {deleted} kayit silindi")

        # 3. Optionally delete employees
        if include_employees:
            deleted = db.query(Employee).delete()
            print(f"  Employee: {deleted} kayit silindi")

        db.commit()

        print()
        print("=" * 50)
        print("SIFIRLAMA TAMAMLANDI!")
        print("=" * 50)
        print()
        print("Korunan veriler:")
        print(f"  Organization: {db.query(Organization).count()}")
        print(f"  Branch: {db.query(Branch).count()}")
        print(f"  User: {db.query(User).count()}")
        print(f"  Supplier: {db.query(Supplier).count()}")
        print(f"  ExpenseCategory: {db.query(ExpenseCategory).count()}")
        print(f"  OnlinePlatform: {db.query(OnlinePlatform).count()}")
        print(f"  PurchaseProductGroup: {db.query(PurchaseProductGroup).count()}")
        print(f"  PurchaseProduct: {db.query(PurchaseProduct).count()}")
        if not include_employees:
            print(f"  Employee: {db.query(Employee).count()}")

    except Exception as e:
        db.rollback()
        print(f"HATA: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    # Check for --include-employees flag
    include_employees = "--include-employees" in sys.argv

    # Confirmation prompt
    print()
    print("!!! DIKKAT !!!")
    print("Bu islem tum transactional verileri silecek:")
    print("  - Satis kayitlari")
    print("  - Mal alimlari")
    print("  - Giderler")
    print("  - Uretim kayitlari")
    print("  - Personel yemekleri")
    print("  - Bordro kayitlari")
    print("  - Kurye giderleri")
    if include_employees:
        print("  - Personel kartlari")
    print()

    response = input("Devam etmek istiyor musunuz? (evet/hayir): ")
    if response.lower() != "evet":
        print("Islem iptal edildi.")
        sys.exit(0)

    print()
    reset_transactional_data(include_employees=include_employees)
