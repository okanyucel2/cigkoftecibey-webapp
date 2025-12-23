# Kasa Farki (Cash Difference) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a cash difference tracking system that imports data from Excel (Kasa Raporu) and POS images (Hasilat Raporu), compares them, and provides management tools.

**Architecture:**
- Backend: FastAPI with SQLAlchemy model, Alembic migration, Claude Vision for OCR
- Frontend: Vue 3 with TypeScript, new import page and management page
- Data flow: Upload files → Parse (Excel/OCR) → Preview → Confirm → Save to DB

**Tech Stack:** FastAPI, SQLAlchemy, openpyxl, Anthropic Claude Vision API, Vue 3, TypeScript, Tailwind CSS

---

## Task 1: Database Migration - CashDifference Table

**Files:**
- Create: `backend/alembic/versions/XXXXXX_add_cash_differences_table.py`

**Step 1: Create the migration file**

```bash
cd /Users/okan.yucel/cigkoftecibey-webapp/backend
source venv/bin/activate
alembic revision -m "add_cash_differences_table"
```

**Step 2: Write the migration**

```python
"""add_cash_differences_table

Revision ID: [auto-generated]
Revises: [previous]
Create Date: [auto-generated]

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '[auto-generated]'
down_revision: Union[str, None] = '[previous]'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('cash_differences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=False),
        sa.Column('difference_date', sa.Date(), nullable=False),

        # Kasa Raporu (Excel)
        sa.Column('kasa_visa', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('kasa_nakit', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('kasa_trendyol', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('kasa_getir', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('kasa_yemeksepeti', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('kasa_migros', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('kasa_total', sa.Numeric(precision=12, scale=2), server_default='0'),

        # POS Hasilat (Gorsel)
        sa.Column('pos_visa', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('pos_nakit', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('pos_trendyol', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('pos_getir', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('pos_yemeksepeti', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('pos_migros', sa.Numeric(precision=12, scale=2), server_default='0'),
        sa.Column('pos_total', sa.Numeric(precision=12, scale=2), server_default='0'),

        # Meta
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('severity', sa.String(20), server_default='ok'),
        sa.Column('resolution_note', sa.Text(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),

        # Files
        sa.Column('excel_file_url', sa.Text(), nullable=True),
        sa.Column('pos_image_url', sa.Text(), nullable=True),
        sa.Column('ocr_confidence_score', sa.Numeric(precision=5, scale=2), nullable=True),

        # Audit
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('branch_id', 'difference_date', name='uq_cash_diff_branch_date')
    )
    op.create_index('ix_cash_differences_date', 'cash_differences', ['difference_date'])
    op.create_index('ix_cash_differences_status', 'cash_differences', ['status'])


def downgrade() -> None:
    op.drop_index('ix_cash_differences_status', table_name='cash_differences')
    op.drop_index('ix_cash_differences_date', table_name='cash_differences')
    op.drop_table('cash_differences')
```

**Step 3: Run the migration**

```bash
alembic upgrade head
```

**Step 4: Commit**

```bash
git add backend/alembic/versions/*_add_cash_differences_table.py
git commit -m "feat: add cash_differences table migration"
```

---

## Task 2: Add "Kategorize Edilmemis" System Category

**Files:**
- Create: `backend/alembic/versions/XXXXXX_add_uncategorized_expense_category.py`
- Modify: `backend/app/models/__init__.py` (add is_system field to ExpenseCategory)

**Step 1: Update ExpenseCategory model**

Add `is_system` field to `ExpenseCategory` in `backend/app/models/__init__.py:151-161`:

```python
class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("branches.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100))
    is_fixed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # NEW: System categories cannot be deleted
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    expenses: Mapped[list["Expense"]] = relationship(back_populates="category")
```

**Step 2: Create migration for is_system and seed data**

```bash
alembic revision -m "add_uncategorized_expense_category"
```

```python
"""add_uncategorized_expense_category

Revision ID: [auto-generated]
Revises: [previous - cash_differences]
"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Add is_system column
    op.add_column('expense_categories',
        sa.Column('is_system', sa.Boolean(), server_default='false', nullable=False))

    # Insert "Kategorize Edilmemis" category
    op.execute("""
        INSERT INTO expense_categories (name, is_fixed, is_system, display_order)
        VALUES ('Kategorize Edilmemis', false, true, -1)
    """)


def downgrade() -> None:
    op.execute("DELETE FROM expense_categories WHERE name = 'Kategorize Edilmemis'")
    op.drop_column('expense_categories', 'is_system')
```

**Step 3: Run migration**

```bash
alembic upgrade head
```

**Step 4: Update expense delete endpoint to prevent system category deletion**

In `backend/app/api/expenses.py:47-63`, update delete function:

```python
@router.delete("/categories/{category_id}")
def delete_expense_category(category_id: int, db: DBSession, ctx: CurrentBranchContext):
    category = db.query(ExpenseCategory).filter(ExpenseCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategori bulunamadi")

    # System categories cannot be deleted
    if category.is_system:
        raise HTTPException(status_code=400, detail="Sistem kategorileri silinemez")

    expense_count = db.query(Expense).filter(Expense.category_id == category_id).count()
    if expense_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Bu kategoride {expense_count} gider kaydi var."
        )

    db.delete(category)
    db.commit()
    return {"message": "Kategori silindi"}
```

**Step 5: Commit**

```bash
git add backend/alembic/versions/*_add_uncategorized_expense_category.py backend/app/models/__init__.py backend/app/api/expenses.py
git commit -m "feat: add Kategorize Edilmemis system expense category"
```

---

## Task 3: CashDifference Model

**Files:**
- Modify: `backend/app/models/__init__.py`

**Step 1: Add CashDifference model**

Add after `CourierExpense` class (around line 447):

```python
class CashDifference(Base):
    """Kasa farki takibi - Excel vs POS karsilastirmasi"""
    __tablename__ = "cash_differences"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    difference_date: Mapped[date] = mapped_column(Date, index=True)

    # Kasa Raporu (Excel)
    kasa_visa: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    kasa_nakit: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    kasa_trendyol: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    kasa_getir: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    kasa_yemeksepeti: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    kasa_migros: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    kasa_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    # POS Hasilat (Gorsel)
    pos_visa: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    pos_nakit: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    pos_trendyol: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    pos_getir: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    pos_yemeksepeti: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    pos_migros: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    pos_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    # Meta
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, reviewed, resolved, flagged
    severity: Mapped[str] = mapped_column(String(20), default="ok")  # ok, warning, critical
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Files
    excel_file_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pos_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ocr_confidence_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)

    # Audit
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Computed properties
    @property
    def diff_visa(self) -> Decimal:
        return self.pos_visa - self.kasa_visa

    @property
    def diff_nakit(self) -> Decimal:
        return self.pos_nakit - self.kasa_nakit

    @property
    def diff_trendyol(self) -> Decimal:
        return self.pos_trendyol - self.kasa_trendyol

    @property
    def diff_getir(self) -> Decimal:
        return self.pos_getir - self.kasa_getir

    @property
    def diff_yemeksepeti(self) -> Decimal:
        return self.pos_yemeksepeti - self.kasa_yemeksepeti

    @property
    def diff_migros(self) -> Decimal:
        return self.pos_migros - self.kasa_migros

    @property
    def diff_total(self) -> Decimal:
        return self.pos_total - self.kasa_total
```

**Step 2: Commit**

```bash
git add backend/app/models/__init__.py
git commit -m "feat: add CashDifference model"
```

---

## Task 4: Pydantic Schemas for CashDifference

**Files:**
- Modify: `backend/app/schemas/__init__.py`

**Step 1: Add schemas at the end of the file**

```python
# Cash Difference (Kasa Farki)
class CashDifferenceBase(BaseModel):
    difference_date: date
    kasa_visa: Decimal = Decimal("0")
    kasa_nakit: Decimal = Decimal("0")
    kasa_trendyol: Decimal = Decimal("0")
    kasa_getir: Decimal = Decimal("0")
    kasa_yemeksepeti: Decimal = Decimal("0")
    kasa_migros: Decimal = Decimal("0")
    kasa_total: Decimal = Decimal("0")
    pos_visa: Decimal = Decimal("0")
    pos_nakit: Decimal = Decimal("0")
    pos_trendyol: Decimal = Decimal("0")
    pos_getir: Decimal = Decimal("0")
    pos_yemeksepeti: Decimal = Decimal("0")
    pos_migros: Decimal = Decimal("0")
    pos_total: Decimal = Decimal("0")


class CashDifferenceCreate(CashDifferenceBase):
    excel_file_url: Optional[str] = None
    pos_image_url: Optional[str] = None
    ocr_confidence_score: Optional[Decimal] = None


class CashDifferenceUpdate(BaseModel):
    status: Optional[str] = None
    resolution_note: Optional[str] = None


class CashDifferenceResponse(CashDifferenceBase):
    id: int
    branch_id: int
    status: str
    severity: str
    resolution_note: Optional[str] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    excel_file_url: Optional[str] = None
    pos_image_url: Optional[str] = None
    ocr_confidence_score: Optional[Decimal] = None
    created_by: int
    created_at: datetime
    # Computed diffs
    diff_visa: Decimal
    diff_nakit: Decimal
    diff_trendyol: Decimal
    diff_getir: Decimal
    diff_yemeksepeti: Decimal
    diff_migros: Decimal
    diff_total: Decimal

    class Config:
        from_attributes = True


class CashDifferenceSummary(BaseModel):
    total_records: int
    pending_count: int
    resolved_count: int
    critical_count: int
    total_diff: Decimal
    period_start: date
    period_end: date


class ExcelParseResult(BaseModel):
    """Result of parsing Excel Kasa Raporu"""
    date: date
    visa: Decimal
    nakit: Decimal
    trendyol: Decimal
    getir: Decimal
    yemeksepeti: Decimal
    migros: Decimal
    total: Decimal
    expenses: list[dict]  # [{description: str, amount: Decimal}]


class POSParseResult(BaseModel):
    """Result of parsing POS image via OCR"""
    date: date
    visa: Decimal
    nakit: Decimal
    trendyol: Decimal
    getir: Decimal
    yemeksepeti: Decimal
    migros: Decimal
    total: Decimal
    confidence_score: Decimal
```

**Step 2: Commit**

```bash
git add backend/app/schemas/__init__.py
git commit -m "feat: add CashDifference schemas"
```

---

## Task 5: Excel Parser Utility

**Files:**
- Create: `backend/app/utils/__init__.py`
- Create: `backend/app/utils/excel_parser.py`

**Step 1: Create utils package**

```bash
mkdir -p /Users/okan.yucel/cigkoftecibey-webapp/backend/app/utils
touch /Users/okan.yucel/cigkoftecibey-webapp/backend/app/utils/__init__.py
```

**Step 2: Create excel_parser.py**

```python
"""
Excel Kasa Raporu Parser

Parses the cashier's Excel report (1453.xlsx format) and extracts:
- Sales data by channel (VISA, NAKİT, online platforms)
- Expense items from the GIDERLER section
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
import openpyxl
from io import BytesIO


def parse_kasa_raporu(file_content: bytes) -> dict:
    """
    Parse Excel Kasa Raporu and return structured data.

    Expected Excel structure (FORM sheet):
    - Row 4: TARIH (Date)
    - Row 6: VISA
    - Row 7: PAKET VISA
    - Row 8: NFS KOMISYON
    - Row 10: NAKIT
    - Row 11: PAKET NAKIT
    - Row 13: TRENDYOL
    - Row 14: GETIR
    - Row 15: YEMEK SEPETI
    - Row 16: MIGROS YEMEK
    - Rows 21+: GIDERLER (expenses)

    Columns: D = Sabahci, N = Aksamci
    """
    wb = openpyxl.load_workbook(BytesIO(file_content), data_only=True)

    # Try FORM sheet first, then KASA RAPORU
    if 'FORM' in wb.sheetnames:
        sheet = wb['FORM']
        # FORM has two shifts: D (morning) and N (evening)
        return _parse_form_sheet(sheet)
    elif 'KASA RAPORU' in wb.sheetnames:
        sheet = wb['KASA RAPORU']
        return _parse_kasa_raporu_sheet(sheet)
    else:
        raise ValueError("Excel dosyasinda FORM veya KASA RAPORU sayfasi bulunamadi")


def _parse_form_sheet(sheet) -> dict:
    """Parse FORM sheet with two shifts (Sabahci + Aksamci)"""

    def get_value(row: int, col: int) -> Decimal:
        """Get cell value, handle formulas by getting cached value"""
        val = sheet.cell(row=row, column=col).value
        if val is None:
            return Decimal("0")
        if isinstance(val, str) and val.startswith('='):
            return Decimal("0")  # Formula - use data_only=True should handle this
        try:
            return Decimal(str(val))
        except:
            return Decimal("0")

    # Column indices: D=4 (Sabahci), N=14 (Aksamci)
    COL_SABAHCI = 4
    COL_AKSAMCI = 14

    # Parse date from row 4
    date_val = sheet.cell(row=4, column=COL_SABAHCI).value
    if isinstance(date_val, datetime):
        parsed_date = date_val.date()
    elif isinstance(date_val, date):
        parsed_date = date_val
    else:
        parsed_date = date.today()

    # Sum both shifts
    result = {
        "date": parsed_date,
        "visa": (
            get_value(6, COL_SABAHCI) + get_value(6, COL_AKSAMCI) +  # VISA
            get_value(7, COL_SABAHCI) + get_value(7, COL_AKSAMCI) +  # PAKET VISA
            get_value(8, COL_SABAHCI) + get_value(8, COL_AKSAMCI)    # NFS KOMISYON
        ),
        "nakit": (
            get_value(10, COL_SABAHCI) + get_value(10, COL_AKSAMCI) +  # NAKIT
            get_value(11, COL_SABAHCI) + get_value(11, COL_AKSAMCI)    # PAKET NAKIT
        ),
        "trendyol": get_value(13, COL_SABAHCI) + get_value(13, COL_AKSAMCI),
        "getir": get_value(14, COL_SABAHCI) + get_value(14, COL_AKSAMCI),
        "yemeksepeti": get_value(15, COL_SABAHCI) + get_value(15, COL_AKSAMCI),
        "migros": get_value(16, COL_SABAHCI) + get_value(16, COL_AKSAMCI),
        "expenses": []
    }

    # Calculate total
    result["total"] = (
        result["visa"] + result["nakit"] +
        result["trendyol"] + result["getir"] +
        result["yemeksepeti"] + result["migros"]
    )

    # Parse expenses (rows 21+, column A=description, H=amount for Sabahci)
    for row in range(21, sheet.max_row + 1):
        desc = sheet.cell(row=row, column=1).value  # Column A
        amount_s = get_value(row, 8)  # Column H (Sabahci)
        amount_a = get_value(row, 18)  # Column R (Aksamci) - approximate

        if desc and (amount_s > 0 or amount_a > 0):
            result["expenses"].append({
                "description": str(desc),
                "amount": amount_s + amount_a
            })

    return result


def _parse_kasa_raporu_sheet(sheet) -> dict:
    """Parse KASA RAPORU sheet (combined summary)"""

    def get_value(row: int, col: int = 4) -> Decimal:
        val = sheet.cell(row=row, column=col).value
        if val is None:
            return Decimal("0")
        try:
            return Decimal(str(val))
        except:
            return Decimal("0")

    # Parse date
    date_val = sheet.cell(row=4, column=4).value
    if isinstance(date_val, datetime):
        parsed_date = date_val.date()
    elif isinstance(date_val, date):
        parsed_date = date_val
    else:
        parsed_date = date.today()

    result = {
        "date": parsed_date,
        "visa": get_value(6) + get_value(7) + get_value(8),  # VISA + PAKET VISA + NFS
        "nakit": get_value(10) + get_value(11),  # NAKIT + PAKET NAKIT
        "trendyol": get_value(13),
        "getir": get_value(14),
        "yemeksepeti": get_value(15),
        "migros": get_value(16),
        "expenses": []
    }

    result["total"] = (
        result["visa"] + result["nakit"] +
        result["trendyol"] + result["getir"] +
        result["yemeksepeti"] + result["migros"]
    )

    # Parse expenses
    for row in range(21, sheet.max_row + 1):
        desc = sheet.cell(row=row, column=1).value
        amount = get_value(row, 8)

        if desc and amount > 0:
            result["expenses"].append({
                "description": str(desc),
                "amount": amount
            })

    return result
```

**Step 3: Commit**

```bash
git add backend/app/utils/
git commit -m "feat: add Excel Kasa Raporu parser utility"
```

---

## Task 6: POS Image OCR Parser (Claude Vision)

**Files:**
- Create: `backend/app/utils/pos_ocr.py`

**Step 1: Create pos_ocr.py**

```python
"""
POS Hasilat Raporu OCR Parser

Uses Claude Vision API to extract sales data from POS system screenshots.
"""
import anthropic
import base64
import json
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


def parse_pos_image(image_content: bytes, media_type: str = "image/jpeg") -> dict:
    """
    Parse POS Hasilat Raporu image using Claude Vision API.

    Expected POS fields:
    - VISA, NAKİT, POS 1, POS 2, PAKET VISA, PAKET NKT.
    - TDY ONLINE, GTR ONLINE, MİGROS ONLİNE
    - TOPLAM

    Returns structured data with confidence score.
    """
    client = anthropic.Anthropic()

    # Encode image to base64
    image_base64 = base64.standard_b64encode(image_content).decode("utf-8")

    prompt = """Bu POS hasılat raporundan verileri çıkart.

Aşağıdaki alanları bul ve değerlerini al:
- Tarih (format: YYYY-MM-DD)
- VISA (salon visa satışları)
- NAKİT (salon nakit satışları)
- POS 1, POS 2 (ek kart terminalleri - varsa)
- PAKET VISA (paket visa satışları)
- PAKET NKT veya PAKET NAKİT (paket nakit satışları)
- TDY ONLINE veya TRENDYOL (Trendyol satışları)
- GTR ONLINE veya GETİR (Getir satışları)
- MİGROS ONLINE veya MİGROS (Migros satışları)
- TOPLAM (genel toplam)

Tutarları nokta ve virgül olmadan sadece sayı olarak yaz.
Bulamadığın alanları 0 olarak yaz.

JSON formatında dön:
{
    "date": "YYYY-MM-DD",
    "visa": 0,
    "paket_visa": 0,
    "pos1": 0,
    "pos2": 0,
    "nakit": 0,
    "paket_nakit": 0,
    "trendyol": 0,
    "getir": 0,
    "migros": 0,
    "total": 0,
    "confidence": 0.95
}

confidence: Ne kadar emin olduğun (0.0-1.0 arası). Görüntü net değilse veya bazı değerler belirsizse düşür.

SADECE JSON dön, başka bir şey yazma."""

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ],
    )

    # Parse response
    response_text = message.content[0].text.strip()

    # Try to extract JSON from response
    try:
        # Handle potential markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        data = json.loads(response_text)
    except json.JSONDecodeError:
        # Try to find JSON object in response
        match = re.search(r'\{[^{}]+\}', response_text, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            raise ValueError(f"Could not parse OCR response: {response_text}")

    # Parse date
    try:
        parsed_date = datetime.strptime(data.get("date", ""), "%Y-%m-%d").date()
    except:
        parsed_date = date.today()

    # Aggregate values
    visa_total = (
        Decimal(str(data.get("visa", 0))) +
        Decimal(str(data.get("paket_visa", 0))) +
        Decimal(str(data.get("pos1", 0))) +
        Decimal(str(data.get("pos2", 0)))
    )

    nakit_total = (
        Decimal(str(data.get("nakit", 0))) +
        Decimal(str(data.get("paket_nakit", 0)))
    )

    return {
        "date": parsed_date,
        "visa": visa_total,
        "nakit": nakit_total,
        "trendyol": Decimal(str(data.get("trendyol", 0))),
        "getir": Decimal(str(data.get("getir", 0))),
        "yemeksepeti": Decimal(str(data.get("yemeksepeti", 0))),  # Usually not in POS
        "migros": Decimal(str(data.get("migros", 0))),
        "total": Decimal(str(data.get("total", 0))),
        "confidence_score": Decimal(str(data.get("confidence", 0.8)))
    }
```

**Step 2: Add anthropic to requirements**

Check if anthropic is in requirements.txt, add if not:

```bash
grep -q "anthropic" backend/requirements.txt || echo "anthropic>=0.18.0" >> backend/requirements.txt
```

**Step 3: Commit**

```bash
git add backend/app/utils/pos_ocr.py backend/requirements.txt
git commit -m "feat: add POS image OCR parser using Claude Vision"
```

---

## Task 7: Cash Difference API Endpoints

**Files:**
- Create: `backend/app/api/cash_difference.py`
- Modify: `backend/app/api/__init__.py`

**Step 1: Create cash_difference.py**

```python
"""
Cash Difference API - Kasa Farki Takibi

Endpoints for importing Excel/POS data and managing cash differences.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from sqlalchemy import func, and_
from app.api.deps import DBSession, CurrentBranchContext
from app.models import CashDifference, Expense, ExpenseCategory
from app.schemas import (
    CashDifferenceCreate, CashDifferenceUpdate, CashDifferenceResponse,
    CashDifferenceSummary, ExcelParseResult, POSParseResult
)
from app.utils.excel_parser import parse_kasa_raporu
from app.utils.pos_ocr import parse_pos_image

router = APIRouter(prefix="/cash-difference", tags=["cash-difference"])


def calculate_severity(diff_total: Decimal) -> str:
    """Calculate severity based on total difference"""
    abs_diff = abs(diff_total)
    if abs_diff <= 50:
        return "ok"
    elif abs_diff <= 200:
        return "warning"
    else:
        return "critical"


# ==================== PARSE ENDPOINTS ====================

@router.post("/parse-excel", response_model=ExcelParseResult)
async def parse_excel_file(
    file: UploadFile = File(...),
    ctx: CurrentBranchContext = None
):
    """Parse Excel Kasa Raporu and return extracted data for preview"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Sadece Excel dosyalari (.xlsx, .xls) kabul edilir")

    content = await file.read()

    try:
        data = parse_kasa_raporu(content)
        return ExcelParseResult(
            date=data["date"],
            visa=data["visa"],
            nakit=data["nakit"],
            trendyol=data["trendyol"],
            getir=data["getir"],
            yemeksepeti=data["yemeksepeti"],
            migros=data["migros"],
            total=data["total"],
            expenses=data["expenses"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel parse hatasi: {str(e)}")


@router.post("/parse-pos-image", response_model=POSParseResult)
async def parse_pos_image_file(
    file: UploadFile = File(...),
    ctx: CurrentBranchContext = None
):
    """Parse POS Hasilat image using OCR and return extracted data for preview"""
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Sadece JPEG ve PNG gorseller kabul edilir")

    content = await file.read()

    try:
        data = parse_pos_image(content, file.content_type)
        return POSParseResult(
            date=data["date"],
            visa=data["visa"],
            nakit=data["nakit"],
            trendyol=data["trendyol"],
            getir=data["getir"],
            yemeksepeti=data["yemeksepeti"],
            migros=data["migros"],
            total=data["total"],
            confidence_score=data["confidence_score"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OCR hatasi: {str(e)}")


# ==================== CRUD ENDPOINTS ====================

@router.post("/import", response_model=CashDifferenceResponse)
def import_cash_difference(
    data: CashDifferenceCreate,
    db: DBSession,
    ctx: CurrentBranchContext,
    import_expenses: bool = Query(default=True, description="Import expenses to Kategorize Edilmemis"),
    expenses: list[dict] = []
):
    """
    Import parsed data and create CashDifference record.
    Also imports expenses to 'Kategorize Edilmemis' category if provided.
    """
    # Check if record already exists for this date
    existing = db.query(CashDifference).filter(
        CashDifference.branch_id == ctx.current_branch_id,
        CashDifference.difference_date == data.difference_date
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"{data.difference_date} tarihi icin zaten kayit var. Guncellemek icin mevcut kaydi silin."
        )

    # Calculate severity
    diff_total = data.pos_total - data.kasa_total
    severity = calculate_severity(diff_total)

    # Create record
    record = CashDifference(
        branch_id=ctx.current_branch_id,
        difference_date=data.difference_date,
        kasa_visa=data.kasa_visa,
        kasa_nakit=data.kasa_nakit,
        kasa_trendyol=data.kasa_trendyol,
        kasa_getir=data.kasa_getir,
        kasa_yemeksepeti=data.kasa_yemeksepeti,
        kasa_migros=data.kasa_migros,
        kasa_total=data.kasa_total,
        pos_visa=data.pos_visa,
        pos_nakit=data.pos_nakit,
        pos_trendyol=data.pos_trendyol,
        pos_getir=data.pos_getir,
        pos_yemeksepeti=data.pos_yemeksepeti,
        pos_migros=data.pos_migros,
        pos_total=data.pos_total,
        status="pending",
        severity=severity,
        excel_file_url=data.excel_file_url,
        pos_image_url=data.pos_image_url,
        ocr_confidence_score=data.ocr_confidence_score,
        created_by=ctx.user.id
    )

    db.add(record)

    # Import expenses if provided
    if import_expenses and expenses:
        # Get "Kategorize Edilmemis" category
        uncategorized = db.query(ExpenseCategory).filter(
            ExpenseCategory.name == "Kategorize Edilmemis"
        ).first()

        if uncategorized:
            for exp in expenses:
                if exp.get("amount", 0) > 0:
                    expense = Expense(
                        branch_id=ctx.current_branch_id,
                        category_id=uncategorized.id,
                        expense_date=data.difference_date,
                        description=exp.get("description", "Excel'den aktarildi"),
                        amount=Decimal(str(exp["amount"])),
                        created_by=ctx.user.id
                    )
                    db.add(expense)

    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[CashDifferenceResponse])
def get_cash_differences(
    db: DBSession,
    ctx: CurrentBranchContext,
    start_date: date | None = None,
    end_date: date | None = None,
    status: str | None = None,
    month: int | None = None,
    year: int | None = None,
    limit: int = Query(default=50, le=200)
):
    """Get cash difference records with filters"""
    query = db.query(CashDifference).filter(
        CashDifference.branch_id == ctx.current_branch_id
    )

    if start_date:
        query = query.filter(CashDifference.difference_date >= start_date)
    if end_date:
        query = query.filter(CashDifference.difference_date <= end_date)
    if status:
        query = query.filter(CashDifference.status == status)
    if month and year:
        from calendar import monthrange
        start = date(year, month, 1)
        end = date(year, month, monthrange(year, month)[1])
        query = query.filter(
            CashDifference.difference_date >= start,
            CashDifference.difference_date <= end
        )

    return query.order_by(CashDifference.difference_date.desc()).limit(limit).all()


@router.get("/summary", response_model=CashDifferenceSummary)
def get_cash_difference_summary(
    db: DBSession,
    ctx: CurrentBranchContext,
    month: int | None = None,
    year: int | None = None
):
    """Get summary statistics for cash differences"""
    from calendar import monthrange

    if not month or not year:
        today = date.today()
        month = month or today.month
        year = year or today.year

    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])

    records = db.query(CashDifference).filter(
        CashDifference.branch_id == ctx.current_branch_id,
        CashDifference.difference_date >= start,
        CashDifference.difference_date <= end
    ).all()

    total_diff = sum(r.diff_total for r in records)

    return CashDifferenceSummary(
        total_records=len(records),
        pending_count=sum(1 for r in records if r.status == "pending"),
        resolved_count=sum(1 for r in records if r.status == "resolved"),
        critical_count=sum(1 for r in records if r.severity == "critical"),
        total_diff=total_diff,
        period_start=start,
        period_end=end
    )


@router.get("/{record_id}", response_model=CashDifferenceResponse)
def get_cash_difference(
    record_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Get single cash difference record"""
    record = db.query(CashDifference).filter(
        CashDifference.id == record_id,
        CashDifference.branch_id == ctx.current_branch_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")

    return record


@router.put("/{record_id}", response_model=CashDifferenceResponse)
def update_cash_difference(
    record_id: int,
    data: CashDifferenceUpdate,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Update cash difference status and resolution note"""
    record = db.query(CashDifference).filter(
        CashDifference.id == record_id,
        CashDifference.branch_id == ctx.current_branch_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")

    if data.status:
        record.status = data.status
        if data.status == "resolved":
            record.resolved_by = ctx.user.id
            record.resolved_at = datetime.utcnow()

    if data.resolution_note is not None:
        record.resolution_note = data.resolution_note

    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}")
def delete_cash_difference(
    record_id: int,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Delete cash difference record"""
    record = db.query(CashDifference).filter(
        CashDifference.id == record_id,
        CashDifference.branch_id == ctx.current_branch_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Kayit bulunamadi")

    db.delete(record)
    db.commit()
    return {"message": "Kayit silindi"}
```

**Step 2: Register router in __init__.py**

Add to `backend/app/api/__init__.py`:

```python
from app.api.cash_difference import router as cash_difference_router
# ... in the router list ...
app.include_router(cash_difference_router)
```

**Step 3: Commit**

```bash
git add backend/app/api/cash_difference.py backend/app/api/__init__.py
git commit -m "feat: add Cash Difference API endpoints"
```

---

## Task 8: Frontend TypeScript Types

**Files:**
- Modify: `frontend/src/types/index.ts`

**Step 1: Add CashDifference types at end of file**

```typescript
// Cash Difference (Kasa Farki) Types
export interface CashDifference {
  id: number
  branch_id: number
  difference_date: string
  // Kasa Raporu
  kasa_visa: number
  kasa_nakit: number
  kasa_trendyol: number
  kasa_getir: number
  kasa_yemeksepeti: number
  kasa_migros: number
  kasa_total: number
  // POS Hasilat
  pos_visa: number
  pos_nakit: number
  pos_trendyol: number
  pos_getir: number
  pos_yemeksepeti: number
  pos_migros: number
  pos_total: number
  // Diffs
  diff_visa: number
  diff_nakit: number
  diff_trendyol: number
  diff_getir: number
  diff_yemeksepeti: number
  diff_migros: number
  diff_total: number
  // Meta
  status: 'pending' | 'reviewed' | 'resolved' | 'flagged'
  severity: 'ok' | 'warning' | 'critical'
  resolution_note?: string
  resolved_by?: number
  resolved_at?: string
  // Files
  excel_file_url?: string
  pos_image_url?: string
  ocr_confidence_score?: number
  // Audit
  created_by: number
  created_at: string
}

export interface CashDifferenceSummary {
  total_records: number
  pending_count: number
  resolved_count: number
  critical_count: number
  total_diff: number
  period_start: string
  period_end: string
}

export interface ExcelParseResult {
  date: string
  visa: number
  nakit: number
  trendyol: number
  getir: number
  yemeksepeti: number
  migros: number
  total: number
  expenses: Array<{ description: string; amount: number }>
}

export interface POSParseResult {
  date: string
  visa: number
  nakit: number
  trendyol: number
  getir: number
  yemeksepeti: number
  migros: number
  total: number
  confidence_score: number
}
```

**Step 2: Commit**

```bash
git add frontend/src/types/index.ts
git commit -m "feat: add CashDifference TypeScript types"
```

---

## Task 9: Frontend API Service

**Files:**
- Modify: `frontend/src/services/api.ts`

**Step 1: Add imports and API service**

Add to imports at top:

```typescript
import type {
  // ... existing imports ...
  CashDifference, CashDifferenceSummary, ExcelParseResult, POSParseResult
} from '@/types'
```

Add at end before `export default api`:

```typescript
// Cash Difference (Kasa Farki)
export const cashDifferenceApi = {
  // Parse files
  parseExcel: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<ExcelParseResult>('/cash-difference/parse-excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  parsePOSImage: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<POSParseResult>('/cash-difference/parse-pos-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // CRUD
  import: (data: {
    difference_date: string
    kasa_visa: number
    kasa_nakit: number
    kasa_trendyol: number
    kasa_getir: number
    kasa_yemeksepeti: number
    kasa_migros: number
    kasa_total: number
    pos_visa: number
    pos_nakit: number
    pos_trendyol: number
    pos_getir: number
    pos_yemeksepeti: number
    pos_migros: number
    pos_total: number
    excel_file_url?: string
    pos_image_url?: string
    ocr_confidence_score?: number
  }, expenses?: Array<{ description: string; amount: number }>) =>
    api.post<CashDifference>('/cash-difference/import', data, {
      params: { import_expenses: true },
      data: { ...data, expenses }
    }),

  getAll: (params?: {
    start_date?: string
    end_date?: string
    status?: string
    month?: number
    year?: number
  }) => api.get<CashDifference[]>('/cash-difference', { params }),

  getById: (id: number) => api.get<CashDifference>(`/cash-difference/${id}`),

  getSummary: (params?: { month?: number; year?: number }) =>
    api.get<CashDifferenceSummary>('/cash-difference/summary', { params }),

  update: (id: number, data: { status?: string; resolution_note?: string }) =>
    api.put<CashDifference>(`/cash-difference/${id}`, data),

  delete: (id: number) => api.delete(`/cash-difference/${id}`)
}
```

**Step 2: Commit**

```bash
git add frontend/src/services/api.ts
git commit -m "feat: add CashDifference API service"
```

---

## Task 10: Frontend - Import Page Component

**Files:**
- Create: `frontend/src/views/CashDifferenceImport.vue`

**Step 1: Create the import page**

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ExcelParseResult, POSParseResult } from '@/types'
import { cashDifferenceApi } from '@/services/api'
import { useFormatters } from '@/composables'
import { ErrorAlert, LoadingState } from '@/components/ui'

const { formatCurrency } = useFormatters()

// State
const loading = ref(false)
const error = ref('')
const success = ref(false)

// File inputs
const excelFile = ref<File | null>(null)
const posFile = ref<File | null>(null)

// Parsed data
const excelData = ref<ExcelParseResult | null>(null)
const posData = ref<POSParseResult | null>(null)

// Computed
const hasData = computed(() => excelData.value || posData.value)
const selectedDate = computed(() => excelData.value?.date || posData.value?.date || '')

const comparisonRows = computed(() => {
  if (!hasData.value) return []

  const kasa = excelData.value
  const pos = posData.value

  return [
    { label: 'VISA', kasa: kasa?.visa || 0, pos: pos?.visa || 0 },
    { label: 'NAKİT', kasa: kasa?.nakit || 0, pos: pos?.nakit || 0 },
    { label: 'Trendyol', kasa: kasa?.trendyol || 0, pos: pos?.trendyol || 0 },
    { label: 'Getir', kasa: kasa?.getir || 0, pos: pos?.getir || 0 },
    { label: 'Yemek Sepeti', kasa: kasa?.yemeksepeti || 0, pos: pos?.yemeksepeti || 0 },
    { label: 'Migros', kasa: kasa?.migros || 0, pos: pos?.migros || 0 },
  ]
})

const totals = computed(() => ({
  kasa: excelData.value?.total || 0,
  pos: posData.value?.total || 0,
  diff: (posData.value?.total || 0) - (excelData.value?.total || 0)
}))

// Methods
async function handleExcelUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return

  excelFile.value = input.files[0]
  loading.value = true
  error.value = ''

  try {
    const response = await cashDifferenceApi.parseExcel(excelFile.value)
    excelData.value = response.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Excel parse hatasi'
    excelFile.value = null
  } finally {
    loading.value = false
  }
}

async function handlePOSUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return

  posFile.value = input.files[0]
  loading.value = true
  error.value = ''

  try {
    const response = await cashDifferenceApi.parsePOSImage(posFile.value)
    posData.value = response.data
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'OCR hatasi'
    posFile.value = null
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!hasData.value) return

  loading.value = true
  error.value = ''

  try {
    const kasa = excelData.value
    const pos = posData.value

    await cashDifferenceApi.import({
      difference_date: selectedDate.value,
      kasa_visa: kasa?.visa || 0,
      kasa_nakit: kasa?.nakit || 0,
      kasa_trendyol: kasa?.trendyol || 0,
      kasa_getir: kasa?.getir || 0,
      kasa_yemeksepeti: kasa?.yemeksepeti || 0,
      kasa_migros: kasa?.migros || 0,
      kasa_total: kasa?.total || 0,
      pos_visa: pos?.visa || 0,
      pos_nakit: pos?.nakit || 0,
      pos_trendyol: pos?.trendyol || 0,
      pos_getir: pos?.getir || 0,
      pos_yemeksepeti: pos?.yemeksepeti || 0,
      pos_migros: pos?.migros || 0,
      pos_total: pos?.total || 0,
      ocr_confidence_score: pos?.confidence_score
    }, kasa?.expenses || [])

    success.value = true
    // Reset form
    excelFile.value = null
    posFile.value = null
    excelData.value = null
    posData.value = null
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Kayit hatasi'
  } finally {
    loading.value = false
  }
}

function getDiffClass(diff: number) {
  if (diff > 0) return 'text-green-600'
  if (diff < 0) return 'text-red-600'
  return 'text-gray-500'
}

function getDiffIcon(diff: number) {
  if (diff > 0) return '🟢'
  if (diff < 0) return '🔴'
  return '⚪'
}
</script>

<template>
  <div class="p-6 max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">Gunluk Veri Import</h1>

    <ErrorAlert v-if="error" :message="error" class="mb-4" />

    <div v-if="success" class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
      <p class="text-green-800">✅ Veriler basariyla kaydedildi!</p>
    </div>

    <!-- Upload Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <!-- Excel Upload -->
      <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
        <div class="text-4xl mb-2">📊</div>
        <h3 class="font-semibold mb-2">Kasa Raporu (Excel)</h3>
        <input
          type="file"
          accept=".xlsx,.xls"
          @change="handleExcelUpload"
          class="hidden"
          id="excel-input"
        />
        <label
          for="excel-input"
          class="cursor-pointer inline-block px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          {{ excelFile ? excelFile.name : 'Dosya Sec' }}
        </label>
        <p v-if="excelData" class="mt-2 text-sm text-green-600">
          ✓ {{ excelData.date }} tarihi okundu
        </p>
      </div>

      <!-- POS Image Upload -->
      <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-purple-400 transition-colors">
        <div class="text-4xl mb-2">📸</div>
        <h3 class="font-semibold mb-2">POS Hasilat (Gorsel)</h3>
        <input
          type="file"
          accept="image/jpeg,image/png"
          @change="handlePOSUpload"
          class="hidden"
          id="pos-input"
        />
        <label
          for="pos-input"
          class="cursor-pointer inline-block px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
        >
          {{ posFile ? posFile.name : 'Gorsel Sec' }}
        </label>
        <p v-if="posData" class="mt-2 text-sm text-green-600">
          ✓ Guven: {{ (posData.confidence_score * 100).toFixed(0) }}%
        </p>
      </div>
    </div>

    <LoadingState v-if="loading" message="Isleniyor..." />

    <!-- Comparison Table -->
    <div v-if="hasData && !loading" class="bg-white rounded-lg shadow overflow-hidden">
      <div class="px-6 py-4 bg-gray-50 border-b">
        <h3 class="font-semibold">Karsilastirma - {{ selectedDate }}</h3>
      </div>

      <table class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-sm font-medium text-gray-500">Kanal</th>
            <th class="px-6 py-3 text-right text-sm font-medium text-gray-500">Kasa</th>
            <th class="px-6 py-3 text-right text-sm font-medium text-gray-500">POS</th>
            <th class="px-6 py-3 text-right text-sm font-medium text-gray-500">Fark</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="row in comparisonRows" :key="row.label">
            <td class="px-6 py-4 text-sm font-medium">{{ row.label }}</td>
            <td class="px-6 py-4 text-sm text-right">{{ formatCurrency(row.kasa) }}</td>
            <td class="px-6 py-4 text-sm text-right">{{ formatCurrency(row.pos) }}</td>
            <td class="px-6 py-4 text-sm text-right" :class="getDiffClass(row.pos - row.kasa)">
              {{ getDiffIcon(row.pos - row.kasa) }} {{ formatCurrency(row.pos - row.kasa) }}
            </td>
          </tr>
          <tr class="bg-gray-50 font-bold">
            <td class="px-6 py-4">TOPLAM</td>
            <td class="px-6 py-4 text-right">{{ formatCurrency(totals.kasa) }}</td>
            <td class="px-6 py-4 text-right">{{ formatCurrency(totals.pos) }}</td>
            <td class="px-6 py-4 text-right" :class="getDiffClass(totals.diff)">
              {{ getDiffIcon(totals.diff) }} {{ formatCurrency(totals.diff) }}
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Expenses Preview -->
      <div v-if="excelData?.expenses?.length" class="px-6 py-4 border-t">
        <h4 class="font-medium mb-2">Giderler ({{ excelData.expenses.length }} kalem)</h4>
        <div class="text-sm text-gray-600 space-y-1">
          <div v-for="(exp, i) in excelData.expenses.slice(0, 5)" :key="i">
            {{ exp.description }}: {{ formatCurrency(exp.amount) }}
          </div>
          <div v-if="excelData.expenses.length > 5" class="text-gray-400">
            +{{ excelData.expenses.length - 5 }} daha...
          </div>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="px-6 py-4 bg-gray-50 border-t">
        <button
          @click="handleSubmit"
          :disabled="loading"
          class="w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
        >
          💾 Onayla ve Kaydet
        </button>
      </div>
    </div>
  </div>
</template>
```

**Step 2: Commit**

```bash
git add frontend/src/views/CashDifferenceImport.vue
git commit -m "feat: add CashDifferenceImport page component"
```

---

## Task 11: Frontend - Management Page Component

**Files:**
- Create: `frontend/src/views/CashDifference.vue`

**Step 1: Create the management page (see separate file for full implementation)**

This is a larger component. Key features:
- Monthly filter
- Summary cards (critical, pending, resolved, total diff)
- List of records with status badges
- Click to open review modal
- Status update functionality

**Step 2: Commit**

```bash
git add frontend/src/views/CashDifference.vue
git commit -m "feat: add CashDifference management page"
```

---

## Task 12: Frontend Router Updates

**Files:**
- Modify: `frontend/src/router/index.ts`

**Step 1: Add routes**

```typescript
// Add imports
// In routes array, add:
{
  path: '/kasa-farki',
  name: 'CashDifference',
  component: () => import('@/views/CashDifference.vue'),
  meta: { requiresAuth: true }
},
{
  path: '/kasa-farki/import',
  name: 'CashDifferenceImport',
  component: () => import('@/views/CashDifferenceImport.vue'),
  meta: { requiresAuth: true }
},
```

**Step 2: Commit**

```bash
git add frontend/src/router/index.ts
git commit -m "feat: add CashDifference routes"
```

---

## Task 13: Navigation Menu Update

**Files:**
- Modify: `frontend/src/views/Layout.vue`

**Step 1: Add menu item**

Find the navigation section and add:

```vue
<router-link
  to="/kasa-farki"
  class="..."
>
  <span class="...">💰</span>
  <span>Kasa Farki</span>
</router-link>
```

**Step 2: Commit**

```bash
git add frontend/src/views/Layout.vue
git commit -m "feat: add Kasa Farki to navigation menu"
```

---

## Task 14: Bilanco Integration

**Files:**
- Modify: `backend/app/api/reports.py` (add kasa_farki to bilanco response)
- Modify: `backend/app/schemas/__init__.py` (update BilancoStats)
- Modify: `frontend/src/types/index.ts` (update BilancoStats type)
- Modify: `frontend/src/views/Bilanco.vue` (add Kasa Farki card)

**Step 1: Update backend to include kasa farki summary in bilanco**

**Step 2: Update frontend BilancoStats type**

**Step 3: Add Kasa Farki card to Bilanco.vue**

**Step 4: Commit**

```bash
git add backend/app/api/reports.py backend/app/schemas/__init__.py frontend/src/types/index.ts frontend/src/views/Bilanco.vue
git commit -m "feat: integrate Kasa Farki into Bilanco dashboard"
```

---

## Final Verification

**Run all checks:**

```bash
# Backend
cd /Users/okan.yucel/cigkoftecibey-webapp/backend
source venv/bin/activate
alembic upgrade head
python -c "from app.models import CashDifference; print('Model OK')"
python -c "from app.utils.excel_parser import parse_kasa_raporu; print('Excel parser OK')"

# Frontend
cd /Users/okan.yucel/cigkoftecibey-webapp/frontend
npm run build

# Test manually
# 1. Start backend: uvicorn app.main:app --reload
# 2. Start frontend: npm run dev
# 3. Navigate to /kasa-farki/import
# 4. Upload test Excel and POS image
# 5. Verify comparison table shows correctly
# 6. Submit and verify record appears in /kasa-farki
```

---

## Summary

| Task | Component | Files |
|------|-----------|-------|
| 1 | DB Migration | alembic/versions/..._add_cash_differences_table.py |
| 2 | System Category | alembic/versions/..._add_uncategorized_expense_category.py |
| 3 | Model | backend/app/models/__init__.py |
| 4 | Schemas | backend/app/schemas/__init__.py |
| 5 | Excel Parser | backend/app/utils/excel_parser.py |
| 6 | OCR Parser | backend/app/utils/pos_ocr.py |
| 7 | API Endpoints | backend/app/api/cash_difference.py |
| 8 | Types | frontend/src/types/index.ts |
| 9 | API Service | frontend/src/services/api.ts |
| 10 | Import Page | frontend/src/views/CashDifferenceImport.vue |
| 11 | Management Page | frontend/src/views/CashDifference.vue |
| 12 | Router | frontend/src/router/index.ts |
| 13 | Navigation | frontend/src/views/Layout.vue |
| 14 | Bilanco | Multiple files |
