# Platform Evolution Roadmap

> **For Claude:** Execute phases in order. Each phase builds on previous.

**Goal:** Transform single-tenant app into scalable multi-restaurant SaaS with centralized import and dynamic POS support.

**Phases:**
1. UI/UX Reorganization + Central Import Hub - IMMEDIATE
2. Multi-Tenancy Foundation - NEXT
3. Dynamic POS Field Mapping - FUTURE

---

## Phase 1: UI/UX Reorganization + Central Import Hub

**Status:** READY TO IMPLEMENT

**Goals:**
1. Reduce 9 top-level tabs to 6 logical groups
2. Create centralized Import Hub for all data entry
3. Clean up code before multi-tenancy

### Current State (9 tabs)
```
Bilanço | Kasa Hareketleri | Üretim/Legen | Mal Alımı |
Personel Yemek | Personel Yönetimi | Kurye Giderleri |
İşletme Giderleri | Kasa Farkı
```

### Target State (6 main groups)

```
📊 Bilanço (/)
   └── Ana dashboard, günlük/haftalık/aylık özet

📥 İçe Aktar (/import) ← YENİ - Central Import Hub
   ├── Drag & drop zone
   ├── Otomatik dosya tipi algılama
   ├── Veri önizleme ve mapping
   ├── Cross-validation (Kasa vs Hasilat)
   └── Onay ve kaydet

💰 Ciro (/sales)
   ├── /sales → Satış listesi (mevcut Kasa Hareketleri)
   └── /sales/verify → Kasa Farkı detay/düzeltme

🏭 Operasyon (/operations)
   ├── /operations/production → Üretim/Legen
   └── /operations/purchases → Mal Alımı

👥 Personel (/personnel)
   ├── /personnel → Çalışan listesi
   ├── /personnel/meals → Personel Yemek
   └── /personnel/payroll → Maaş/Bordro

💸 Giderler (/expenses)
   ├── /expenses → İşletme Giderleri
   └── /expenses/courier → Kurye Giderleri

⚙️ Ayarlar (/settings) - Admin only
   ├── /settings → Genel ayarlar
   ├── /settings/branches → Şube Yönetimi
   ├── /settings/users → Kullanıcı Yönetimi
   └── /settings/pos → POS Yapılandırma (Phase 3)
```

### Central Import Hub Detay

**Desteklenen Dosya Tipleri:**

| Dosya Tipi | Algılama Kriteri | Hedef |
|------------|------------------|-------|
| Kasa Raporu | "KASA RAPORU" header veya VISA+NAKİT+GİDERLER yapısı | Ciro + Giderler |
| Hasilat Raporu | "HASILAT RAPORU" header veya POS 1/POS 2 yapısı | Doğrulama |
| Personel Maaş | "PERSONEL MAAŞ" header veya MAAŞ+SGK kolonları | Personel Bordro |
| POS Fişi | Image (JPG/PNG) | Kasa Farkı doğrulama |

**Import Flow:**

```
1. Kullanıcı dosya sürükler
   ↓
2. Sistem dosya tipini algılar
   ├── Excel: Header pattern matching
   └── Image: POS fişi olarak işle
   ↓
3. Veri parse edilir ve önizleme gösterilir
   ├── Kasa Raporu: Satış + Gider tablosu
   ├── Hasilat Raporu: Özet + Fark hesabı
   └── Personel Maaş: Çalışan listesi
   ↓
4. Cross-validation (varsa)
   ├── Kasa vs Hasilat toplam karşılaştırma
   └── Fark varsa uyarı göster
   ↓
5. Kullanıcı onaylar
   ↓
6. Veriler ilgili tablolara yazılır
   └── Import log tutulur
```

**UI Wireframe:**

```
┌─────────────────────────────────────────────────────────┐
│  📥 Veri İçe Aktar                          [Geçmiş ↓] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                 │   │
│  │     📄 Dosyaları buraya sürükleyin             │   │
│  │        veya tıklayarak seçin                   │   │
│  │                                                 │   │
│  │   Desteklenen: Excel (.xlsx), Resim (.jpg/png) │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ─────────────── Son Yüklemeler ───────────────        │
│                                                         │
│  ✅ Kasa Raporu (23.12.2025) - 190,503 TL              │
│  ✅ Personel Maaş (Aralık 2025) - 22 çalışan           │
│  ⚠️ Hasilat Raporu (23.12.2025) - 50 TL fark!         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Implementation Tasks

#### Task 1.1: Router Restructure
- Update `frontend/src/router/index.ts`
- Create nested route groups
- Add new `/import` route

#### Task 1.2: Navigation Component
- Create sidebar with collapsible groups
- Mobile-friendly bottom nav
- Active state indicators

#### Task 1.3: Import Hub Page
- Create `frontend/src/views/Import.vue`
- Drag & drop file upload
- File type detection logic
- Preview components per file type

#### Task 1.4: Excel Parsers (Backend)
- Enhance `backend/app/utils/excel_parser.py`
- Add Hasilat Raporu parser
- Add Personel Maaş parser
- Auto-detect file type from content

#### Task 1.5: Import API Endpoints
- `POST /api/import/detect` - Detect file type
- `POST /api/import/preview` - Parse and preview
- `POST /api/import/confirm` - Save to database
- `GET /api/import/history` - Recent imports

#### Task 1.6: Existing Pages Migration
- Move existing views to new route structure
- Update internal links
- Test all flows

---

## Phase 2: Multi-Tenancy Foundation

**Status:** PLANNED - Execute after Phase 1

**Goal:** Add tenant isolation for multiple restaurant chains.

### Data Model Changes

```sql
-- NEW TABLE
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,        -- "Çiğköfteci Bey"
    slug VARCHAR(100) UNIQUE NOT NULL, -- "cigkofteci-bey"
    plan VARCHAR(50) DEFAULT 'free',   -- free, pro, enterprise
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- MODIFY branches
ALTER TABLE branches ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);

-- MODIFY users
ALTER TABLE users ADD COLUMN tenant_id INTEGER REFERENCES tenants(id);

-- RLS Policies (after migration)
ALTER TABLE branches ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON branches
    USING (tenant_id = current_setting('app.current_tenant')::int);
```

### Auth Changes

```python
# Current
class TokenPayload:
    sub: str  # user_id
    branch_id: int

# New
class TokenPayload:
    sub: str  # user_id
    tenant_id: int          # NEW
    branch_id: int
    accessible_branches: list[int]
```

### API Middleware

```python
@app.middleware("http")
async def tenant_context(request: Request, call_next):
    # Extract tenant from token
    tenant_id = get_tenant_from_token(request)

    # Set PostgreSQL session variable for RLS
    db.execute(f"SET app.current_tenant = {tenant_id}")

    # Add to request state
    request.state.tenant_id = tenant_id

    return await call_next(request)
```

### Migration Strategy

1. Create `tenants` table
2. Create default tenant (id=1) for existing data
3. Add `tenant_id` to `branches` (default=1)
4. Add `tenant_id` to `users` (default=1)
5. Update auth to include tenant context
6. Add RLS policies
7. Update all API endpoints

### Implementation Tasks

#### Task 2.1: Tenant Model & Migration
- Create Tenant SQLAlchemy model
- Write Alembic migration
- Create default tenant for existing data

#### Task 2.2: Update Branch & User Models
- Add tenant_id foreign key
- Update relationships

#### Task 2.3: Auth System Update
- Modify token payload
- Add tenant context to login
- Update CurrentContext dependency

#### Task 2.4: RLS Policies
- Enable RLS on all tenant-scoped tables
- Create policies for read/write operations

#### Task 2.5: API Middleware
- Create tenant context middleware
- Apply to all routes

#### Task 2.6: Frontend Tenant Context
- Store tenant info in auth store
- Display tenant name in header

---

## Phase 3: Dynamic POS Field Mapping

**Status:** PLANNED - Execute after Phase 2

**Goal:** Support any POS report format through user-defined mapping.

### Problem

Current system has hardcoded fields:
- VISA, NAKİT, Trendyol, Getir, Yemek Sepeti, Migros

Different restaurants have:
- Different POS systems
- Different payment methods
- Different report layouts
- Different number of POS devices

### Solution: Template-Based Mapping

```
1. User uploads sample POS image/Excel (first time)
2. System detects all data fields
3. User maps each field to destination:
   - "VISA" → Satış: Kredi Kartı
   - "POS 1" → Satış: POS Cihazı 1
   - "Elektrik" → Gider: Faturalar
4. Template saved for branch
5. Future imports auto-apply template
```

### Data Model

```sql
CREATE TABLE pos_templates (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER REFERENCES branches(id),
    name VARCHAR(255),
    template_type VARCHAR(50), -- 'excel', 'image'
    field_mappings JSONB,
    -- Example field_mappings:
    -- [
    --   {"source_label": "VISA", "dest_type": "sale", "dest_platform_id": 1},
    --   {"source_label": "POS 1", "dest_type": "sale", "dest_platform_id": 2},
    --   {"source_label": "Elektrik", "dest_type": "expense", "dest_category_id": 5}
    -- ]
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP
);

CREATE TABLE import_logs (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER REFERENCES branches(id),
    template_id INTEGER REFERENCES pos_templates(id),
    import_date DATE,
    file_type VARCHAR(50),
    raw_data JSONB,
    mapped_data JSONB,
    validation_status VARCHAR(50), -- pending, validated, error
    validation_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### OCR Validation & Auto-Retry

```python
def validate_ocr_against_excel(ocr_values: dict, excel_values: dict) -> dict:
    """
    Compare OCR results with Excel values.
    Auto-retry if decimal misread detected (100x difference).
    """
    issues = []

    for field, ocr_val in ocr_values.items():
        excel_val = excel_values.get(field)
        if excel_val and excel_val > 0:
            ratio = ocr_val / excel_val
            if ratio > 100:  # OCR read 68,000,000 instead of 68,000
                issues.append({
                    "field": field,
                    "ocr": ocr_val,
                    "excel": excel_val,
                    "issue": "decimal_misread",
                    "action": "auto_retry"
                })
            elif ratio < 0.01:  # OCR missed digits
                issues.append({
                    "field": field,
                    "ocr": ocr_val,
                    "excel": excel_val,
                    "issue": "digits_missed",
                    "action": "auto_retry"
                })
            elif abs(ocr_val - excel_val) > 100:  # Small difference
                issues.append({
                    "field": field,
                    "ocr": ocr_val,
                    "excel": excel_val,
                    "issue": "minor_difference",
                    "action": "manual_review"
                })

    if any(i["action"] == "auto_retry" for i in issues):
        return {"status": "retry", "issues": issues}
    elif issues:
        return {"status": "review", "issues": issues}
    else:
        return {"status": "ok"}
```

### Template Editor UI

```
┌─────────────────────────────────────────────────────────┐
│  ⚙️ POS Şablonu Düzenle                    [Kaydet]    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Şablon Adı: [Günlük Kasa Raporu          ]            │
│                                                         │
│  ─────────────── Alan Eşleştirme ───────────────       │
│                                                         │
│  Kaynak Alan          Hedef                             │
│  ─────────────────────────────────────────────          │
│  VISA            →   [Satış: Visa         ▼]           │
│  PAKET VISA      →   [Satış: Visa         ▼]           │
│  NAKİT           →   [Satış: Nakit        ▼]           │
│  PAKET NAKİT     →   [Satış: Nakit        ▼]           │
│  TRENDYOL        →   [Satış: Trendyol     ▼]           │
│  GETİR           →   [Satış: Getir        ▼]           │
│  POS 1           →   [Satış: POS Cihazı 1 ▼]           │
│  POS 2           →   [Satış: POS Cihazı 2 ▼]           │
│  Elektrik        →   [Gider: Faturalar    ▼]           │
│  NFS KOMİSYON    →   [Yoksay              ▼]           │
│                                                         │
│  [+ Yeni Hedef Ekle]                                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Implementation Tasks

#### Task 3.1: POSTemplate Model & Migration

#### Task 3.2: Template CRUD API

#### Task 3.3: Enhanced Excel Parser
- Detect all fields dynamically
- Apply template mapping

#### Task 3.4: Enhanced OCR
- Region-based field detection
- Template-guided extraction

#### Task 3.5: Validation Engine
- Excel vs OCR comparison
- Auto-retry logic

#### Task 3.6: Template Editor UI

#### Task 3.7: Import Flow Integration
- Use template during import
- Show mapping in preview

---

## Execution Summary

| Phase | Focus | Prerequisites | Est. Effort |
|-------|-------|---------------|-------------|
| 1 | UI Reorganization + Import Hub | None | 1-2 weeks |
| 2 | Multi-Tenancy | Phase 1 | 2 weeks |
| 3 | Dynamic POS Mapping | Phase 2 | 2 weeks |

---

## Key Decisions Made

1. **Central Import Hub** at `/import` - single entry point for all data
2. **Shared database with RLS** for multi-tenancy
3. **Template-based mapping** for POS flexibility
4. **OCR validation** with auto-retry on 100x differences
5. **Excel type detection** from content, not filename

## Open Questions

1. **Tenant onboarding:** Self-service or admin-created?
2. **Billing:** Per-tenant or per-branch?
3. **Template sharing:** Can templates be copied between branches?
4. **Import history:** How long to keep?

---

## Appendix: Analyzed Excel Structures

### Kasa Raporu (1453.xlsx)
```
Row 3:  TARİH        | 2025-12-23
Row 5:  VISA         | 112,452
Row 6:  PAKET VISA   | 12,993
Row 7:  NFS KOMİSYON | 500
Row 8:  TOPLAM       | 125,945
Row 9:  NAKİT        | 37,023
Row 10: PAKET NAKİT  | 15,300
Row 11: TOPLAM       | 52,323
Row 12: TRENDYOL     | 5,000
Row 13: GETİR        | 6,123
Row 14: YEMEK SEPETİ | 946
Row 15: MİGROS YEMEK | 166
Row 17: GENEL TOPLAM | 190,503
Row 18+: GİDERLER bölümü
```

### Hasilat Raporu (ŞEFİM)
```
Row 2:  TARİH        | 2025-12-23
Row 3:  VISA         | 108,452
Row 4:  POS 1        | 10,040  ← Kasa raporunda yok
Row 5:  POS 2        | 2,634   ← Kasa raporunda yok
Row 6:  PAKET VISA   | 4,867
Row 7:  TOPLAM       | 125,993
Row 8:  NAKİT        | 37,023
Row 9:  PAKET NAKİT  | 15,302
Row 10: TOPLAM       | 52,325
Row 11: TRENDYOL     | 5,000
Row 12: GETİR        | 6,123
Row 13: YEMEK SEPETİ | 946
Row 14: MİGROS YEMEK | 166
Row 15: GENEL TOPLAM | 190,553
```

### Personel Maaş
```
Row 1: Header
Row 2: GENEL TOPLAM | 1,318,350 | 187,000 | ... | 1,620,810
Row 3: Column names: PERSONEL İSMİ | MAAŞ | SGK | PRİM | MESAİ | EK ÖDENEK | AVANS | KESİNTİ | TOPLAM
Row 4+: Employee data (22 rows)
Row 26+: Haftalık mesai saatleri (1.HAFTA, 2.HAFTA, 3.HAFTA, 4.HAFTA)
```
