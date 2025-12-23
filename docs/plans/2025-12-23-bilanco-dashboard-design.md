# Bilanço Dashboard Tasarımı

**Tarih:** 2025-12-23
**Durum:** Onaylandı

## Problem

Mevcut dashboard sadece `date.today()` için sorgu yapıyor. Kullanıcı akşam veri giriyor, sabah geçmiş verilere bakarak güne hazırlanıyor. Bugün için veri olmadığında tüm kartlar ₺0 gösteriyor.

## Çözüm

Tek sayfa, çoklu bölüm yaklaşımı:
- Üstte "Dün" özeti (sabah açıldığında anında görünür)
- Ortada "Bu Hafta vs Geçen Hafta" karşılaştırması
- Altta "Bu Ay" özeti ve tahminler

## Tasarım Kararları

1. **Tab adı:** "Dashboard" → "Bilanço" olarak değişecek
2. **Salon/Telefon kartları kaldırıldı:** Kullanıcı ihtiyaç duymuyor
3. **Sadece ciro odaklı:** Haftalık karşılaştırmada sadece ciro gösteriliyor
4. **Türkçe:** Tüm gün adları ve metinler Türkçe

---

## Bölüm 1: Üst Kısım (AI + Dün Özeti)

```
┌─────────────────────────────────────────────────────────────┐
│  ✨ AI Asistan (mevcut - korunuyor)                        │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │ Beklenen     │ Tahmini      │ Hava         │            │
│  │ Ciro ₺11,475 │ Müşteri 114  │ ☁️ Yağmurlu  │            │
│  └──────────────┴──────────────┴──────────────┘            │
│  "Günaydın patron! Bugün..."                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  📅 Dün (22 Aralık 2025, Pazartesi)                        │
│  ┌─────────────────┬─────────────────┬─────────────────┐   │
│  │ 💰 Toplam Ciro  │ 📦 Toplam Gider │ 📈 Net Kâr      │   │
│  │    ₺48,500     │    ₺31,200     │    ₺17,300     │   │
│  │  ▲ %12 önceki  │  ▼ %5 önceki   │  ▲ %18 önceki  │   │
│  └─────────────────┴─────────────────┴─────────────────┘   │
│                                                             │
│  Detay: Online ₺38,200 · Mal Alımı ₺18,000 · Gider ₺8,200 │
│         Staff ₺3,500 · Kurye ₺1,500                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  🚀 Hızlı İşlemler                                         │
│  [Satış Gir] [Mal Alımı] [Gider Ekle] [Üretim Gir]        │
└─────────────────────────────────────────────────────────────┘
```

### Detaylar

- **Dün başlığı dinamik:** Tarih ve gün adı gösterir
- **Karşılaştırma göstergesi:** Her kartta önceki güne göre % değişim
- **Detay satırı:** Tek satırda tüm alt kırılımlar

---

## Bölüm 2: Orta Kısım (Haftalık Karşılaştırma)

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Bu Hafta vs Geçen Hafta                                │
│                                                             │
│  ┌─────────────────────────┬─────────────────────────┐     │
│  │ Bu Hafta (16-22 Aralık) │ Geçen Hafta (9-15 Aralık)│     │
│  │      ₺285,000           │      ₺248,000           │     │
│  │      ▲ %15 artış        │                         │     │
│  └─────────────────────────┴─────────────────────────┘     │
│                                                             │
│  Gün Bazlı Karşılaştırma:                                  │
│  ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐              │
│  │ Pzt │ Sal │ Çar │ Per │ Cum │ Cmt │ Paz │              │
│  │ 42K │ 38K │ 45K │ 41K │ 52K │ 48K │ 19K │ ← Bu Hafta   │
│  │ 35K │ 33K │ 40K │ 38K │ 48K │ 42K │ 12K │ ← Geçen      │
│  └─────┴─────┴─────┴─────┴─────┴─────┴─────┘              │
│                                                             │
│  🏆 En iyi gün: Cuma (₺52,000)                             │
│  📉 En düşük: Pazar (₺19,000)                              │
└─────────────────────────────────────────────────────────────┘
```

### Detaylar

- **İki hafta yan yana:** Anında karşılaştırma
- **Gün bazlı bar chart:** Üst üste iki çubuk (bu hafta koyu, geçen hafta açık)
- **Mini insight'lar:** En iyi/en düşük gün otomatik hesaplanıyor
- **Türkçe gün adları:** Pzt, Sal, Çar, Per, Cum, Cmt, Paz

---

## Bölüm 3: Alt Kısım (Aylık Özet)

```
┌─────────────────────────────────────────────────────────────┐
│  📆 Aralık 2025 Özeti                        22/31 gün     │
│                                                             │
│  ┌─────────────────┬─────────────────┬─────────────────┐   │
│  │ 💰 Toplam Ciro  │ 📦 Toplam Gider │ 📈 Net Kâr      │   │
│  │   ₺966,207     │   ₺612,400     │   ₺353,807     │   │
│  │                 │                 │                 │   │
│  │ Geçen Ay:       │ Geçen Ay:       │ Geçen Ay:       │   │
│  │ ₺1,124,000     │ ₺698,000       │ ₺426,000       │   │
│  └─────────────────┴─────────────────┴─────────────────┘   │
│                                                             │
│  📊 Aylık Ciro Grafiği                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │     ▂▃▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆                         │   │
│  │     1  5  10  15  20  25  30                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Günlük Ortalama: ₺43,918 · Kalan Gün: 9                   │
│  Tahmini Ay Sonu: ₺1,361,469                               │
└─────────────────────────────────────────────────────────────┘
```

### Detaylar

- **Gün sayacı:** "22/31 gün" ayın neresinde olduğumuzu gösterir
- **Geçen ay karşılaştırması:** Her kartın altında geçen ayın aynı dönemi
- **Mini çizgi grafik:** Ayın günlük ciro trendi
- **Akıllı tahmin:** Günlük ortalama × kalan gün = Tahmini ay sonu

---

## API Değişiklikleri

### Yeni Endpoint: `/api/reports/bilanco`

```python
@router.get("/bilanco")
def get_bilanco_stats(db: DBSession, ctx: CurrentBranchContext):
    """
    Bilanço dashboard için tüm verileri döner:
    - yesterday: Dünün özeti
    - this_week: Bu hafta verileri
    - last_week: Geçen hafta verileri
    - this_month: Bu ay özeti
    - last_month: Geçen ay özeti
    """
```

### Response Schema

```python
class BilancoStats(BaseModel):
    # Dün
    yesterday_date: date
    yesterday_day_name: str  # "Pazartesi"
    yesterday_revenue: Decimal
    yesterday_expenses: Decimal
    yesterday_profit: Decimal
    yesterday_vs_previous: Decimal  # % değişim
    yesterday_breakdown: dict  # Online, Mal Alımı, Gider, Staff, Kurye

    # Bu Hafta
    this_week_start: date
    this_week_end: date
    this_week_total: Decimal
    this_week_daily: list[dict]  # [{day: "Pzt", amount: 42000}, ...]
    this_week_best_day: dict
    this_week_worst_day: dict

    # Geçen Hafta
    last_week_start: date
    last_week_end: date
    last_week_total: Decimal
    last_week_daily: list[dict]
    week_vs_week_change: Decimal  # % değişim

    # Bu Ay
    this_month_name: str  # "Aralık 2025"
    this_month_days_passed: int
    this_month_days_total: int
    this_month_revenue: Decimal
    this_month_expenses: Decimal
    this_month_profit: Decimal
    this_month_daily_avg: Decimal
    this_month_forecast: Decimal  # Tahmini ay sonu
    this_month_chart: list[dict]  # Günlük veriler

    # Geçen Ay
    last_month_revenue: Decimal
    last_month_expenses: Decimal
    last_month_profit: Decimal
```

---

## Frontend Değişiklikleri

1. **Sidebar:** "Dashboard" → "Bilanço" olarak güncelle
2. **Router:** `/dashboard` → `/bilanco` (veya aynı kalabilir, sadece isim değişir)
3. **Component:** `Dashboard.vue` → `Bilanco.vue` olarak yeniden yaz
4. **Mevcut kartları kaldır:** Salon, Telefon, Online, eski Toplam Ciro/Gider/Kar
5. **Yeni bölümler ekle:** Dün Özeti, Haftalık Karşılaştırma, Aylık Özet

---

## Kaldırılan Özellikler

- ❌ Salon Satışı kartı
- ❌ Telefon Paket kartı
- ❌ Online Satış kartı (toplam ciroya dahil edildi)
- ❌ Eski "Haftalık Satış Trendi" (yeni haftalık karşılaştırma ile değiştirildi)

## Korunan Özellikler

- ✅ AI Asistan kartı (olduğu gibi)
- ✅ Hızlı İşlemler butonları

---

## Gelecek İyileştirmeler (v2)

- Stok/Üretim tahmini: "Bugün ne kadar üretmeliyim?"
- Hedef belirleme: Aylık ciro hedefi ve ilerleme çubuğu
- Anomali uyarıları: "Bugün normalden %30 düşük satış"
