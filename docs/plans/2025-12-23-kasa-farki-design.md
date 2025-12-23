# Kasa Farki (Cash Difference) Feature Design

## Overview

Kasa personeli gunluk olarak iki farkli kaynaktan veri raporluyor:
1. **Excel Kasa Raporu** - Manuel girilen satis ve gider verileri
2. **POS Hasilat Raporu** - POS sisteminin kaydettigi gercek satislar (gorsel)

Bu iki kaynak arasindaki fark "Kasa Farki" olarak takip edilecek.

## Veri Kaynaklari

### 1. Excel Kasa Raporu (1453.xlsx)

**Yapisi:**
- FORM sayfasi: Sabahci ve Aksamci vardiyalari yan yana (D ve N kolonlari)
- KASA RAPORU sayfasi: Iki vardiyayi birlestiren ozet

**Satirlar (Row 4-18):**
| Satir | Alan | Mapping |
|-------|------|---------|
| 4 | TARIH | Tarih |
| 5 | DEVIR | Ignore (sabit 500 TL) |
| 6 | VISA | → VISA |
| 7 | PAKET VISA | → VISA |
| 8 | NFS KOMISYON | → VISA |
| 9 | TOPLAM | Hesaplanan |
| 10 | NAKIT | → NAKIT |
| 11 | PAKET NAKIT | → NAKIT |
| 12 | TOPLAM | Hesaplanan |
| 13 | TRENDYOL | → Trendyol |
| 14 | GETIR | → Getir |
| 15 | YEMEK SEPETI | → Yemek Sepeti |
| 16 | MIGROS YEMEK | → Migros Yemek |
| 17 | VIZA NAKIT | Ignore |
| 18 | GENEL TOPLAM | Hesaplanan |
| 19+ | GIDERLER | → Isletme Giderleri (kategorisiz) |

**Vardiya Isleme:** Sabahci + Aksamci toplanarak tek gunluk kayit olusturulur.

### 2. POS Hasilat Raporu (Gorsel)

**Kaynagi:** POS sistemi ekran goruntusu (WhatsApp veya kamera ile alinir)

**Alanlar ve Mapping:**
| POS Alani | Mapping |
|-----------|---------|
| VISA | → VISA |
| PAKET VISA | → VISA |
| POS 1 | → VISA |
| POS 2 | → VISA |
| NAKIT | → NAKIT |
| PAKET NKT. | → NAKIT |
| TDY ONLINE | → Trendyol |
| GTR ONLINE | → Getir |
| MIGROS ONLINE | → Migros Yemek |
| TOPLAM | Dogrulama icin |

## Sistem Tasarimi

### Yeni Veritabani Tablolari

#### 1. CashDifference (kasa_farki)

```sql
CREATE TABLE cash_differences (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER NOT NULL REFERENCES branches(id),
    difference_date DATE NOT NULL,

    -- Kasa Raporu (Excel)
    kasa_visa DECIMAL(12,2) DEFAULT 0,
    kasa_nakit DECIMAL(12,2) DEFAULT 0,
    kasa_trendyol DECIMAL(12,2) DEFAULT 0,
    kasa_getir DECIMAL(12,2) DEFAULT 0,
    kasa_yemeksepeti DECIMAL(12,2) DEFAULT 0,
    kasa_migros DECIMAL(12,2) DEFAULT 0,
    kasa_total DECIMAL(12,2) DEFAULT 0,

    -- POS Hasilat (Gorsel)
    pos_visa DECIMAL(12,2) DEFAULT 0,
    pos_nakit DECIMAL(12,2) DEFAULT 0,
    pos_trendyol DECIMAL(12,2) DEFAULT 0,
    pos_getir DECIMAL(12,2) DEFAULT 0,
    pos_yemeksepeti DECIMAL(12,2) DEFAULT 0,
    pos_migros DECIMAL(12,2) DEFAULT 0,
    pos_total DECIMAL(12,2) DEFAULT 0,

    -- Farklar (Hesaplanan)
    diff_visa DECIMAL(12,2) GENERATED ALWAYS AS (pos_visa - kasa_visa) STORED,
    diff_nakit DECIMAL(12,2) GENERATED ALWAYS AS (pos_nakit - kasa_nakit) STORED,
    diff_trendyol DECIMAL(12,2) GENERATED ALWAYS AS (pos_trendyol - kasa_trendyol) STORED,
    diff_getir DECIMAL(12,2) GENERATED ALWAYS AS (pos_getir - kasa_getir) STORED,
    diff_yemeksepeti DECIMAL(12,2) GENERATED ALWAYS AS (pos_yemeksepeti - kasa_yemeksepeti) STORED,
    diff_migros DECIMAL(12,2) GENERATED ALWAYS AS (pos_migros - kasa_migros) STORED,
    diff_total DECIMAL(12,2) GENERATED ALWAYS AS (pos_total - kasa_total) STORED,

    -- Meta
    status VARCHAR(20) DEFAULT 'pending', -- pending, reviewed, resolved, flagged
    severity VARCHAR(20) DEFAULT 'ok',    -- ok, warning, critical
    resolution_note TEXT,
    resolved_by INTEGER REFERENCES users(id),
    resolved_at TIMESTAMP,

    -- Dosyalar
    excel_file_url TEXT,
    pos_image_url TEXT,
    ocr_confidence_score DECIMAL(5,2),

    -- Audit
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(branch_id, difference_date)
);
```

#### 2. Expense Category Guncelleme

"Kategorize Edilmemis" sistem kategorisi eklenmeli:
```sql
INSERT INTO expense_categories (name, is_fixed, is_system, display_order)
VALUES ('Kategorize Edilmemis', false, true, 0);
```

### Severity Hesaplama

```python
def calculate_severity(diff_total: Decimal) -> str:
    abs_diff = abs(diff_total)
    if abs_diff <= 50:
        return "ok"
    elif abs_diff <= 200:
        return "warning"
    else:
        return "critical"
```

*Esikler branch bazli ayarlanabilir olacak (gelecek gelistirme)*

## UI/UX Tasarimi

### 1. Birlesik Import Sayfasi

**Route:** `/kasa-farki/import` veya `/sales` sayfasina tab olarak

**Akis:**
1. Kullanici Excel ve/veya POS gorseli yukler (drag & drop)
2. Sistem parse eder:
   - Excel: openpyxl ile
   - Gorsel: Claude Vision API ile OCR
3. Onizleme gosterilir:
   - Kanal bazli karsilastirma tablosu
   - Farklar renk kodlu (yesil/kirmizi)
   - Toplam tutarlik dogrulamasi
4. Kullanici onaylar → Kayit olusturulur

**Tek Dosya Destegi:**
- Sadece Excel → Kasa verileri kaydedilir, POS bos
- Sadece Gorsel → POS verileri kaydedilir, Kasa bos
- Ikisi birden → Tam karsilastirma

### 2. Kasa Farki Yonetim Sayfasi

**Route:** `/kasa-farki`

**Ozellikler:**
- Aylik gorunum (takvim veya liste)
- Filtreleme: Durum (beklemede, cozuldu, kritik)
- Ozet kartlari: Kritik sayisi, beklemede sayisi, ay toplami
- Her satir icin: Tarih, Kasa, POS, Fark, Durum, Islem butonu

### 3. Inceleme Modal

**Icerik:**
- Excel ve POS gorsel onizleme
- Kanal bazli karsilastirma tablosu
- Cozum notu text alani
- "Cozuldu Olarak Isaretle" butonu

### 4. Bilanco Entegrasyonu

**Yeni Kart:** "Kasa Farki" bolumu
- Bugun farki
- Bu hafta toplam farki
- Bu ay toplam farki
- Mini chart (son 7 gun)
- Bekleyen kayit sayisi uyarisi

## API Endpoints

```
POST   /api/cash-difference/import     # Excel + Gorsel yukle, parse et, kaydet
GET    /api/cash-difference            # Liste (filtreli)
GET    /api/cash-difference/{id}       # Tekil kayit
PUT    /api/cash-difference/{id}       # Durum guncelle, not ekle
GET    /api/cash-difference/summary    # Ozet istatistikler
DELETE /api/cash-difference/{id}       # Kayit sil
```

## OCR Entegrasyonu

**Claude Vision API kullanimi:**

```python
import anthropic

def parse_pos_image(image_base64: str) -> dict:
    client = anthropic.Anthropic()

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
                            "media_type": "image/jpeg",
                            "data": image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": """Bu POS hasilat raporundan verileri cikart.
                        JSON formatinda don:
                        {
                            "date": "YYYY-MM-DD",
                            "visa": 0,
                            "nakit": 0,
                            "paket_visa": 0,
                            "paket_nakit": 0,
                            "pos1": 0,
                            "pos2": 0,
                            "trendyol": 0,
                            "getir": 0,
                            "migros": 0,
                            "total": 0
                        }
                        Sadece JSON don, baska bir sey yazma."""
                    }
                ],
            }
        ],
    )

    return json.loads(message.content[0].text)
```

## Gider Import Akisi

Excel'deki giderler (satir 19+):
1. Her gider satiri icin `Expense` kaydi olustur
2. `category_id` = "Kategorize Edilmemis" kategorisinin ID'si
3. `description` = Excel'deki aciklama
4. Kullanici sonradan Isletme Giderleri sayfasindan kategori atar

## Dosya Validasyonu

### Excel
- Uzanti: .xlsx, .xls
- FORM veya KASA RAPORU sayfasi olmali
- Tarih satiri (4) gecerli tarih icermeli

### Gorsel
- Uzanti: .jpg, .jpeg, .png
- Min boyut: 200x200px
- Max boyut: 10MB

## Gelecek Gelistirmeler (v2)

1. WhatsApp Bot entegrasyonu
2. Branch bazli severity esikleri
3. Haftalik ozet email raporu
4. Cashier performans analizi
5. Anomaly detection (ML)
