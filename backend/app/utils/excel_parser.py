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
            return Decimal("0")
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
            get_value(6, COL_SABAHCI) + get_value(6, COL_AKSAMCI) +
            get_value(7, COL_SABAHCI) + get_value(7, COL_AKSAMCI) +
            get_value(8, COL_SABAHCI) + get_value(8, COL_AKSAMCI)
        ),
        "nakit": (
            get_value(10, COL_SABAHCI) + get_value(10, COL_AKSAMCI) +
            get_value(11, COL_SABAHCI) + get_value(11, COL_AKSAMCI)
        ),
        "trendyol": get_value(13, COL_SABAHCI) + get_value(13, COL_AKSAMCI),
        "getir": get_value(14, COL_SABAHCI) + get_value(14, COL_AKSAMCI),
        "yemeksepeti": get_value(15, COL_SABAHCI) + get_value(15, COL_AKSAMCI),
        "migros": get_value(16, COL_SABAHCI) + get_value(16, COL_AKSAMCI),
        "expenses": []
    }

    result["total"] = (
        result["visa"] + result["nakit"] +
        result["trendyol"] + result["getir"] +
        result["yemeksepeti"] + result["migros"]
    )

    # Parse expenses (rows 21+)
    for row in range(21, sheet.max_row + 1):
        desc = sheet.cell(row=row, column=1).value
        amount_s = get_value(row, 8)
        amount_a = get_value(row, 18)

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

    date_val = sheet.cell(row=4, column=4).value
    if isinstance(date_val, datetime):
        parsed_date = date_val.date()
    elif isinstance(date_val, date):
        parsed_date = date_val
    else:
        parsed_date = date.today()

    result = {
        "date": parsed_date,
        "visa": get_value(6) + get_value(7) + get_value(8),
        "nakit": get_value(10) + get_value(11),
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

    for row in range(21, sheet.max_row + 1):
        desc = sheet.cell(row=row, column=1).value
        amount = get_value(row, 8)

        if desc and amount > 0:
            result["expenses"].append({
                "description": str(desc),
                "amount": amount
            })

    return result
