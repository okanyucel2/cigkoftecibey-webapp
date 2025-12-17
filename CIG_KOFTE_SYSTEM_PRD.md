# 🥙 ÇİĞ KÖFTE RESTORAN YÖNETİM SİSTEMİ
## Product Requirements Document (PRD) - Enterprise Edition

**Versiyon:** 1.0  
**Tarih:** 2025-12-16  
**Hazırlayan:** Claude (Anthropic)  
**Hedef:** Claude Code Implementation  

---

## 📋 İÇİNDEKİLER

1. [Executive Summary](#1-executive-summary)
2. [Problem Tanımı & Çözüm](#2-problem-tanımı--çözüm)
3. [Kullanıcı Personaları](#3-kullanıcı-personaları)
4. [Sistem Mimarisi](#4-sistem-mimarisi)
5. [Veri Modeli](#5-veri-modeli)
6. [Özellik Spesifikasyonları](#6-özellik-spesifikasyonları)
7. [Ekran Tasarımları](#7-ekran-tasarımları)
8. [Metrikler & KPI'lar](#8-metrikler--kpılar)
9. [AI Özellikleri](#9-ai-özellikleri)
10. [Rol Bazlı Erişim Kontrolü](#10-rol-bazlı-erişim-kontrolü)
11. [UI/UX Tasarım Sistemi](#11-uiux-tasarım-sistemi)
12. [Teknik Stack](#12-teknik-stack)
13. [Fazlama & Roadmap](#13-fazlama--roadmap)

---

## 1. EXECUTIVE SUMMARY

### 1.1 Vizyon
Türkiye'nin en gelişmiş çiğ köfte restoran yönetim platformu. Excel tabanlı manuel süreçleri tamamen ortadan kaldıran, AI destekli tahminleme yapan, çoklu şube yönetimi sağlayan enterprise-grade bir sistem.

### 1.2 Mevcut Durum (As-Is)
- **Veri Girişi:** Manuel Excel, hataya açık
- **Ay Sonu Kapanış:** ~10 dakika (veri hataları ile +saatler)
- **Şube:** 1 (büyüme planı var)
- **Günlük Sipariş:** 1,000-1,500 (25-30 paket)
- **Kullanıcılar:** İşletme yöneticisi, kasiyer
- **Problem:** Yanlış veri girişi, yanlış hücreye giriş, görünürlük eksikliği

### 1.3 Hedef Durum (To-Be)
- **Veri Girişi:** Guided forms, validation, tek tıkla giriş
- **Ay Sonu Kapanış:** < 30 saniye (otomatik)
- **Şube:** Sınırsız (multi-tenant)
- **AI:** Talep tahmini, maliyet optimizasyonu, anomali tespiti
- **Real-time:** Canlı dashboard, anlık metrikler

### 1.4 Başarı Kriterleri
| Metrik | Mevcut | Hedef |
|--------|--------|-------|
| Veri giriş süresi | 15-20 dk/gün | < 3 dk/gün |
| Hata oranı | %5-10 | < %0.1 |
| Ay sonu kapanış | 10 dk + düzeltmeler | < 30 sn |
| Karar hızı | Günler | Anlık |
| Şube ölçeklenebilirlik | 1 | Sınırsız |

---

## 2. PROBLEM TANIMI & ÇÖZÜM

### 2.1 Mevcut Problemler

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXCEL KAYNAKLI PROBLEMLER                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ❌ Manuel Veri Girişi                                          │
│     └─ Her gün 10+ farklı sheet'e veri girişi                   │
│     └─ Yanlış hücreye giriş riski                               │
│     └─ Formül bozulma riski                                     │
│                                                                  │
│  ❌ Veri Tutarsızlığı                                           │
│     └─ Aynı veri birden fazla yerde                             │
│     └─ Senkronizasyon sorunu                                    │
│     └─ Versiyon kontrolü yok                                    │
│                                                                  │
│  ❌ Görünürlük Eksikliği                                        │
│     └─ Anlık kar/zarar görülemiyor                              │
│     └─ Trend analizi manuel                                      │
│     └─ Alarm/uyarı mekanizması yok                              │
│                                                                  │
│  ❌ Ölçeklenebilirlik                                           │
│     └─ Çoklu şube yönetimi imkansız                             │
│     └─ Kullanıcı bazlı erişim yok                               │
│     └─ Eşzamanlı düzenleme sorunu                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Çözüm Yaklaşımı

```
┌─────────────────────────────────────────────────────────────────┐
│                      ÇÖZÜM MİMARİSİ                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✅ Akıllı Veri Girişi                                          │
│     └─ Context-aware formlar                                    │
│     └─ Auto-complete & öneriler                                 │
│     └─ Real-time validation                                     │
│     └─ Bulk import (fotoğraftan OCR - gelecek)                  │
│                                                                  │
│  ✅ Single Source of Truth                                       │
│     └─ Normalize edilmiş veritabanı                             │
│     └─ Otomatik agregasyon                                      │
│     └─ Audit trail (kim, ne, ne zaman)                          │
│                                                                  │
│  ✅ Real-time Analytics                                          │
│     └─ Live dashboard                                           │
│     └─ Trend grafikleri                                         │
│     └─ AI-powered insights                                      │
│     └─ Proaktif uyarılar                                        │
│                                                                  │
│  ✅ Enterprise Ölçek                                             │
│     └─ Multi-tenant architecture                                │
│     └─ Role-based access control                                │
│     └─ Şube bazlı izolasyon + merkezi raporlama                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. KULLANICI PERSONALARI

### 3.1 Persona: İşletme Yöneticisi (Okan)

```yaml
Profil:
  Ad: Okan
  Rol: İşletme Sahibi / Genel Müdür
  Teknik Seviye: Orta (Excel kullanabiliyor)
  Cihaz: MacBook Pro, iPhone
  Çalışma Saatleri: 08:00-22:00 (esnek)

Günlük Rutini:
  Sabah:
    - Dünün satış ve maliyet özetine bak
    - Stok durumunu kontrol et
    - Personel devamsızlık/izin kontrol
  
  Gün İçi:
    - Tedarikçi siparişlerini onayla
    - Anlık satış performansını izle
    - Personel mesai takibi
  
  Akşam:
    - Günlük kapanış raporu
    - Yarının planlaması
    - Kritik metriklere son bakış

Acı Noktaları:
  - "Excel'e giriş yapmak saatlerimi alıyor"
  - "Ay sonunda rakamlar tutmuyor, düzeltmek 2 saat"
  - "Hangi ürün karlı bilmiyorum"
  - "Personel maliyeti kontrolden çıkıyor"
  - "İkinci şubeyi açsam yönetemem"

İstekleri:
  - Tek bakışta tüm resmi görmek
  - Telefondan anlık erişim
  - Otomatik uyarılar (stok azaldı, maliyet arttı)
  - AI önerileri (ne zaman malzeme al, kaç kişi çalıştır)

Başarı Metrikleri:
  - Veri girişine harcanan süre %80 azalsın
  - Anlık kar/zarar görebileyim
  - Ay sonu 1 dakikada kapansın
```

### 3.2 Persona: Kasiyer (Ayşe)

```yaml
Profil:
  Ad: Ayşe
  Rol: Kasiyer / Ön Büro
  Teknik Seviye: Düşük-Orta
  Cihaz: Restoran tableti, kendi telefonu
  Çalışma Saatleri: Vardiyalı (07:00-15:00 veya 15:00-23:00)

Günlük Rutini:
  Vardiya Başı:
    - Kasa açılış sayımı
    - Günlük hazırlık kontrolü
  
  Gün İçi:
    - Sipariş alma (salon + paket)
    - Ödeme tahsilatı
    - Müşteri ilişkileri
  
  Vardiya Sonu:
    - Kasa kapanış sayımı
    - Z raporu
    - Eksik/fazla bildirimi

Acı Noktaları:
  - "Excel'e giriş yapmayı bilmiyorum"
  - "Yanlış yere yazıyorum, patron kızıyor"
  - "Kasa sayımı uzun sürüyor"
  - "Hangi ürün bitti bilmiyorum"

İstekleri:
  - Basit, büyük butonlu arayüz
  - Hata yapamayacağım form
  - Tek tıkla kasa kapanışı
  - Stok uyarıları

Başarı Metrikleri:
  - Sıfır veri giriş hatası
  - Kasa kapanış < 2 dakika
  - Stok sorunu yaşamama
```

### 3.3 Persona: Bölge Müdürü (Gelecek - Çoklu Şube)

```yaml
Profil:
  Ad: Mehmet
  Rol: Bölge Müdürü (3-5 şube)
  Teknik Seviye: Orta
  Cihaz: Laptop, Tablet, Telefon
  Çalışma Saatleri: 09:00-18:00

Sorumlulukları:
  - Birden fazla şubenin performans takibi
  - Şubeler arası karşılaştırma
  - Kaynaklar arası optimizasyon
  - Merkezi satın alma koordinasyonu

İstekleri:
  - Tüm şubeleri tek ekranda görmek
  - Şube bazlı drill-down
  - Benchmark ve karşılaştırma
  - Konsolide raporlar
```

---

## 4. SİSTEM MİMARİSİ

### 4.1 Yüksek Seviye Mimari

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ÇİĞ KÖFTE YÖNETİM SİSTEMİ                        │
│                         Enterprise Architecture                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                            PRESENTATION LAYER                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│   │   Web App    │  │  Mobile PWA  │  │   Tablet     │                  │
│   │   (Vue 3)    │  │   (Vue 3)    │  │   Kiosk      │                  │
│   └──────────────┘  └──────────────┘  └──────────────┘                  │
│          │                 │                 │                           │
│          └─────────────────┼─────────────────┘                           │
│                            │                                             │
│                    ┌───────▼───────┐                                     │
│                    │  API Gateway  │                                     │
│                    │   (FastAPI)   │                                     │
│                    └───────────────┘                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                            APPLICATION LAYER                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      CORE SERVICES                               │   │
│   ├─────────────────────────────────────────────────────────────────┤   │
│   │                                                                  │   │
│   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │   │
│   │  │   Satış     │ │   Stok      │ │  Personel   │ │  Finans   │ │   │
│   │  │  Service    │ │  Service    │ │  Service    │ │  Service  │ │   │
│   │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │   │
│   │                                                                  │   │
│   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │   │
│   │  │  Üretim     │ │  Tedarik    │ │  Raporlama  │ │    AI     │ │   │
│   │  │  Service    │ │  Service    │ │  Service    │ │  Service  │ │   │
│   │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    CROSS-CUTTING CONCERNS                        │   │
│   ├─────────────────────────────────────────────────────────────────┤   │
│   │  Auth/RBAC │ Audit Trail │ Notifications │ Multi-Tenancy       │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│   │   PostgreSQL     │  │     Redis        │  │   TimescaleDB    │      │
│   │   (Primary DB)   │  │   (Cache/Queue)  │  │   (Time Series)  │      │
│   └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│                                                                          │
│   ┌──────────────────┐  ┌──────────────────┐                            │
│   │   File Storage   │  │   AI Model Store │                            │
│   │   (Receipts/Img) │  │   (ML Artifacts) │                            │
│   └──────────────────┘  └──────────────────┘                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Multi-Tenant Mimari

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MULTI-TENANT ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                         ┌─────────────────┐                              │
│                         │   TENANT: HQ    │                              │
│                         │   (Holding)     │                              │
│                         └────────┬────────┘                              │
│                                  │                                       │
│              ┌───────────────────┼───────────────────┐                  │
│              │                   │                   │                  │
│      ┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐         │
│      │   BRANCH 1    │   │   BRANCH 2    │   │   BRANCH N    │         │
│      │   Kadıköy     │   │   Beşiktaş    │   │   ...         │         │
│      └───────────────┘   └───────────────┘   └───────────────┘         │
│                                                                          │
│  Data Isolation Strategy:                                                │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Option A: Schema-per-tenant (Seçilen ✓)                        │    │
│  │  - Her şube ayrı schema: branch_001.sales, branch_002.sales     │    │
│  │  - Güçlü izolasyon                                              │    │
│  │  - Kolay backup/restore per branch                              │    │
│  │  - Cross-branch query için central reporting schema             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  Central Schema (reporting):                                             │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  - Consolidated views                                           │    │
│  │  - Materialized views for performance                          │    │
│  │  - Real-time sync via triggers                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. VERİ MODELİ

### 5.1 Entity Relationship Diagram (Conceptual)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CORE DATA MODEL                                  │
└─────────────────────────────────────────────────────────────────────────┘

                            ┌─────────────┐
                            │   TENANT    │
                            │  (Holding)  │
                            └──────┬──────┘
                                   │
                                   │ 1:N
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                              BRANCH (Şube)                                │
│  - id, tenant_id, name, code, address, phone, status, created_at        │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
           ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│      USER        │    │     PRODUCT      │    │    SUPPLIER      │
│  - id            │    │  - id            │    │  - id            │
│  - branch_id     │    │  - branch_id     │    │  - branch_id     │
│  - name          │    │  - category_id   │    │  - name          │
│  - email         │    │  - name          │    │  - contact       │
│  - role          │    │  - unit          │    │  - phone         │
│  - pin_code      │    │  - cost_price    │    │  - category      │
│  - status        │    │  - sale_price    │    │  - status        │
└────────┬─────────┘    │  - recipe_id     │    └────────┬─────────┘
         │              └────────┬─────────┘             │
         │                       │                       │
         │              ┌────────┴────────┐              │
         │              │                 │              │
         │              ▼                 ▼              │
         │    ┌──────────────┐  ┌──────────────┐        │
         │    │   CATEGORY   │  │    RECIPE    │        │
         │    │  - id        │  │  - id        │        │
         │    │  - name      │  │  - product_id│        │
         │    │  - parent_id │  │  - name      │        │
         │    └──────────────┘  └──────┬───────┘        │
         │                             │                │
         │                             ▼                │
         │                   ┌──────────────────┐       │
         │                   │ RECIPE_INGREDIENT│       │
         │                   │  - recipe_id     │       │
         │                   │  - ingredient_id │       │
         │                   │  - quantity      │       │
         │                   │  - unit          │       │
         │                   └────────┬─────────┘       │
         │                            │                 │
         │              ┌─────────────┴─────────┐       │
         │              ▼                       │       │
         │    ┌──────────────────┐              │       │
         │    │   INGREDIENT     │              │       │
         │    │  (Raw Material)  │◄─────────────┼───────┘
         │    │  - id            │              │
         │    │  - name          │              │
         │    │  - unit          │              │
         │    │  - category      │              │
         │    │  - supplier_id   │              │
         │    │  - min_stock     │              │
         │    │  - current_stock │              │
         │    └────────┬─────────┘              │
         │             │                        │
         │             │                        │
         ▼             ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          TRANSACTIONAL TABLES                            │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│      ORDER       │    │    PURCHASE      │    │   PRODUCTION     │
│  - id            │    │  - id            │    │  (Hamur Üretimi) │
│  - branch_id     │    │  - branch_id     │    │  - id            │
│  - user_id       │    │  - supplier_id   │    │  - branch_id     │
│  - type (salon/  │    │  - date          │    │  - date          │
│    paket)        │    │  - total         │    │  - product_type  │
│  - channel       │    │  - status        │    │  - quantity_kg   │
│  - total         │    │  - payment_status│    │  - batch_count   │
│  - status        │    └────────┬─────────┘    │  - cost          │
│  - created_at    │             │              │  - user_id       │
└────────┬─────────┘             ▼              └────────┬─────────┘
         │              ┌──────────────────┐             │
         ▼              │  PURCHASE_ITEM   │             │
┌──────────────────┐    │  - purchase_id   │             │
│   ORDER_ITEM     │    │  - ingredient_id │             │
│  - order_id      │    │  - quantity      │             │
│  - product_id    │    │  - unit_price    │             │
│  - quantity      │    │  - total         │             │
│  - unit_price    │    └──────────────────┘             │
│  - total         │                                     │
└──────────────────┘                                     │
                                                         │
┌──────────────────┐    ┌──────────────────┐             │
│     EXPENSE      │    │   CASH_REGISTER  │             │
│  - id            │    │  - id            │             │
│  - branch_id     │    │  - branch_id     │             │
│  - category      │    │  - date          │             │
│  - subcategory   │    │  - opening       │             │
│  - description   │    │  - closing       │             │
│  - amount        │    │  - expected      │             │
│  - date          │    │  - difference    │             │
│  - receipt_url   │    │  - user_id       │             │
│  - user_id       │    └──────────────────┘             │
└──────────────────┘                                     │
                                                         │
┌──────────────────┐    ┌──────────────────┐             │
│    EMPLOYEE      │    │   EMPLOYEE_      │             │
│  - id            │    │   ATTENDANCE     │◄────────────┘
│  - branch_id     │    │  - employee_id   │
│  - name          │    │  - date          │
│  - position      │    │  - shift         │
│  - salary        │    │  - hours_worked  │
│  - sgk_premium   │    │  - overtime_hrs  │
│  - hire_date     │    │  - meal_provided │
│  - status        │    │  - notes         │
└──────────────────┘    └──────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           AUDIT & ANALYTICS                              │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   AUDIT_LOG      │    │   DAILY_SUMMARY  │    │   AI_PREDICTION  │
│  - id            │    │  - id            │    │  - id            │
│  - branch_id     │    │  - branch_id     │    │  - branch_id     │
│  - user_id       │    │  - date          │    │  - date          │
│  - action        │    │  - total_sales   │    │  - metric_type   │
│  - entity_type   │    │  - total_expense │    │  - predicted_val │
│  - entity_id     │    │  - total_purchase│    │  - actual_val    │
│  - old_value     │    │  - net_profit    │    │  - accuracy      │
│  - new_value     │    │  - order_count   │    │  - model_version │
│  - timestamp     │    │  - avg_ticket    │    │  - created_at    │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

### 5.2 Detaylı Schema Tanımları

```sql
-- ============================================
-- TENANT & BRANCH (Multi-Tenancy)
-- ============================================

CREATE TABLE tenant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    contact_email VARCHAR(255),
    subscription_plan VARCHAR(50) DEFAULT 'enterprise',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE branch (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenant(id),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL, -- e.g., 'KDK' for Kadıköy
    address TEXT,
    city VARCHAR(50),
    district VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(255),
    tax_number VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    opening_time TIME DEFAULT '08:00',
    closing_time TIME DEFAULT '23:00',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, code)
);

-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE app_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    pin_code VARCHAR(6), -- For quick POS access
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) NOT NULL, -- 'owner', 'manager', 'cashier', 'kitchen', 'regional_manager'
    permissions JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active',
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- PRODUCT CATALOG
-- ============================================

CREATE TABLE product_category (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    parent_id UUID REFERENCES product_category(id),
    name VARCHAR(100) NOT NULL,
    display_order INT DEFAULT 0,
    icon VARCHAR(50),
    color VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE product (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    category_id UUID REFERENCES product_category(id),
    sku VARCHAR(50),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    unit VARCHAR(20) NOT NULL, -- 'adet', 'porsiyon', 'kg'
    sale_price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2), -- Calculated from recipe or manual
    tax_rate DECIMAL(5,2) DEFAULT 10.00,
    image_url TEXT,
    is_active BOOLEAN DEFAULT true,
    is_available BOOLEAN DEFAULT true, -- For temp out-of-stock
    display_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INGREDIENT & RECIPE (BOM - Bill of Materials)
-- ============================================

CREATE TABLE ingredient_category (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL, -- 'Manav', 'Kuru Gıda', 'Süt Ürünleri', etc.
    display_order INT DEFAULT 0
);

CREATE TABLE ingredient (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    category_id UUID REFERENCES ingredient_category(id),
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL, -- 'kg', 'lt', 'adet', 'paket'
    min_stock_level DECIMAL(10,3) DEFAULT 0,
    current_stock DECIMAL(10,3) DEFAULT 0,
    avg_unit_cost DECIMAL(10,2), -- Weighted average
    last_purchase_price DECIMAL(10,2),
    shelf_life_days INT,
    storage_location VARCHAR(50),
    is_critical BOOLEAN DEFAULT false, -- Kritik malzeme (üretimi durdurur)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE recipe (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES product(id) UNIQUE,
    name VARCHAR(100) NOT NULL,
    yield_quantity DECIMAL(10,3) NOT NULL, -- Kaç porsiyon/adet çıkar
    yield_unit VARCHAR(20) NOT NULL,
    preparation_time_min INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE recipe_ingredient (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id UUID REFERENCES recipe(id),
    ingredient_id UUID REFERENCES ingredient(id),
    quantity DECIMAL(10,3) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    is_optional BOOLEAN DEFAULT false,
    notes TEXT,
    UNIQUE(recipe_id, ingredient_id)
);

-- ============================================
-- SUPPLIER & PURCHASING
-- ============================================

CREATE TABLE supplier (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    name VARCHAR(100) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    tax_number VARCHAR(20),
    category VARCHAR(50), -- 'manav', 'kasap', 'kurugida', etc.
    payment_terms VARCHAR(50), -- 'peşin', '15 gün vadeli', etc.
    rating INT CHECK (rating BETWEEN 1 AND 5),
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE supplier_product (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id UUID REFERENCES supplier(id),
    ingredient_id UUID REFERENCES ingredient(id),
    supplier_sku VARCHAR(50),
    unit_price DECIMAL(10,2),
    min_order_quantity DECIMAL(10,3),
    lead_time_days INT DEFAULT 1,
    is_preferred BOOLEAN DEFAULT false,
    UNIQUE(supplier_id, ingredient_id)
);

CREATE TABLE purchase_order (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    supplier_id UUID REFERENCES supplier(id),
    order_number VARCHAR(50) UNIQUE,
    order_date DATE NOT NULL,
    expected_delivery DATE,
    actual_delivery DATE,
    subtotal DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'ordered', 'received', 'partial', 'cancelled'
    payment_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'partial', 'paid'
    payment_due_date DATE,
    notes TEXT,
    created_by UUID REFERENCES app_user(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE purchase_order_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purchase_order_id UUID REFERENCES purchase_order(id),
    ingredient_id UUID REFERENCES ingredient(id),
    quantity_ordered DECIMAL(10,3) NOT NULL,
    quantity_received DECIMAL(10,3) DEFAULT 0,
    unit VARCHAR(20) NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    notes TEXT
);

-- ============================================
-- SALES & ORDERS
-- ============================================

CREATE TABLE sales_channel (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL, -- 'SALON', 'PAKET', 'TRENDYOL', 'GETIR', etc.
    name VARCHAR(50) NOT NULL,
    commission_rate DECIMAL(5,2) DEFAULT 0, -- Platform komisyonu
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE sales_order (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    order_number VARCHAR(50), -- Auto-generated: KDK-20251216-0001
    channel_id UUID REFERENCES sales_channel(id),
    channel_order_id VARCHAR(100), -- External platform order ID
    order_type VARCHAR(20) NOT NULL, -- 'salon', 'paket', 'online'
    table_number VARCHAR(10),
    customer_name VARCHAR(100),
    customer_phone VARCHAR(20),
    delivery_address TEXT,
    subtotal DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) DEFAULT 0,
    delivery_fee DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(20), -- 'cash', 'card', 'online', 'mixed'
    payment_status VARCHAR(20) DEFAULT 'pending',
    order_status VARCHAR(20) DEFAULT 'new', -- 'new', 'preparing', 'ready', 'delivered', 'cancelled'
    notes TEXT,
    created_by UUID REFERENCES app_user(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sales_order_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES sales_order(id),
    product_id UUID REFERENCES product(id),
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    total_price DECIMAL(12,2) NOT NULL,
    notes TEXT -- Special requests
);

-- ============================================
-- PRODUCTION (Hamur Üretimi)
-- ============================================

CREATE TABLE production_batch (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    batch_number VARCHAR(50), -- Auto: PROD-20251216-001
    production_date DATE NOT NULL,
    product_type VARCHAR(50) NOT NULL, -- 'cig_kofte_hamuru', 'lavaş', etc.
    quantity_kg DECIMAL(10,2) NOT NULL,
    batch_count INT, -- Kaç legen/tepsi
    unit_size_kg DECIMAL(10,2), -- Legen başı kg
    total_cost DECIMAL(12,2), -- Calculated from ingredients
    cost_per_kg DECIMAL(10,2), -- Calculated
    quality_score INT CHECK (quality_score BETWEEN 1 AND 5),
    notes TEXT,
    created_by UUID REFERENCES app_user(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE production_ingredient_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID REFERENCES production_batch(id),
    ingredient_id UUID REFERENCES ingredient(id),
    quantity_used DECIMAL(10,3) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    unit_cost DECIMAL(10,2),
    total_cost DECIMAL(12,2)
);

-- ============================================
-- EXPENSES
-- ============================================

CREATE TABLE expense_category (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES expense_category(id),
    budget_monthly DECIMAL(12,2), -- Aylık bütçe limiti
    is_fixed BOOLEAN DEFAULT false, -- Sabit gider mi?
    is_active BOOLEAN DEFAULT true
);

-- Seed data örneği:
-- INSERT INTO expense_category (code, name, is_fixed) VALUES
-- ('KIRA', 'Kira Giderleri', true),
-- ('KIRA_DUKKAN', 'Dükkan Kirası', true),
-- ('KIRA_DEPO', 'Depo Kirası', true),
-- ('KIRA_PERSONEL_EV', 'Personel Evi Kirası', true),
-- ('FATURA', 'Faturalar', false),
-- ('FATURA_ELEKTRIK', 'Elektrik', false),
-- ('FATURA_SU', 'Su', false),
-- ('FATURA_GAZ', 'Doğalgaz', false),
-- ('FATURA_INTERNET', 'İnternet', false),
-- ('ARAC', 'Araç Giderleri', false),
-- ('ARAC_YAKIT', 'Yakıt', false),
-- ('ARAC_BAKIM', 'Bakım/Onarım', false),
-- ('PERSONEL', 'Personel Giderleri', false),
-- ('PERSONEL_YEMEK', 'Personel Yemek', false),
-- ('DIGER', 'Diğer Giderler', false);

CREATE TABLE expense (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    category_id UUID REFERENCES expense_category(id),
    expense_date DATE NOT NULL,
    description TEXT,
    amount DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(20),
    payment_status VARCHAR(20) DEFAULT 'paid',
    receipt_url TEXT,
    vendor_name VARCHAR(100),
    is_recurring BOOLEAN DEFAULT false,
    recurrence_period VARCHAR(20), -- 'monthly', 'weekly', etc.
    notes TEXT,
    created_by UUID REFERENCES app_user(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- EMPLOYEE & PAYROLL
-- ============================================

CREATE TABLE employee (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    employee_number VARCHAR(20) UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    tc_kimlik VARCHAR(11),
    phone VARCHAR(20),
    address TEXT,
    position VARCHAR(50) NOT NULL, -- 'şef', 'kasiyer', 'garson', 'kurye', etc.
    employment_type VARCHAR(20) NOT NULL, -- 'full_time', 'part_time', 'seasonal'
    base_salary DECIMAL(12,2),
    sgk_premium DECIMAL(12,2),
    hire_date DATE NOT NULL,
    termination_date DATE,
    bank_name VARCHAR(50),
    iban VARCHAR(34),
    emergency_contact VARCHAR(100),
    emergency_phone VARCHAR(20),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE employee_attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID REFERENCES employee(id),
    attendance_date DATE NOT NULL,
    shift_type VARCHAR(20), -- 'morning', 'evening', 'full'
    check_in TIME,
    check_out TIME,
    hours_worked DECIMAL(5,2),
    overtime_hours DECIMAL(5,2) DEFAULT 0,
    break_minutes INT DEFAULT 0,
    meal_provided BOOLEAN DEFAULT true,
    status VARCHAR(20) DEFAULT 'present', -- 'present', 'absent', 'late', 'leave', 'sick'
    notes TEXT,
    created_by UUID REFERENCES app_user(id),
    UNIQUE(employee_id, attendance_date)
);

CREATE TABLE payroll (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    employee_id UUID REFERENCES employee(id),
    period_year INT NOT NULL,
    period_month INT NOT NULL,
    base_salary DECIMAL(12,2) NOT NULL,
    overtime_amount DECIMAL(12,2) DEFAULT 0,
    bonus_amount DECIMAL(12,2) DEFAULT 0,
    deduction_amount DECIMAL(12,2) DEFAULT 0,
    advance_amount DECIMAL(12,2) DEFAULT 0, -- Avans
    sgk_employee DECIMAL(12,2) DEFAULT 0,
    sgk_employer DECIMAL(12,2) DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0,
    net_salary DECIMAL(12,2) NOT NULL,
    gross_cost DECIMAL(12,2) NOT NULL, -- Total employer cost
    payment_date DATE,
    payment_status VARCHAR(20) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(employee_id, period_year, period_month)
);

-- ============================================
-- CASH REGISTER
-- ============================================

CREATE TABLE cash_register_session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    session_date DATE NOT NULL,
    opening_user_id UUID REFERENCES app_user(id),
    closing_user_id UUID REFERENCES app_user(id),
    opening_time TIMESTAMP NOT NULL,
    closing_time TIMESTAMP,
    opening_cash DECIMAL(12,2) NOT NULL,
    expected_cash DECIMAL(12,2), -- Calculated
    actual_cash DECIMAL(12,2),
    cash_difference DECIMAL(12,2),
    total_card_sales DECIMAL(12,2) DEFAULT 0,
    total_cash_sales DECIMAL(12,2) DEFAULT 0,
    total_online_sales DECIMAL(12,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'open', -- 'open', 'closed', 'reconciled'
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- AUDIT & LOGGING
-- ============================================

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    user_id UUID REFERENCES app_user(id),
    action VARCHAR(50) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'EXPORT', etc.
    entity_type VARCHAR(50) NOT NULL, -- Table name
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- AI & ANALYTICS
-- ============================================

CREATE TABLE daily_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    summary_date DATE NOT NULL,
    
    -- Sales metrics
    total_orders INT DEFAULT 0,
    salon_orders INT DEFAULT 0,
    package_orders INT DEFAULT 0,
    online_orders INT DEFAULT 0,
    total_revenue DECIMAL(12,2) DEFAULT 0,
    total_discount DECIMAL(12,2) DEFAULT 0,
    avg_order_value DECIMAL(10,2),
    
    -- Cost metrics
    total_purchase_cost DECIMAL(12,2) DEFAULT 0,
    total_expense DECIMAL(12,2) DEFAULT 0,
    total_labor_cost DECIMAL(12,2) DEFAULT 0,
    
    -- Production metrics
    total_production_kg DECIMAL(10,2) DEFAULT 0,
    production_cost DECIMAL(12,2) DEFAULT 0,
    
    -- Calculated metrics
    gross_profit DECIMAL(12,2),
    gross_margin_pct DECIMAL(5,2),
    net_profit DECIMAL(12,2),
    net_margin_pct DECIMAL(5,2),
    
    -- Operational metrics
    employee_count INT,
    labor_cost_pct DECIMAL(5,2),
    food_cost_pct DECIMAL(5,2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(branch_id, summary_date)
);

CREATE TABLE ai_prediction (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    prediction_date DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- 'sales', 'orders', 'production', 'purchase'
    predicted_value DECIMAL(12,2) NOT NULL,
    actual_value DECIMAL(12,2),
    confidence_score DECIMAL(5,2),
    accuracy_score DECIMAL(5,2), -- Calculated after actual
    model_version VARCHAR(20),
    features_used JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ai_alert (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id UUID REFERENCES branch(id),
    alert_type VARCHAR(50) NOT NULL, -- 'anomaly', 'threshold', 'prediction', 'recommendation'
    severity VARCHAR(20) NOT NULL, -- 'info', 'warning', 'critical'
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    metric_name VARCHAR(50),
    metric_value DECIMAL(12,2),
    threshold_value DECIMAL(12,2),
    recommendation TEXT,
    is_read BOOLEAN DEFAULT false,
    is_dismissed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX idx_sales_order_branch_date ON sales_order(branch_id, created_at);
CREATE INDEX idx_sales_order_channel ON sales_order(channel_id);
CREATE INDEX idx_purchase_order_branch_date ON purchase_order(branch_id, order_date);
CREATE INDEX idx_expense_branch_date ON expense(branch_id, expense_date);
CREATE INDEX idx_production_branch_date ON production_batch(branch_id, production_date);
CREATE INDEX idx_attendance_employee_date ON employee_attendance(employee_id, attendance_date);
CREATE INDEX idx_daily_summary_branch_date ON daily_summary(branch_id, summary_date);
CREATE INDEX idx_audit_log_branch_entity ON audit_log(branch_id, entity_type, created_at);
```

---

## 6. ÖZELLİK SPESİFİKASYONLARI

### 6.1 Modül Haritası

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MODÜL HARİTASI                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    🏠 ANA DASHBOARD                              │    │
│  │  Real-time metrics, AI insights, alerts, quick actions          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │  💰 SATIŞ   │ │  📦 STOK    │ │  👥 PERSONEL│ │  💵 FİNANS  │       │
│  │             │ │             │ │             │ │             │       │
│  │ • POS       │ │ • Envanter  │ │ • Çalışanlar│ │ • Giderler  │       │
│  │ • Siparişler│ │ • Alımlar   │ │ • Puantaj   │ │ • Gelirler  │       │
│  │ • Kanallar  │ │ • Reçeteler │ │ • Maaş      │ │ • Kasa      │       │
│  │ • Raporlar  │ │ • Fire      │ │ • İzin      │ │ • Bilanço   │       │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │
│                                                                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │  🏭 ÜRETİM  │ │  📊 RAPORLAR│ │  🤖 AI      │ │  ⚙️ AYARLAR │       │
│  │             │ │             │ │             │ │             │       │
│  │ • Hamur     │ │ • Günlük    │ │ • Tahmin    │ │ • Şubeler   │       │
│  │ • Legen     │ │ • Haftalık  │ │ • Anomali   │ │ • Kullanıcı │       │
│  │ • Maliyet   │ │ • Aylık     │ │ • Öneriler  │ │ • Yetkiler  │       │
│  │ • Verimlilik│ │ • Karşılaş. │ │ • Trendler  │ │ • Bildirim  │       │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Modül Detayları

#### 6.2.1 Ana Dashboard

```yaml
Amaç: Tek bakışta tüm kritik metrikleri görmek

Bileşenler:
  Header:
    - Şube seçici (multi-branch için)
    - Tarih aralığı seçici
    - Bildirim ikonu (badge ile)
    - Kullanıcı menüsü
  
  KPI Kartları (4'lü grid):
    - Günlük Ciro (trend ile)
    - Günlük Sipariş (salon/paket breakdown)
    - Günlük Kar/Zarar
    - Aktif Personel
  
  Ana Grafikler:
    - Saatlik Satış Dağılımı (line chart)
    - Son 7 Gün Trend (area chart)
    - Kanal Bazlı Dağılım (donut chart)
    - Ürün Kategori Performans (bar chart)
  
  AI Insights Panel:
    - "Bugün satış tahmini: 1,250 sipariş"
    - "Dikkat: Marul stoğu 2 güne bitecek"
    - "Öneri: Cuma günü +2 personel planla"
  
  Quick Actions:
    - Yeni Sipariş
    - Mal Alımı Ekle
    - Kasa Kapat
    - Günü Kapat
  
  Canlı Feed:
    - Son 10 sipariş (real-time)
    - Son uyarılar
    - Sistem bildirimleri
```

#### 6.2.2 Satış Modülü

```yaml
POS Ekranı (Kasiyer İçin):
  Layout: Full-screen, touch-optimized
  
  Sol Panel (70%):
    - Kategori sekmeler (yatay scroll)
    - Ürün grid'i (büyük butonlar, resimli)
    - Ürüne tıkla → sepete ekle
    - Quantity selector (+/- butonlar)
  
  Sağ Panel (30%):
    - Aktif sepet
    - Sipariş tipi: Salon / Paket / Online
    - Masa numarası (salon için)
    - Müşteri bilgisi (paket için)
    - Ara toplam / KDV / İndirim / Toplam
    - Ödeme butonları: Nakit / Kart / Karışık
    - Notu ekle butonu
  
  Keyboard Shortcuts:
    - F1: Nakit ödeme
    - F2: Kart ödeme
    - F3: Sepeti temizle
    - Enter: Siparişi tamamla

Sipariş Listesi:
  Filtreler:
    - Tarih aralığı
    - Sipariş tipi
    - Kanal
    - Durum
    - Arama (sipariş no, müşteri)
  
  Tablo Kolonları:
    - Sipariş No
    - Saat
    - Tip
    - Kanal
    - Tutar
    - Ödeme
    - Durum
    - Aksiyonlar
  
  Detay Modal:
    - Sipariş özeti
    - Ürün listesi
    - Ödeme detayı
    - İptal/İade butonu

Kanal Yönetimi:
  - Platform listesi (Trendyol, Getir, etc.)
  - Komisyon oranları
  - Fatura takibi
  - Aylık özet
```

#### 6.2.3 Stok & Satın Alma Modülü

```yaml
Envanter Dashboard:
  Özet Kartlar:
    - Toplam Stok Değeri
    - Kritik Stok Uyarısı (kaç ürün)
    - Bu Hafta Kullanım
    - Tahmini Fire Oranı
  
  Stok Tablosu:
    - Malzeme adı
    - Kategori
    - Mevcut Stok
    - Min Stok
    - Durum (OK/Düşük/Kritik)
    - Son Alım Tarihi
    - Birim Maliyet
    - Toplam Değer
  
  Filtreler:
    - Kategori
    - Durum
    - Tedarikçi
  
  Actions:
    - Sayım Gir
    - Fire Kaydet
    - Transfer (şubeler arası)

Mal Alımı (Purchase Order):
  Hızlı Giriş Formu:
    - Tedarikçi seç (autocomplete)
    - Tarih (default: bugün)
    - Ürün ekle (çoklu):
      - Malzeme seç (autocomplete)
      - Miktar
      - Birim
      - Birim Fiyat
      - Toplam (auto-calc)
    - Toplam tutar
    - Ödeme durumu
    - Kaydet
  
  AI Asistan:
    - "Geçen hafta aynı gün 50kg marul aldınız"
    - "Fiyat %15 arttı, alternatif tedarikçi önerisi"
  
  Alım Geçmişi:
    - Tarih bazlı liste
    - Tedarikçi bazlı agregasyon
    - Ürün bazlı trend

Reçete Yönetimi:
  - Ürün bazlı reçete tanımlama
  - Malzeme ve miktarlar
  - Maliyet hesaplama (otomatik)
  - Fire oranı ekleme
  - Yield (çıktı) tanımlama
```

#### 6.2.4 Üretim Modülü

```yaml
Günlük Üretim Girişi:
  Form:
    - Tarih
    - Üretim Tipi (Çiğ köfte hamuru, Lavaş, etc.)
    - Toplam Üretim (kg)
    - Legen/Tepsi Sayısı
    - Legen başı kg (auto-calc veya manual)
    - Kalite notu (1-5)
    - Açıklama
  
  Malzeme Kullanımı (auto-populated from recipe):
    - Bulgur: X kg
    - İsot: X kg
    - Nar ekşisi: X lt
    - ... (düzenlenebilir)
  
  Maliyet Özeti:
    - Toplam Malzeme Maliyeti
    - Kg Başı Maliyet
    - Önceki dönem karşılaştırma

Üretim Raporları:
  - Günlük/haftalık/aylık üretim trendi
  - Maliyet trendi
  - Verimlilik analizi
  - Fire oranı takibi
```

#### 6.2.5 Personel Modülü

```yaml
Çalışan Listesi:
  Tablo:
    - Ad Soyad
    - Pozisyon
    - Tip (Full/Part-time)
    - Maaş
    - Giriş Tarihi
    - Durum
  
  Çalışan Kartı (detay):
    - Kişisel bilgiler
    - İletişim
    - Banka bilgileri
    - SGK bilgileri
    - Çalışma geçmişi
    - Performans notları

Puantaj (Attendance):
  Takvim Görünümü:
    - Ay takvimi
    - Renk kodlu günler (geldi/gelmedi/izinli/hasta)
    - Tıkla → giriş-çıkış saati
  
  Liste Görünümü:
    - Tarih seçici
    - Tüm personel listesi
    - Saat gir/düzenle
    - Mesai hesaplama (otomatik)
    - Yemek verildi checkbox
  
  Toplu Giriş:
    - Vardiya seç
    - Personel seç (çoklu)
    - Saat uygula
    - Kaydet

Maaş Hesaplama:
  Aylık Bordro:
    - Personel seç
    - Dönem seç (ay/yıl)
    - Otomatik hesaplama:
      - Baz maaş
      - Mesai ücreti
      - SGK işçi
      - SGK işveren
      - Vergi kesintisi
      - Avans düşümü
      - Net ödeme
    - Onay workflow
    - Excel export
```

#### 6.2.6 Finans Modülü

```yaml
Gider Girişi:
  Hızlı Form:
    - Kategori seç (hiyerarşik dropdown)
    - Alt kategori
    - Tarih
    - Tutar
    - KDV
    - Açıklama
    - Ödeme yöntemi
    - Fiş/fatura yükle (resim)
  
  Gider Kategorileri (predefined):
    ├── Kira
    │   ├── Dükkan Kirası
    │   ├── Depo Kirası
    │   └── Personel Evi
    ├── Faturalar
    │   ├── Elektrik
    │   ├── Su
    │   ├── Gaz
    │   └── İnternet/Telefon
    ├── Araç Giderleri
    │   ├── Yakıt
    │   └── Bakım
    ├── Personel
    │   └── Yemek
    └── Diğer

Kasa Yönetimi:
  Kasa Açılış:
    - Başlangıç tutarı gir
    - Açılış saati (auto)
    - Açan kişi (auto)
  
  Kasa Kapanış:
    - Beklenen tutar (auto-calc)
    - Sayılan tutar (gir)
    - Fark (auto-calc, highlight if ≠0)
    - Açıklama (fark varsa zorunlu)
    - Kapat butonu

Bilanço/P&L:
  Özet Görünüm:
    - Dönem seçici
    - GELİRLER
      - Satışlar (kanal bazlı)
      - Diğer gelirler
    - GİDERLER
      - Mal alımları
      - Personel
      - Kira
      - Faturalar
      - Diğer
    - BRÜT KAR
    - NET KAR
    - Kar marjı %
  
  Karşılaştırmalı:
    - Bu ay vs geçen ay
    - Bu yıl vs geçen yıl
    - Şubeler arası
```

#### 6.2.7 Raporlama Modülü

```yaml
Standart Raporlar:
  Günlük:
    - Satış özeti
    - Sipariş detayı
    - Kasa raporu
    - Üretim raporu
  
  Haftalık:
    - Trend analizi
    - Personel performans
    - Stok hareket
  
  Aylık:
    - P&L statement
    - Kategori bazlı analiz
    - Karşılaştırmalı performans
  
  Özel:
    - Tarih aralığı seç
    - Metrik seç
    - Grupla (gün/hafta/ay)
    - Export (Excel/PDF)

Dashboard Builder (Advanced):
  - Drag & drop widgets
  - Custom date ranges
  - Save as template
  - Share/schedule
```

#### 6.2.8 AI Modülü

```yaml
Talep Tahmini:
  - Günlük sipariş tahmini
  - Ürün bazlı tahmin
  - Hava durumu korelasyonu
  - Özel gün faktörü (bayram, hafta sonu)
  
Maliyet Optimizasyonu:
  - Tedarikçi fiyat karşılaştırma
  - Optimal sipariş miktarı
  - Fire azaltma önerileri
  
Anomali Tespiti:
  - Beklenmedik maliyet artışı
  - Stok tutarsızlığı
  - Kasa farkları pattern
  
Akıllı Uyarılar:
  - Stok minimum seviye
  - Bütçe aşımı
  - Performans düşüşü
  - Trend değişimi
```

---

## 7. EKRAN TASARIMLARI

### 7.1 Wireframe Spesifikasyonları

#### Ana Dashboard Wireframe

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🥙 ÇİĞ KÖFTE YÖNETİM          [Kadıköy ▼]  [📅 Bugün ▼]  🔔(3)  👤 Okan │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ 💰 GÜNLÜK    │ │ 📦 SİPARİŞ  │ │ 📈 NET KAR  │ │ 👥 PERSONEL  │    │
│  │    CİRO      │ │    SAYISI    │ │             │ │              │    │
│  │              │ │              │ │             │ │              │    │
│  │  ₺45,230     │ │    1,247     │ │  ₺12,450   │ │    14/17     │    │
│  │  ▲ +8%       │ │  🏠1220 📦27│ │  ▲ +12%    │ │   aktif      │    │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                                          │
│  ┌──────────────────────────────────────┐ ┌─────────────────────────┐   │
│  │        SAATLİK SATIŞ TRENDİ          │ │    KANAL DAĞILIMI       │   │
│  │                                       │ │                         │   │
│  │     ╭─────╮                          │ │      ┌────────┐         │   │
│  │    ╱       ╲         ╭───            │ │     /  Salon   \        │   │
│  │   ╱         ╲       ╱                │ │    │    78%     │       │   │
│  │  ╱           ╲─────╱                 │ │     \  Paket   /        │   │
│  │ ╱                                    │ │      └────────┘         │   │
│  │ 08  10  12  14  16  18  20  22      │ │  ■ Trendyol 12%         │   │
│  │                                       │ │  ■ Getir 8%            │   │
│  └──────────────────────────────────────┘ │  ■ Diğer 2%            │   │
│                                           └─────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ 🤖 AI INSIGHTS                                                   │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │ ⚠️ Stok Uyarısı: Marul stoğu 2 güne yetecek seviyede            │    │
│  │ 📊 Tahmin: Yarın ~1,350 sipariş bekleniyor (Cuma etkisi)        │    │
│  │ 💡 Öneri: Bu hafta sonu için +2 part-time personel planla       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌───────────────────────────┐ ┌───────────────────────────────────┐    │
│  │ ⚡ HIZLI İŞLEMLER         │ │ 📋 SON SİPARİŞLER                 │    │
│  ├───────────────────────────┤ ├───────────────────────────────────┤    │
│  │                           │ │ #1247 🏠 14:32  ₺125  ✓ Tamamlandı│    │
│  │  [➕ Yeni Sipariş]        │ │ #1246 📦 14:30  ₺89   🔄 Hazırlık │    │
│  │                           │ │ #1245 🏠 14:28  ₺156  ✓ Tamamlandı│    │
│  │  [📦 Mal Alımı]           │ │ #1244 📦 14:25  ₺234  ✓ Tamamlandı│    │
│  │                           │ │ #1243 🏠 14:22  ₺67   ✓ Tamamlandı│    │
│  │  [💵 Kasa Kapat]          │ │                                   │    │
│  │                           │ │         [Tümünü Gör →]            │    │
│  └───────────────────────────┘ └───────────────────────────────────┘    │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│ 🏠 Dashboard │ 💰 Satış │ 📦 Stok │ 👥 Personel │ 💵 Finans │ ⚙️ Ayar │
└─────────────────────────────────────────────────────────────────────────┘
```

#### POS Ekranı (Kasiyer) Wireframe

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🥙 POS - Kadıköy                                          🕐 14:35  👤 │
├────────────────────────────────────────────────────┬────────────────────┤
│                                                    │                    │
│  [Çiğ Köfte] [İçecek] [Sos/Ek] [Tatlı] [Paket]    │  📋 SEPET          │
│                                                    │                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │  ┌──────────────┐  │
│  │  🥙     │ │  🥙     │ │  🥙     │ │  🥙     │  │  │ 2x Dürüm     │  │
│  │         │ │         │ │         │ │         │  │  │    ₺90       │  │
│  │ Dürüm   │ │ Porsiyon│ │ Tombik  │ │ Çocuk   │  │  │  [-] [+]  🗑 │  │
│  │  ₺45    │ │  ₺35    │ │  ₺55    │ │  ₺25    │  │  ├──────────────┤  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │  │ 1x Ayran     │  │
│                                                    │  │    ₺15       │  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │  │  [-] [+]  🗑 │  │
│  │  🥙     │ │  🥙     │ │  🥙     │ │  🥙     │  │  └──────────────┘  │
│  │         │ │         │ │         │ │         │  │                    │
│  │ Tam     │ │ Yarım   │ │ Aile    │ │ Lavaş   │  │  ────────────────  │
│  │  ₺120   │ │  ₺70    │ │  ₺180   │ │  ₺5     │  │  Ara Toplam: ₺105 │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │  KDV (%10):   ₺10  │
│                                                    │  ────────────────  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │  TOPLAM:    ₺115  │
│  │  🍹     │ │  🍹     │ │  🍹     │ │  🍹     │  │                    │
│  │         │ │         │ │         │ │         │  │  ┌──────────────┐  │
│  │ Ayran   │ │ Kola    │ │ Şalgam  │ │ Su      │  │  │ 🏠 SALON     │  │
│  │  ₺15    │ │  ₺20    │ │  ₺18    │ │  ₺8     │  │  │ Masa: [___]  │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │  └──────────────┘  │
│                                                    │  ┌──────────────┐  │
│                                                    │  │ 📦 PAKET     │  │
│                                                    │  │ Tel: [______]│  │
│                                                    │  └──────────────┘  │
│                                                    │                    │
│                                                    │  ┌──────┐ ┌──────┐│
│                                                    │  │💵NAKÎT│ │💳KART││
│                                                    │  │ (F1) │ │ (F2) ││
│                                                    │  └──────┘ └──────┘│
│                                                    │                    │
│                                                    │  [🗑 Temizle (F3)]│
└────────────────────────────────────────────────────┴────────────────────┘
```

#### Mal Alımı Formu Wireframe

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 📦 MAL ALIMI GİRİŞİ                                          ← Geri    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Tedarikçi: [Çınar Lavaş_________________ ▼]    Tarih: [16.12.2025 📅]  │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ ÜRÜNLER                                                [+ Ekle] │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                  │    │
│  │  Malzeme              Miktar    Birim    Birim Fiyat   Toplam   │    │
│  │  ─────────────────────────────────────────────────────────────  │    │
│  │  [Lavaş_________▼]   [550___]  [adet▼]  [₺6.36____]   ₺3,498   │    │
│  │                                                          [🗑]   │    │
│  │  ─────────────────────────────────────────────────────────────  │    │
│  │  [Ayran_________▼]   [25____]  [koli▼]  [₺130.17__]   ₺3,254   │    │
│  │                                                          [🗑]   │    │
│  │  ─────────────────────────────────────────────────────────────  │    │
│  │  [_______________]   [______]  [____▼]  [₺________]            │    │
│  │                                                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ 🤖 AI Asistan                                                    │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │ 💡 Geçen hafta aynı gün 600 adet lavaş almıştınız               │    │
│  │ ⚠️ Ayran fiyatı %5 artmış (geçen ay: ₺124)                      │    │
│  │ 📊 Stok durumu: Lavaş 2 günlük, Ayran 4 günlük                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌────────────────────────────────────┐                                 │
│  │ ÖZET                               │                                 │
│  │                                    │                                 │
│  │ Ara Toplam:           ₺6,752      │                                 │
│  │ KDV (%10):              ₺675      │                                 │
│  │ ─────────────────────────────     │                                 │
│  │ TOPLAM:               ₺7,427      │                                 │
│  │                                    │                                 │
│  │ Ödeme: [⚪ Peşin] [🔘 Vadeli]      │                                 │
│  └────────────────────────────────────┘                                 │
│                                                                          │
│  [Fiş Fotoğrafı Yükle 📷]                                               │
│                                                                          │
│                              [İptal]  [💾 Kaydet]                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 8. METRİKLER & KPI'LAR

### 8.1 Operasyonel Metrikler

```yaml
Satış Metrikleri:
  Temel:
    - Günlük/Haftalık/Aylık Ciro
    - Sipariş Sayısı
    - Ortalama Sipariş Tutarı (Average Order Value - AOV)
    - Sepet Büyüklüğü (Items per Order)
  
  Kanal Bazlı:
    - Salon Satışları (adet, tutar, %)
    - Paket Satışları (adet, tutar, %)
    - Online Platform Satışları (Trendyol, Getir, etc.)
    - Kanal Başı Komisyon Maliyeti
  
  Zaman Bazlı:
    - Saatlik Dağılım (peak hours)
    - Gün bazlı dağılım (en yoğun günler)
    - Mevsimsel trend
  
  Ürün Bazlı:
    - En Çok Satan Top 10 Ürün
    - Ürün Kategori Dağılımı
    - Ürün Başı Kar Marjı
    - Çapraz Satış Oranı (combo ürünler)

Maliyet Metrikleri:
  Food Cost:
    - COGS (Cost of Goods Sold)
    - Food Cost % = (Mal Alımı / Ciro) × 100
    - Target: < %30
  
  Labor Cost:
    - Toplam Personel Maliyeti
    - Labor Cost % = (Personel / Ciro) × 100
    - Target: < %25
    - Saatlik İşgücü Maliyeti
    - Sipariş Başı İşgücü Maliyeti
  
  Overhead:
    - Sabit Giderler (kira, sigorta, etc.)
    - Değişken Giderler (enerji, sarf)
    - Overhead % = (Genel Gider / Ciro) × 100

Karlılık Metrikleri:
  - Brüt Kar = Ciro - COGS
  - Brüt Kar Marjı % = (Brüt Kar / Ciro) × 100
  - Faaliyet Karı = Brüt Kar - İşletme Giderleri
  - Net Kar = Faaliyet Karı - Diğer Giderler
  - Net Kar Marjı % = (Net Kar / Ciro) × 100
  - Target Net Margin: > %10
```

### 8.2 Verimlilik Metrikleri

```yaml
Üretim Verimliliği:
  - Günlük Üretim (kg)
  - Kg Başı Maliyet
  - Fire Oranı % = (Fire / Üretim) × 100
  - Legen Başı Maliyet
  - Yield Rate (Reçete vs Gerçek)

Personel Verimliliği:
  - Sipariş/Personel/Saat
  - Ciro/Personel/Saat
  - Mesai Saati Oranı
  - Devamsızlık Oranı
  - Turnover Rate

Stok Verimliliği:
  - Stok Devir Hızı = COGS / Ortalama Stok
  - Günlük Stok Değeri
  - Dead Stock (Ölü stok) %
  - Stockout Frequency (Stok tükenmesi sıklığı)

Operasyonel Verimlilik:
  - Average Service Time
  - Order Accuracy Rate
  - Customer Wait Time
  - Table Turnover Rate
```

### 8.3 AI-Powered Metrikler

```yaml
Tahmin Metrikleri:
  - Predicted vs Actual Sales
  - Forecast Accuracy %
  - Demand Prediction Error

Anomali Metrikleri:
  - Unusual Expense Alert
  - Inventory Discrepancy
  - Cash Register Variance
  - Price Anomaly Detection

Trend Metrikleri:
  - Week-over-Week Growth
  - Month-over-Month Growth
  - Seasonal Index
  - Trend Direction Indicator

Benchmark Metrikleri:
  - Same Store Sales Growth
  - Branch Comparison Index
  - Industry Benchmark Delta
```

### 8.4 KPI Dashboard Konfigürasyonu

```yaml
Executive Dashboard (Patron):
  Primary KPIs:
    - Günlük Net Kar (trend ile)
    - Food Cost %
    - Labor Cost %
    - Customer Count
  
  Secondary KPIs:
    - AOV
    - Kanal Mix
    - Stok Günü
    - Personel Puanı

Manager Dashboard:
  Primary KPIs:
    - Saatlik Satış
    - Stok Uyarıları
    - Personel Devam
    - Kasa Durumu
  
  Secondary KPIs:
    - Sipariş Durumları
    - Üretim Takibi
    - Bekleyen Ödemeler

Cashier Dashboard:
  Primary KPIs:
    - Bugünkü Sipariş Sayısı
    - Kasa Toplamı
    - Bekleyen Siparişler
```

---

## 9. AI ÖZELLİKLERİ

### 9.1 AI Modülleri

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI MODULE ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    DEMAND FORECASTING ENGINE                     │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                  │    │
│  │  Inputs:                      Model:           Outputs:          │    │
│  │  ┌──────────────┐            ┌──────────┐    ┌──────────────┐   │    │
│  │  │ Historical   │            │          │    │ Daily Order  │   │    │
│  │  │ Sales Data   │──────────▶│  LSTM +  │───▶│ Prediction   │   │    │
│  │  │              │            │ XGBoost  │    │              │   │    │
│  │  │ Calendar     │──────────▶│ Ensemble │───▶│ Product Mix  │   │    │
│  │  │ (holidays)   │            │          │    │ Forecast     │   │    │
│  │  │              │            └──────────┘    │              │   │    │
│  │  │ Weather API  │─────────────────────────▶│ Confidence   │   │    │
│  │  │              │                           │ Score        │   │    │
│  │  │ Local Events │                           └──────────────┘   │    │
│  │  └──────────────┘                                               │    │
│  │                                                                  │    │
│  │  Accuracy Target: > 85% (±10% variance)                         │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    ANOMALY DETECTION ENGINE                      │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                  │    │
│  │  Detection Types:                                                │    │
│  │                                                                  │    │
│  │  📊 Statistical Anomaly:                                         │    │
│  │     - Z-score > 3 standard deviations                           │    │
│  │     - Moving average deviation                                   │    │
│  │     - Seasonal decomposition outliers                           │    │
│  │                                                                  │    │
│  │  🔍 Pattern Anomaly:                                             │    │
│  │     - Unusual transaction patterns                               │    │
│  │     - Inventory shrinkage patterns                               │    │
│  │     - Employee behavior anomalies                                │    │
│  │                                                                  │    │
│  │  💰 Financial Anomaly:                                           │    │
│  │     - Price manipulation                                         │    │
│  │     - Discount abuse                                             │    │
│  │     - Cash register discrepancies                                │    │
│  │                                                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    RECOMMENDATION ENGINE                         │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │                                                                  │    │
│  │  📦 Inventory Recommendations:                                   │    │
│  │     - Optimal reorder points                                     │    │
│  │     - Economic order quantity                                    │    │
│  │     - Supplier comparison & switching                           │    │
│  │                                                                  │    │
│  │  👥 Staffing Recommendations:                                    │    │
│  │     - Shift optimization                                         │    │
│  │     - Peak hour staffing                                         │    │
│  │     - Overtime prediction & avoidance                           │    │
│  │                                                                  │    │
│  │  💡 Operational Recommendations:                                 │    │
│  │     - Menu optimization                                          │    │
│  │     - Price adjustment suggestions                               │    │
│  │     - Waste reduction strategies                                 │    │
│  │                                                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 9.2 AI Alert System

```yaml
Alert Categories:
  
  Critical (🔴):
    - Stok bitme noktasında (< 1 gün)
    - Kasa farkı > ₺500
    - Sistemsel anomali tespit
    - Bütçe aşımı > %20
    
    Action: Immediate notification (push, SMS)
  
  Warning (🟡):
    - Stok düşük (< 3 gün)
    - Maliyet trendi yukarı
    - Performans düşüşü
    - Tahmin sapması > %15
    
    Action: Dashboard highlight + notification
  
  Info (🔵):
    - Yeni trend tespit
    - Optimizasyon fırsatı
    - Benchmark karşılaştırma
    - Weekly digest
    
    Action: Dashboard widget + email digest

Alert Examples:
  - "⚠️ Marul stoğu 2 güne yetecek. Tedarikçiden sipariş önerilir."
  - "📊 Cuma günleri %35 daha yoğun. Bu hafta +2 personel önerilir."
  - "💰 Lavaş fiyatı %8 arttı. Alternatif tedarikçi: X (₺5.90/adet)"
  - "🎯 Geçen aydan %12 daha az fire. Tebrikler!"
  - "⏰ Öğle 12-14 arası en yoğun. Hazırlık buna göre planlanabilir."
```

### 9.3 AI Implementation Roadmap

```yaml
Phase 1 (MVP):
  - Rule-based alerts (stok minimum, bütçe limit)
  - Simple moving averages for trends
  - Basic anomaly detection (threshold-based)

Phase 2 (v1.1):
  - Time series forecasting (ARIMA/Prophet)
  - Pattern-based anomaly detection
  - Supplier price comparison

Phase 3 (v2.0):
  - ML-based demand forecasting
  - Staffing optimization
  - Menu profitability analysis

Phase 4 (Enterprise):
  - Real-time ML inference
  - Multi-branch pattern learning
  - Natural language insights
  - Predictive maintenance
```

---

## 10. ROL BAZLI ERİŞİM KONTROLÜ

### 10.1 Rol Tanımları

```yaml
Roller:
  
  OWNER (İşletme Sahibi):
    Açıklama: Tüm yetkilere sahip, sistem admini
    Yetkiler:
      - Tüm modüllere tam erişim
      - Kullanıcı yönetimi
      - Şube yönetimi
      - Finansal veriler
      - AI insights
      - Sistem ayarları
  
  MANAGER (Şube Müdürü):
    Açıklama: Şube bazlı tam yetki
    Yetkiler:
      - Satış yönetimi
      - Stok yönetimi
      - Personel puantaj
      - Gider girişi
      - Raporlar (şube bazlı)
      - Kasa yönetimi
    Kısıtlamalar:
      - Maaş detaylarını göremez
      - Diğer şube verilerine erişemez
      - Sistem ayarlarını değiştiremez
  
  CASHIER (Kasiyer):
    Açıklama: POS ve temel işlemler
    Yetkiler:
      - POS kullanımı
      - Sipariş oluşturma
      - Kasa açılış/kapanış
      - Stok görüntüleme
    Kısıtlamalar:
      - Fiyat değiştiremez
      - Rapor göremez
      - Personel bilgilerine erişemez
  
  KITCHEN (Mutfak):
    Açıklama: Üretim ve sipariş takibi
    Yetkiler:
      - Sipariş listesi görme
      - Üretim girişi
      - Stok kullanım kaydı
    Kısıtlamalar:
      - Finansal verilere erişemez
      - Satış yapamaz
  
  REGIONAL_MANAGER (Bölge Müdürü):
    Açıklama: Çoklu şube yönetimi
    Yetkiler:
      - Atanmış şubelere erişim
      - Karşılaştırmalı raporlar
      - Performans takibi
    Kısıtlamalar:
      - Atanmamış şubelere erişemez
      - Sistem ayarlarını değiştiremez
```

### 10.2 İzin Matrisi

```
┌─────────────────────┬───────┬─────────┬─────────┬─────────┬─────────┐
│ Modül / İşlem       │ OWNER │ MANAGER │ CASHIER │ KITCHEN │ REGIONAL│
├─────────────────────┼───────┼─────────┼─────────┼─────────┼─────────┤
│ Dashboard           │  ✅   │   ✅    │   ⚠️    │   ❌    │   ✅    │
│ - Tüm metrikler     │  ✅   │   ✅    │   ❌    │   ❌    │   ✅    │
│ - Basit metrikler   │  ✅   │   ✅    │   ✅    │   ❌    │   ✅    │
├─────────────────────┼───────┼─────────┼─────────┼─────────┼─────────┤
│ Satış               │       │         │         │         │         │
│ - POS kullanım      │  ✅   │   ✅    │   ✅    │   ❌    │   ❌    │
│ - Sipariş iptal     │  ✅   │   ✅    │   ⚠️    │   ❌    │   ❌    │
│ - Fiyat değiştirme  │  ✅   │   ⚠️    │   ❌    │   ❌    │   ❌    │
│ - İndirim uygulama  │  ✅   │   ✅    │   ⚠️    │   ❌    │   ❌    │
├─────────────────────┼───────┼─────────┼─────────┼─────────┼─────────┤
│ Stok                │       │         │         │         │         │
│ - Görüntüleme       │  ✅   │   ✅    │   ✅    │   ✅    │   ✅    │
│ - Mal alımı girişi  │  ✅   │   ✅    │   ❌    │   ❌    │   ❌    │
│ - Stok düzeltme     │  ✅   │   ✅    │   ❌    │   ❌    │   ❌    │
│ - Reçete düzenleme  │  ✅   │   ⚠️    │   ❌    │   ❌    │   ❌    │
├─────────────────────┼───────┼─────────┼─────────┼─────────┼─────────┤
│ Üretim              │       │         │         │         │         │
│ - Üretim girişi     │  ✅   │   ✅    │   ❌    │   ✅    │   ❌    │
│ - Maliyet görme     │  ✅   │   ✅    │   ❌    │   ❌    │   ✅    │
├─────────────────────┼───────┼─────────┼─────────┼─────────┼─────────┤
│ Personel            │       │         │         │         │         │
│ - Puantaj girişi    │  ✅   │   ✅    │   ❌    │   ❌    │   ❌    │
│ - Maaş görme        │  ✅   │   ❌    │   ❌    │   ❌    │   ⚠️    │
│ - Çalışan ekleme    │  ✅   │   ⚠️    │   ❌    │   ❌    │   ❌    │
├─────────────────────┼───────┼─────────┼─────────┼─────────┼─────────┤
│ Finans              │       │         │         │         │         │
│ - Gider girişi      │  ✅   │   ✅    │   ❌    │   ❌    │   ❌    │
│ - Kasa yönetimi     │  ✅   │   ✅    │   ✅    │   ❌    │   ❌    │
│ - P&L raporu        │  ✅   │   ⚠️    │   ❌    │   ❌    │   ✅    │
├─────────────────────┼───────┼─────────┼─────────┼─────────┼─────────┤
│ Raporlar            │       │         │         │         │         │
│ - Günlük rapor      │  ✅   │   ✅    │   ⚠️    │   ❌    │   ✅    │
│ - Detaylı analiz    │  ✅   │   ✅    │   ❌    │   ❌    │   ✅    │
│ - Export (Excel)    │  ✅   │   ✅    │   ❌    │   ❌    │   ✅    │
├─────────────────────┼───────┼─────────┼─────────┼─────────┼─────────┤
│ Ayarlar             │       │         │         │         │         │
│ - Şube ayarları     │  ✅   │   ⚠️    │   ❌    │   ❌    │   ❌    │
│ - Kullanıcı yönetim │  ✅   │   ❌    │   ❌    │   ❌    │   ❌    │
│ - Sistem ayarları   │  ✅   │   ❌    │   ❌    │   ❌    │   ❌    │
├─────────────────────┼───────┼─────────┼─────────┼─────────┼─────────┤
│ AI Insights         │  ✅   │   ✅    │   ❌    │   ❌    │   ✅    │
└─────────────────────┴───────┴─────────┴─────────┴─────────┴─────────┘

Açıklama:
✅ = Tam yetki
⚠️ = Kısıtlı yetki (onay gerekebilir veya limit var)
❌ = Erişim yok
```

---

## 11. UI/UX TASARIM SİSTEMİ

### 11.1 Design Philosophy

```yaml
Aesthetic Direction: "Modern Industrial Kitchen"
  
  Tone: Professional yet warm, efficient yet approachable
  
  Key Principles:
    - Clean & Functional: No unnecessary decoration
    - Touch-First: Large tap targets for POS
    - Data-Dense: Maximize information without clutter
    - Speed: < 100ms interactions
  
  Visual Identity:
    - Bold typography for key numbers
    - Subtle textures for depth
    - Color-coded categories
    - Generous whitespace

Differentiation:
    - Not another generic dashboard
    - Restaurant-specific visual language
    - Turkish cultural touches
    - Chef/kitchen metaphors
```

### 11.2 Color System

```yaml
Primary Palette:
  Brand Red: #C41E3A     # Çiğ köfte kırmızısı
  Brand Dark: #1A1A2E    # Deep navy
  Brand Warm: #F5E6D3    # Warm cream

Semantic Colors:
  Success: #10B981       # Emerald green
  Warning: #F59E0B       # Amber
  Danger: #EF4444        # Red
  Info: #3B82F6          # Blue

Neutral Scale:
  Gray-50: #FAFAFA
  Gray-100: #F4F4F5
  Gray-200: #E4E4E7
  Gray-300: #D4D4D8
  Gray-400: #A1A1AA
  Gray-500: #71717A
  Gray-600: #52525B
  Gray-700: #3F3F46
  Gray-800: #27272A
  Gray-900: #18181B

Data Visualization:
  Chart-1: #C41E3A       # Primary
  Chart-2: #3B82F6       # Blue
  Chart-3: #10B981       # Green
  Chart-4: #F59E0B       # Yellow
  Chart-5: #8B5CF6       # Purple
  Chart-6: #EC4899       # Pink
```

### 11.3 Typography

```yaml
Font Stack:
  Headings: "Plus Jakarta Sans", sans-serif
    - Bold, clean, modern
    - Excellent number rendering
  
  Body: "Inter", sans-serif
    - Highly legible
    - Good for dense data
  
  Mono: "JetBrains Mono", monospace
    - For numbers, codes
    - Tabular figures

Type Scale:
  Display: 48px / 56px / Bold
  H1: 36px / 44px / Bold
  H2: 30px / 38px / Semibold
  H3: 24px / 32px / Semibold
  H4: 20px / 28px / Medium
  Body Large: 18px / 28px / Regular
  Body: 16px / 24px / Regular
  Body Small: 14px / 20px / Regular
  Caption: 12px / 16px / Medium

Number Formatting:
  Currency: ₺1,234.56 (Bold, slightly larger)
  Percentage: 12.5% (with trend indicator)
  Count: 1,234 (with unit label)
```

### 11.4 Component Library

```yaml
Buttons:
  Primary:
    - Background: Brand Red
    - Text: White
    - Hover: Darken 10%
    - Active: Darken 20%
    - Size: 44px height (touch-friendly)
  
  Secondary:
    - Background: Gray-100
    - Text: Gray-700
    - Border: Gray-300
  
  Ghost:
    - Background: Transparent
    - Text: Gray-600
    - Hover: Gray-100

Cards:
  Default:
    - Background: White
    - Border: 1px Gray-200
    - Border-radius: 12px
    - Shadow: sm (subtle)
    - Padding: 24px
  
  KPI Card:
    - Accent border-left (4px, semantic color)
    - Icon with background circle
    - Large number + label
    - Trend indicator (↑↓)

Forms:
  Input:
    - Height: 44px
    - Border: 1px Gray-300
    - Border-radius: 8px
    - Focus: Brand Red border
    - Error: Danger border + message
  
  Select:
    - Same as input
    - Custom dropdown with search

Tables:
  Header:
    - Background: Gray-50
    - Text: Gray-600, uppercase, small
    - Sticky on scroll
  
  Row:
    - Border-bottom: 1px Gray-100
    - Hover: Gray-50
    - Clickable: cursor pointer

Charts:
  Style:
    - Clean, minimal grid
    - Rounded line caps
    - Subtle gradients for area
    - Interactive tooltips
```

### 11.5 Layout System

```yaml
Grid:
  Container: Max 1440px, centered
  Columns: 12-column grid
  Gutter: 24px
  Margins: 32px (desktop), 16px (mobile)

Spacing Scale:
  0: 0px
  1: 4px
  2: 8px
  3: 12px
  4: 16px
  5: 20px
  6: 24px
  8: 32px
  10: 40px
  12: 48px
  16: 64px

Breakpoints:
  sm: 640px
  md: 768px
  lg: 1024px
  xl: 1280px
  2xl: 1536px

Page Structure:
  ┌─────────────────────────────────────────┐
  │ Header (64px)                           │
  ├────────┬────────────────────────────────┤
  │        │                                │
  │ Side   │      Main Content              │
  │ Nav    │      (Scrollable)              │
  │(240px) │                                │
  │        │                                │
  │        │                                │
  ├────────┴────────────────────────────────┤
  │ Mobile Bottom Nav (visible < md)        │
  └─────────────────────────────────────────┘
```

### 11.6 Motion & Interaction

```yaml
Transitions:
  Default: 150ms ease-out
  Slow: 300ms ease-out
  Fast: 100ms ease-out

Micro-interactions:
  Button press: Scale 0.98
  Card hover: Translate Y -2px + shadow
  Toast enter: Slide in from right
  Modal: Fade + scale from 0.95
  Dropdown: Fade + translate Y

Loading States:
  Skeleton: Pulse animation (Gray-200 → Gray-100)
  Spinner: Brand Red, 24px
  Progress: Brand Red bar, smooth

Feedback:
  Success: Green toast + check icon
  Error: Red toast + shake
  Warning: Yellow toast
```

---

## 12. TEKNİK STACK

### 12.1 Önerilen Teknolojiler

```yaml
Frontend:
  Framework: Vue 3 (Composition API)
  State: Pinia
  Router: Vue Router 4
  UI Kit: Custom (Tailwind CSS based)
  Charts: Chart.js veya Apache ECharts
  Forms: VeeValidate + Zod
  HTTP: Axios
  Real-time: Socket.io client
  PWA: Vite PWA plugin
  
Backend:
  Framework: FastAPI (Python 3.11+)
  ORM: SQLAlchemy 2.0
  Validation: Pydantic v2
  Auth: JWT + OAuth2
  Task Queue: Celery + Redis
  Real-time: Socket.io (python-socketio)
  
Database:
  Primary: PostgreSQL 15+
  Cache: Redis 7+
  Time Series: TimescaleDB (PostgreSQL extension)
  Search: PostgreSQL Full-text (yeterli olacaktır)
  
AI/ML:
  Framework: scikit-learn, Prophet
  Serving: FastAPI endpoints
  Future: PyTorch (advanced models)
  
Infrastructure:
  Container: Docker + Docker Compose
  Reverse Proxy: Nginx
  CI/CD: GitHub Actions
  Monitoring: Prometheus + Grafana
  Logging: Loki
  
Development:
  Version Control: Git
  Code Quality: Ruff, Black (Python), ESLint, Prettier (JS)
  Testing: Pytest (backend), Vitest (frontend)
  API Docs: OpenAPI (auto-generated by FastAPI)
```

### 12.2 Proje Yapısı

```
cig-kofte-system/
├── README.md
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Settings
│   │   ├── database.py             # DB connection
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py             # Dependencies
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py       # API router
│   │   │   │   ├── auth.py
│   │   │   │   ├── branches.py
│   │   │   │   ├── products.py
│   │   │   │   ├── orders.py
│   │   │   │   ├── inventory.py
│   │   │   │   ├── purchases.py
│   │   │   │   ├── production.py
│   │   │   │   ├── employees.py
│   │   │   │   ├── expenses.py
│   │   │   │   ├── reports.py
│   │   │   │   └── ai.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── tenant.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   ├── inventory.py
│   │   │   ├── employee.py
│   │   │   ├── expense.py
│   │   │   └── ...
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   └── ...
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── order_service.py
│   │   │   ├── inventory_service.py
│   │   │   ├── report_service.py
│   │   │   └── ai_service.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   ├── permissions.py
│   │   │   └── exceptions.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│   │
│   ├── alembic/                    # DB migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── ...
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   │
│   │   ├── assets/
│   │   │   ├── styles/
│   │   │   │   ├── main.css
│   │   │   │   └── variables.css
│   │   │   └── images/
│   │   │
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Button.vue
│   │   │   │   ├── Card.vue
│   │   │   │   ├── Input.vue
│   │   │   │   ├── Select.vue
│   │   │   │   ├── Modal.vue
│   │   │   │   ├── Table.vue
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.vue
│   │   │   │   ├── Header.vue
│   │   │   │   └── MobileNav.vue
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   ├── KPICard.vue
│   │   │   │   ├── SalesChart.vue
│   │   │   │   ├── AIInsights.vue
│   │   │   │   └── QuickActions.vue
│   │   │   │
│   │   │   ├── pos/
│   │   │   │   ├── ProductGrid.vue
│   │   │   │   ├── Cart.vue
│   │   │   │   └── PaymentModal.vue
│   │   │   │
│   │   │   └── ...
│   │   │
│   │   ├── views/
│   │   │   ├── Dashboard.vue
│   │   │   ├── POS.vue
│   │   │   ├── Orders.vue
│   │   │   ├── Inventory.vue
│   │   │   ├── Purchases.vue
│   │   │   ├── Production.vue
│   │   │   ├── Employees.vue
│   │   │   ├── Expenses.vue
│   │   │   ├── Reports.vue
│   │   │   ├── Settings.vue
│   │   │   └── Login.vue
│   │   │
│   │   ├── stores/
│   │   │   ├── auth.ts
│   │   │   ├── branch.ts
│   │   │   ├── cart.ts
│   │   │   └── ...
│   │   │
│   │   ├── composables/
│   │   │   ├── useAuth.ts
│   │   │   ├── useApi.ts
│   │   │   ├── useToast.ts
│   │   │   └── ...
│   │   │
│   │   ├── router/
│   │   │   └── index.ts
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── socket.ts
│   │   │
│   │   └── types/
│   │       └── index.ts
│   │
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── Dockerfile
│
├── nginx/
│   └── nginx.conf
│
└── docs/
    ├── PRD.md (this file)
    ├── API.md
    └── DEPLOYMENT.md
```

---

## 13. FAZLAMA & ROADMAP

### 13.1 Phase 1: MVP (4-6 Hafta)

```yaml
Sprint 1-2 (2 Hafta): Foundation
  Backend:
    ✅ Project setup (FastAPI, PostgreSQL)
    ✅ Auth system (JWT, roles)
    ✅ Branch & User models
    ✅ Basic CRUD APIs
  
  Frontend:
    ✅ Project setup (Vue 3, Tailwind)
    ✅ Auth pages (login)
    ✅ Layout (sidebar, header)
    ✅ Basic routing

Sprint 3-4 (2 Hafta): Core Features
  Backend:
    ✅ Product & Category APIs
    ✅ Order APIs (create, list)
    ✅ Inventory APIs
    ✅ Purchase Order APIs
  
  Frontend:
    ✅ Dashboard (basic KPIs)
    ✅ POS screen
    ✅ Order list
    ✅ Inventory view
    ✅ Purchase entry form

Sprint 5-6 (2 Hafta): Finance & Polish
  Backend:
    ✅ Employee & Attendance APIs
    ✅ Expense APIs
    ✅ Daily summary aggregation
    ✅ Basic reports
  
  Frontend:
    ✅ Employee management
    ✅ Attendance entry
    ✅ Expense entry
    ✅ Cash register
    ✅ Basic reports

MVP Deliverables:
  - Çalışan POS sistemi
  - Mal alımı girişi
  - Personel puantaj
  - Gider girişi
  - Günlük/aylık rapor
  - Tek şube desteği
```

### 13.2 Phase 2: Enhancement (4 Hafta)

```yaml
Sprint 7-8 (2 Hafta): Production & Stock
  - Üretim modülü (hamur takibi)
  - Reçete yönetimi
  - Stok hareketleri
  - Fire takibi
  - Tedarikçi yönetimi

Sprint 9-10 (2 Hafta): Reporting & UX
  - Gelişmiş raporlar
  - Export (Excel, PDF)
  - Dashboard özelleştirme
  - Mobile responsive
  - PWA desteği
```

### 13.3 Phase 3: Multi-Branch (3 Hafta)

```yaml
Sprint 11-12 (2 Hafta): Multi-Tenancy
  - Schema-per-tenant implementation
  - Branch switching UI
  - Cross-branch reporting
  - Regional manager role

Sprint 13 (1 Hafta): Consolidation
  - Merkezi dashboard
  - Şube karşılaştırma
  - Konsolide P&L
```

### 13.4 Phase 4: AI & Enterprise (4+ Hafta)

```yaml
Sprint 14-15: Basic AI
  - Rule-based alerts
  - Trend analysis
  - Simple forecasting

Sprint 16-17: Advanced AI
  - ML-based demand forecasting
  - Anomaly detection
  - Recommendations engine

Sprint 18+: Enterprise Features
  - API integrations (Trendyol, Getir)
  - Advanced analytics
  - Mobile app (native)
  - Franchise management
```

### 13.5 Success Metrics per Phase

```yaml
MVP Success:
  - ✅ Veri giriş süresi %50 azalma
  - ✅ Ay sonu kapanış < 5 dakika
  - ✅ Sıfır kritik bug
  - ✅ 3 kullanıcı aktif kullanım

Phase 2 Success:
  - ✅ Veri giriş süresi %80 azalma
  - ✅ Maliyet görünürlüğü %100
  - ✅ Mobile kullanım aktif

Phase 3 Success:
  - ✅ 2+ şube aktif
  - ✅ Cross-branch raporlama çalışıyor
  - ✅ Regional manager onboarded

Phase 4 Success:
  - ✅ AI tahmin accuracy > 80%
  - ✅ Proaktif uyarılar aktif
  - ✅ API entegrasyonları canlı
```

---

## 14. EKLER

### 14.1 Excel'den Migrasyon Stratejisi

```yaml
Data Migration Plan:
  
  Phase 1 - Master Data:
    - Ürün katalog (manuel giriş veya CSV import)
    - Malzeme listesi
    - Tedarikçiler
    - Çalışan listesi
    - Gider kategorileri
  
  Phase 2 - Historical Data (Opsiyonel):
    - Son 3 ay satış verisi
    - Son 3 ay mal alımı
    - Maaş geçmişi
  
  Validation:
    - Excel toplamları ile sistem toplamlarını karşılaştır
    - Ay sonu rakamlarını doğrula
  
  Parallel Run:
    - 1-2 hafta hem Excel hem sistem
    - Farklılıkları analiz et
    - Sisteme tam geçiş
```

### 14.2 Güvenlik Gereksinimleri

```yaml
Authentication:
  - JWT token (access + refresh)
  - Token expiry: 15 min (access), 7 days (refresh)
  - PIN code for quick POS access
  - Session management

Authorization:
  - Role-based access control (RBAC)
  - Permission-based fine-tuning
  - Branch-level isolation

Data Security:
  - Password hashing (bcrypt)
  - HTTPS only
  - SQL injection prevention (ORM)
  - XSS prevention (sanitization)
  - CORS configuration

Audit:
  - All write operations logged
  - User action tracking
  - IP and device logging
  - Retention: 2 years
```

### 14.3 Performans Gereksinimleri

```yaml
Response Times:
  - Page load: < 2s
  - API response: < 200ms
  - POS transaction: < 500ms
  - Report generation: < 5s

Scalability:
  - Support 10+ concurrent users per branch
  - Handle 2000+ orders/day
  - Store 5+ years of data

Availability:
  - 99.5% uptime target
  - Graceful degradation
  - Offline POS support (PWA)
```

---

## 📝 NOTLAR

Bu PRD, Claude Code'a verilecek implementasyon kılavuzudur. Her sprint'te bu dokümana referans verilerek geliştirme yapılmalıdır.

**Öncelik Sırası:**
1. MVP'de en kritik: POS + Mal Alımı + Gider Girişi
2. Kullanıcı deneyimi: Touch-friendly, hata yapmayı zorlaştıran tasarım
3. Veri tutarlılığı: Validation, audit trail

**Claude Code İçin Hatırlatmalar:**
- Fix-First: Küçük hataları hemen düzelt
- TDD: Test yazmadan kod yazma
- Shadow-First: Mimari kararlarında danış
- Incremental: Küçük PR'lar, sık commit

---

**Doküman Sonu**
*Versiyon 1.0 - 16 Aralık 2025*
