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

    response_text = message.content[0].text.strip()

    try:
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        data = json.loads(response_text)
    except json.JSONDecodeError:
        match = re.search(r'\{[^{}]+\}', response_text, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            raise ValueError(f"Could not parse OCR response: {response_text}")

    try:
        parsed_date = datetime.strptime(data.get("date", ""), "%Y-%m-%d").date()
    except:
        parsed_date = date.today()

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
        "yemeksepeti": Decimal(str(data.get("yemeksepeti", 0))),
        "migros": Decimal(str(data.get("migros", 0))),
        "total": Decimal(str(data.get("total", 0))),
        "confidence_score": Decimal(str(data.get("confidence", 0.8)))
    }
