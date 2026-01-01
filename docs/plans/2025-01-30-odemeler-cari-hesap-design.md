# Ödemeler - Tedarikçi Cari Hesap Sistemi Tasarımı

> **Tarih:** 2025-01-30
> **Durum:** Tasarım Onaylı, Implementasyona Bekliyor

---

## Amaç

Tedarikçilerle olan borç/alacak ilişkilerini takip etmek, ödemeleri yönetmek ve raporlamak.

---

## Kullanıcı Hikayeleri

1. **Cari Hesap Görüntüleme:** Tedarikçilerin net bakiyesini, toplam borç/alacak bilgisini görebilmek
2. **Hızlı Ödeme:** Tedarikçi listesinden doğrudan ödeme yapabilmek
3. **Ödeme Takibi:** Tüm ödeme kayıtlarını kronolojik olarak görüntüleyebilmek
4. **Detaylı Geçmiş:** Tek tedarikçinin tüm hareket geçmişini (sipariş, ödeme, iade) görebilmek
5. **Raporlama:** Özet ve detaylı raporlar alabilmek, Excel'e aktarabilmek

---

## Ödeme Türleri

| Tür | Açıklama | Ek Alanlar |
|-----|----------|------------|
| Nakit | Cash ödeme | - |
| EFT | Banka havalesi | Banka, Transfer kodu |
| Çek | Çek ile ödeme | Vade tarihi, Banka, Seri no |
| Senet | Senet ile ödeme | Vade tarihi, Banka, Seri no |
| Kısmi | Kısmi ödeme | - |

---

## Menü Yapısı

```
💳 Ödemeler
├── Tedarikçi Cari (varsayılan)
└── Ödeme Kayıtları
```

---

## Sayfa Tasarımları

### 1. Tedarikçi Cari Listesi

**Amaç:** Tüm tedarikçilerin finansal durumunu özet olarak göstermek

**Sütunlar:**

| Sütun | Açıklama |
|-------|----------|
| 🏪 Tedarikçi | İsim + tıklayınca detaya gider |
| 📊 Bakiye | Net bakiye (borç = kırmızı, alacak = yeşil) |
| 📅 Son Hareket | Son işlem tarihi |
| 💵 Toplam Borç | Toplam borç tutarı |
| 💵 Toplam Alacak | Toplam alacak tutarı |
| ⚡ Aksiyon | Hızlı ödeme butonu |

**Filtreler:**
- Tümü / Sadece Borçlu / Sadece Alacaklı

**Sıralama:** En çok borçlu üstte

---

### 2. Ödeme Kayıtları Listesi

**Amaç:** Tüm ödeme movements kronolojik olarak görüntülemek

**Sütunlar:**

| Sütun | Açıklama |
|-------|----------|
| 📅 Tarih | Ödeme tarihi |
| 🏪 Tedarikçi | Tedarikçi adı |
| 💰 Tutar | Ödeme tutarı |
| 💳 Tür | Nakit / EFT / Çek / Senet / Kısmi |
| 📝 Açıklama | Opsiyonel açıklama |
| 🏷️ Referans | İlgili sipariş/makbuz numarası |
| ⚡ Aksiyon | Düzenle / Sil |

**Filtreler:**
- Tarih aralığı
- Ödeme türü
- Tedarikçi
- Tutar aralığı
- Metin araması

**Özet Kartlar (Tablo üstü):**
- Bugün
- Bu Hafta
- Bu Ay
- Toplam

---

### 3. Tedarikçi Cari Detay Sayfası

**Amaç:** Tek bir tedarikçinin tüm hesap hareketlerini görmek

**Header Bilgileri:**
- Tedarikçi adı
- Toplam Borç
- Toplam Alacak
- Net Bakiye
- Son Hareket Tarihi

**Hareket Geçmişi Tablosu:**

| Tarih | İşlem Türü | Açıklama | Borç | Alacak | Bakiye |
|-------|------------|----------|------|--------|--------|
| 2025-01-30 | Sipariş | Sipariş #1234 | ₺2,500 | - | ₺9,750 |
| 2025-01-28 | Ödeme | EFT ile ödeme | - | ₺1,500 | ₺7,250 |

**Aksiyonlar:**
- Hızlı Ödeme Yap
- Düzenle

---

### 4. Ödeme Ekleme Modalı

**Alanlar:**

| Alan | Zorunlu | Tip |
|------|---------|-----|
| Tedarikçi | ✓ | Dropdown |
| Ödeme Türü | ✓ | Radio (Nakit, EFT, Çek, Senet) |
| Tutar | ✓ | Number |
| Tarih | ✓ | Date |
| Açıklama | - | Text |
| Referans | - | Text |
| Banka (EFT) | - | Text |
| Transfer Kodu (EFT) | - | Text |
| Vade Tarihi (Çek/Senet) | - | Date |
| Banka (Çek/Senet) | - | Text |
| Serie No (Çek/Senet) | - | Text |

---

## Veri Yapısı

### Backend Modelleri

```python
# backend/models/supplier_ar.py
class PaymentType(str, enum.Enum):
    CASH = "cash"
    EFT = "eft"
    CHECK = "check"
    PROMISSORY = "promissory"
    PARTIAL = "partial"

class SupplierPayment(Base):
    __tablename__ = "supplier_payments"

    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    description = Column(String(500))
    reference = Column(String(100))

    # EFT için
    bank_name = Column(String(100))
    transfer_code = Column(String(100))

    # Çek/Senet için
    due_date = Column(DateTime)
    serial_number = Column(String(50))

    status = Column(Enum(PaymentStatus), default=PaymentStatus.COMPLETED)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

class SupplierTransaction(Base):
    """
    Hareket kaydı - her sipariş, ödeme, iade için
    Running balance hesaplama için kullanılır
    """
    __tablename__ = "supplier_transactions"

    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # 'order', 'payment', 'return'
    reference_id = Column(Integer)
    description = Column(String(500), nullable=False)
    debt_amount = Column(Numeric(10, 2), default=0)
    credit_amount = Column(Numeric(10, 2), default=0)
    running_balance = Column(Numeric(10, 2), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
```

### Frontend Types

```typescript
export type PaymentType = 'cash' | 'eft' | 'check' | 'promissory' | 'partial'
export type PaymentStatus = 'pending' | 'completed' | 'cancelled'

export interface SupplierARSummary {
  id: number
  name: string
  balance: number
  total_debt: number
  total_credit: number
  last_transaction_date: string | null
}

export interface SupplierPayment {
  id: number
  supplier_id: number
  supplier_name: string
  payment_type: PaymentType
  amount: number
  payment_date: string
  description: string | null
  reference: string | null
  bank_name: string | null
  transfer_code: string | null
  due_date: string | null
  serial_number: string | null
  status: PaymentStatus
}
```

---

## API Endpoint'leri

```
# Tedarikçi Cari Hesap
GET    /api/v1/suppliers/ar/                    # Tüm tedarikçilerin özeti
GET    /api/v1/suppliers/ar/:id                 # Tek tedarikçi detayı
GET    /api/v1/suppliers/ar/:id/transactions    # Hareket geçmişi

# Ödemeler
GET    /api/v1/payments/supplier                # Ödeme listesi
POST   /api/v1/payments/supplier                # Yeni ödeme
GET    /api/v1/payments/supplier/:id            # Ödeme detayı
PUT    /api/v1/payments/supplier/:id            # Ödeme güncelle
DELETE /api/v1/payments/supplier/:id            # Ödeme sil

# Raporlar
GET    /api/v1/payments/summary                 # Özet rapor
GET    /api/v1/payments/detail                  # Detaylı döküm
GET    /api/v1/payments/monthly/:year/:month    # Aylık rapor
GET    /api/v1/payments/export/excel            # Excel export
```

---

## Component Yapısı

```
src/views/Odemeler.vue              # Ana container
├── src/components/payments/
│   ├── SupplierARList.vue          # Tedarikçi Cari Listesi
│   ├── PaymentRecordsList.vue      # Ödeme Kayıtları
│   ├── SupplierARDetail.vue        # Tedarikçi Detayı
│   └── ui/
│       ├── PaymentSummaryCards.vue # Özet kartlar
│       ├── PaymentFilters.vue      # Filtreler
│       └── PaymentTypeBadge.vue    # Tür badge'i
```

---

## Router Konfigürasyonu

```typescript
{
  path: 'odemeler',
  name: 'odemeler',
  component: () => import('@/views/Odemeler.vue'),
  meta: { icon: '💳', title: 'Ödemeler' }
}
```

---

## Tasarım Kararları

1. **Borç = Pozitif:** Bakiye pozitifse borçlu, negatifse alacaklı (standart cari hesap mantığı)
2. **Running Balance:** Her hareket kaydında o ana kadarki bakiye tutulur - performans için
3. **Sipariş Anında Borç:** Sipariş oluşturulduğunda otomatik borç kaydı oluşur
4. **Çoklu Ödeme Türü:** Nakit, EFT, Çek, Senet, Kısmi ödeme desteklenir
5. **Detaylı Takip:** Her hareketin tarihi, türü, açıklaması tutulur
