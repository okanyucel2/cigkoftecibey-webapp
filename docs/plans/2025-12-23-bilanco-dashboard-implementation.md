# Bilanço Dashboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the current Dashboard with a new "Bilanço" dashboard showing yesterday's summary, weekly comparison, and monthly overview.

**Architecture:**
- New `/api/reports/bilanco` endpoint returns all data in one call
- Frontend `Bilanco.vue` replaces `Dashboard.vue` with three sections
- Sidebar label changes from "Dashboard" to "Bilanço"

**Tech Stack:** FastAPI, SQLAlchemy, Vue 3 Composition API, TypeScript, Tailwind CSS

---

## Task 1: Backend - BilancoStats Schema

**Files:**
- Modify: `backend/app/schemas/__init__.py`

**Step 1: Add BilancoStats schema after DashboardStats**

Add this code after line 299 (after `week_sales: list[dict]`):

```python
# Bilanço Dashboard
class DaySummary(BaseModel):
    day_name: str  # "Pzt", "Sal", etc.
    date: date
    amount: Decimal = Decimal("0")

class BilancoStats(BaseModel):
    # Dün
    yesterday_date: date
    yesterday_day_name: str  # "Pazartesi"
    yesterday_revenue: Decimal = Decimal("0")
    yesterday_expenses: Decimal = Decimal("0")
    yesterday_profit: Decimal = Decimal("0")
    yesterday_vs_previous_pct: Decimal = Decimal("0")  # % değişim
    yesterday_breakdown: dict[str, Decimal] = {}  # {"online": x, "mal_alimi": y, ...}

    # Bu Hafta
    this_week_start: date
    this_week_end: date
    this_week_total: Decimal = Decimal("0")
    this_week_daily: list[DaySummary] = []
    this_week_best_day: Optional[DaySummary] = None
    this_week_worst_day: Optional[DaySummary] = None

    # Geçen Hafta
    last_week_start: date
    last_week_end: date
    last_week_total: Decimal = Decimal("0")
    last_week_daily: list[DaySummary] = []
    week_vs_week_pct: Decimal = Decimal("0")  # % değişim

    # Bu Ay
    this_month_name: str  # "Aralık 2025"
    this_month_days_passed: int
    this_month_days_total: int
    this_month_revenue: Decimal = Decimal("0")
    this_month_expenses: Decimal = Decimal("0")
    this_month_profit: Decimal = Decimal("0")
    this_month_daily_avg: Decimal = Decimal("0")
    this_month_forecast: Decimal = Decimal("0")
    this_month_chart: list[DaySummary] = []

    # Geçen Ay (aynı dönem karşılaştırması için)
    last_month_revenue: Decimal = Decimal("0")
    last_month_expenses: Decimal = Decimal("0")
    last_month_profit: Decimal = Decimal("0")
```

**Step 2: Verify schema compiles**

Run: `cd /Users/okan.yucel/cigkoftecibey-webapp/backend && python -c "from app.schemas import BilancoStats; print('OK')"`
Expected: `OK`

**Step 3: Commit**

```bash
git add backend/app/schemas/__init__.py
git commit -m "feat(backend): add BilancoStats schema for new dashboard"
```

---

## Task 2: Backend - Bilanço API Endpoint

**Files:**
- Modify: `backend/app/api/reports.py`

**Step 1: Add helper functions and endpoint**

Add these imports at top of file (after existing imports):

```python
from calendar import monthrange
import locale
```

Add this new endpoint after `get_daily_summary` function:

```python
# Türkçe gün adları
TURKISH_DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
TURKISH_DAYS_SHORT = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
TURKISH_MONTHS = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                  "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]


def get_day_revenue(db: DBSession, branch_id: int, target_date: date) -> Decimal:
    """Belirli bir günün toplam cirosunu hesapla"""
    total = db.query(func.coalesce(func.sum(OnlineSale.amount), 0)).filter(
        OnlineSale.branch_id == branch_id,
        OnlineSale.sale_date == target_date
    ).scalar()
    return Decimal(str(total))


def get_day_expenses(db: DBSession, branch_id: int, target_date: date) -> Decimal:
    """Belirli bir günün toplam giderlerini hesapla (purchases + expenses + staff + courier + parttime)"""
    purchases = db.query(func.coalesce(func.sum(Purchase.total), 0)).filter(
        Purchase.branch_id == branch_id,
        Purchase.purchase_date == target_date
    ).scalar()

    expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.branch_id == branch_id,
        Expense.expense_date == target_date
    ).scalar()

    courier = db.query(func.coalesce(func.sum(CourierExpense.amount), 0)).filter(
        CourierExpense.branch_id == branch_id,
        CourierExpense.expense_date == target_date
    ).scalar()

    parttime = db.query(func.coalesce(func.sum(PartTimeCost.amount), 0)).filter(
        PartTimeCost.branch_id == branch_id,
        PartTimeCost.cost_date == target_date
    ).scalar()

    staff_meal = db.query(StaffMeal).filter(
        StaffMeal.branch_id == branch_id,
        StaffMeal.meal_date == target_date
    ).first()
    staff_cost = staff_meal.total if staff_meal else Decimal("0")

    return Decimal(str(purchases)) + Decimal(str(expenses)) + Decimal(str(courier)) + Decimal(str(parttime)) + staff_cost


def get_day_breakdown(db: DBSession, branch_id: int, target_date: date) -> dict:
    """Belirli bir günün gider kırılımını döndür"""
    purchases = db.query(func.coalesce(func.sum(Purchase.total), 0)).filter(
        Purchase.branch_id == branch_id,
        Purchase.purchase_date == target_date
    ).scalar()

    expenses = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.branch_id == branch_id,
        Expense.expense_date == target_date
    ).scalar()

    courier = db.query(func.coalesce(func.sum(CourierExpense.amount), 0)).filter(
        CourierExpense.branch_id == branch_id,
        CourierExpense.expense_date == target_date
    ).scalar()

    parttime = db.query(func.coalesce(func.sum(PartTimeCost.amount), 0)).filter(
        PartTimeCost.branch_id == branch_id,
        PartTimeCost.cost_date == target_date
    ).scalar()

    staff_meal = db.query(StaffMeal).filter(
        StaffMeal.branch_id == branch_id,
        StaffMeal.meal_date == target_date
    ).first()
    staff_cost = staff_meal.total if staff_meal else Decimal("0")

    revenue = get_day_revenue(db, branch_id, target_date)

    return {
        "online": revenue,
        "mal_alimi": Decimal(str(purchases)),
        "gider": Decimal(str(expenses)),
        "staff": staff_cost,
        "kurye": Decimal(str(courier)),
        "parttime": Decimal(str(parttime))
    }


@router.get("/bilanco", response_model=BilancoStats)
def get_bilanco_stats(db: DBSession, ctx: CurrentBranchContext):
    """Bilanço dashboard - Dün, Bu Hafta, Bu Ay özeti"""
    from app.schemas import BilancoStats, DaySummary

    today = date.today()
    yesterday = today - timedelta(days=1)
    day_before_yesterday = today - timedelta(days=2)
    branch_id = ctx.current_branch_id

    # ===== DÜN =====
    yesterday_revenue = get_day_revenue(db, branch_id, yesterday)
    yesterday_expenses = get_day_expenses(db, branch_id, yesterday)
    yesterday_profit = yesterday_revenue - yesterday_expenses
    yesterday_breakdown = get_day_breakdown(db, branch_id, yesterday)

    # Önceki güne göre değişim
    prev_revenue = get_day_revenue(db, branch_id, day_before_yesterday)
    if prev_revenue > 0:
        yesterday_vs_previous_pct = ((yesterday_revenue - prev_revenue) / prev_revenue) * 100
    else:
        yesterday_vs_previous_pct = Decimal("0")

    yesterday_day_name = TURKISH_DAYS[yesterday.weekday()]

    # ===== BU HAFTA (Pazartesi'den bugüne) =====
    # Haftanın başını bul (Pazartesi)
    days_since_monday = today.weekday()
    this_week_start = today - timedelta(days=days_since_monday)
    this_week_end = yesterday  # Bugün hariç, dün dahil

    this_week_daily = []
    this_week_total = Decimal("0")

    for i in range(7):
        day = this_week_start + timedelta(days=i)
        if day >= today:
            break
        amount = get_day_revenue(db, branch_id, day)
        this_week_daily.append(DaySummary(
            day_name=TURKISH_DAYS_SHORT[day.weekday()],
            date=day,
            amount=amount
        ))
        this_week_total += amount

    # En iyi ve en kötü gün
    if this_week_daily:
        this_week_best = max(this_week_daily, key=lambda x: x.amount)
        this_week_worst = min(this_week_daily, key=lambda x: x.amount)
    else:
        this_week_best = None
        this_week_worst = None

    # ===== GEÇEN HAFTA =====
    last_week_start = this_week_start - timedelta(days=7)
    last_week_end = this_week_start - timedelta(days=1)

    last_week_daily = []
    last_week_total = Decimal("0")

    for i in range(7):
        day = last_week_start + timedelta(days=i)
        amount = get_day_revenue(db, branch_id, day)
        last_week_daily.append(DaySummary(
            day_name=TURKISH_DAYS_SHORT[day.weekday()],
            date=day,
            amount=amount
        ))
        last_week_total += amount

    # Haftalık değişim
    if last_week_total > 0:
        week_vs_week_pct = ((this_week_total - last_week_total) / last_week_total) * 100
    else:
        week_vs_week_pct = Decimal("0")

    # ===== BU AY =====
    this_month_start = today.replace(day=1)
    _, days_in_month = monthrange(today.year, today.month)
    this_month_name = f"{TURKISH_MONTHS[today.month]} {today.year}"
    this_month_days_passed = (yesterday - this_month_start).days + 1
    this_month_days_total = days_in_month

    this_month_revenue = Decimal("0")
    this_month_expenses = Decimal("0")
    this_month_chart = []

    current = this_month_start
    while current < today:
        rev = get_day_revenue(db, branch_id, current)
        exp = get_day_expenses(db, branch_id, current)
        this_month_revenue += rev
        this_month_expenses += exp
        this_month_chart.append(DaySummary(
            day_name=str(current.day),
            date=current,
            amount=rev
        ))
        current += timedelta(days=1)

    this_month_profit = this_month_revenue - this_month_expenses

    # Günlük ortalama ve tahmin
    if this_month_days_passed > 0:
        this_month_daily_avg = this_month_revenue / this_month_days_passed
        remaining_days = this_month_days_total - this_month_days_passed
        this_month_forecast = this_month_revenue + (this_month_daily_avg * remaining_days)
    else:
        this_month_daily_avg = Decimal("0")
        this_month_forecast = Decimal("0")

    # ===== GEÇEN AY (aynı dönem) =====
    if today.month == 1:
        last_month_year = today.year - 1
        last_month_num = 12
    else:
        last_month_year = today.year
        last_month_num = today.month - 1

    last_month_start = date(last_month_year, last_month_num, 1)
    _, last_month_days = monthrange(last_month_year, last_month_num)
    # Aynı gün sayısı kadar karşılaştır
    last_month_compare_end = last_month_start + timedelta(days=min(this_month_days_passed, last_month_days) - 1)

    last_month_revenue = Decimal("0")
    last_month_expenses = Decimal("0")

    current = last_month_start
    while current <= last_month_compare_end:
        last_month_revenue += get_day_revenue(db, branch_id, current)
        last_month_expenses += get_day_expenses(db, branch_id, current)
        current += timedelta(days=1)

    last_month_profit = last_month_revenue - last_month_expenses

    return BilancoStats(
        # Dün
        yesterday_date=yesterday,
        yesterday_day_name=yesterday_day_name,
        yesterday_revenue=yesterday_revenue,
        yesterday_expenses=yesterday_expenses,
        yesterday_profit=yesterday_profit,
        yesterday_vs_previous_pct=yesterday_vs_previous_pct,
        yesterday_breakdown=yesterday_breakdown,
        # Bu Hafta
        this_week_start=this_week_start,
        this_week_end=this_week_end,
        this_week_total=this_week_total,
        this_week_daily=this_week_daily,
        this_week_best_day=this_week_best,
        this_week_worst_day=this_week_worst,
        # Geçen Hafta
        last_week_start=last_week_start,
        last_week_end=last_week_end,
        last_week_total=last_week_total,
        last_week_daily=last_week_daily,
        week_vs_week_pct=week_vs_week_pct,
        # Bu Ay
        this_month_name=this_month_name,
        this_month_days_passed=this_month_days_passed,
        this_month_days_total=this_month_days_total,
        this_month_revenue=this_month_revenue,
        this_month_expenses=this_month_expenses,
        this_month_profit=this_month_profit,
        this_month_daily_avg=this_month_daily_avg,
        this_month_forecast=this_month_forecast,
        this_month_chart=this_month_chart,
        # Geçen Ay
        last_month_revenue=last_month_revenue,
        last_month_expenses=last_month_expenses,
        last_month_profit=last_month_profit
    )
```

**Step 2: Add BilancoStats import to schemas**

Update the import line at top of `reports.py`:
```python
from app.schemas import DashboardStats, BilancoStats, DaySummary
```

**Step 3: Test endpoint manually**

Run: `cd /Users/okan.yucel/cigkoftecibey-webapp && docker-compose up -d`

Then test with curl:
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login-json" -H "Content-Type: application/json" -d '{"email":"admin@cigkofte.com","password":"admin123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
curl -s "http://localhost:8000/api/reports/bilanco" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Expected: JSON response with yesterday, this_week, last_week, this_month data

**Step 4: Commit**

```bash
git add backend/app/api/reports.py
git commit -m "feat(backend): add /api/reports/bilanco endpoint"
```

---

## Task 3: Frontend - BilancoStats Type

**Files:**
- Modify: `frontend/src/types/index.ts`

**Step 1: Add TypeScript interfaces after DashboardStats**

Add after line 141 (after DashboardStats interface):

```typescript
export interface DaySummary {
  day_name: string  // "Pzt", "Sal", etc.
  date: string
  amount: number
}

export interface BilancoStats {
  // Dün
  yesterday_date: string
  yesterday_day_name: string  // "Pazartesi"
  yesterday_revenue: number
  yesterday_expenses: number
  yesterday_profit: number
  yesterday_vs_previous_pct: number
  yesterday_breakdown: {
    online: number
    mal_alimi: number
    gider: number
    staff: number
    kurye: number
    parttime: number
  }

  // Bu Hafta
  this_week_start: string
  this_week_end: string
  this_week_total: number
  this_week_daily: DaySummary[]
  this_week_best_day: DaySummary | null
  this_week_worst_day: DaySummary | null

  // Geçen Hafta
  last_week_start: string
  last_week_end: string
  last_week_total: number
  last_week_daily: DaySummary[]
  week_vs_week_pct: number

  // Bu Ay
  this_month_name: string  // "Aralık 2025"
  this_month_days_passed: number
  this_month_days_total: number
  this_month_revenue: number
  this_month_expenses: number
  this_month_profit: number
  this_month_daily_avg: number
  this_month_forecast: number
  this_month_chart: DaySummary[]

  // Geçen Ay
  last_month_revenue: number
  last_month_expenses: number
  last_month_profit: number
}
```

**Step 2: Verify TypeScript compiles**

Run: `cd /Users/okan.yucel/cigkoftecibey-webapp/frontend && npm run build`
Expected: No TypeScript errors

**Step 3: Commit**

```bash
git add frontend/src/types/index.ts
git commit -m "feat(frontend): add BilancoStats TypeScript interface"
```

---

## Task 4: Frontend - API Service

**Files:**
- Modify: `frontend/src/services/api.ts`

**Step 1: Add getBilanco method to reportsApi**

Find `reportsApi` object (around line 220) and add new method:

```typescript
export const reportsApi = {
  getDashboard: () => api.get<DashboardStats>('/reports/dashboard'),
  getBilanco: () => api.get<BilancoStats>('/reports/bilanco'),
  getDailySummary: (startDate?: string, endDate?: string) =>
    api.get('/reports/daily-summary', { params: { start_date: startDate, end_date: endDate } })
}
```

**Step 2: Add BilancoStats import**

Update import at top of file:
```typescript
import type { ..., BilancoStats } from '@/types'
```

**Step 3: Commit**

```bash
git add frontend/src/services/api.ts
git commit -m "feat(frontend): add getBilanco API method"
```

---

## Task 5: Frontend - Bilanco.vue Component

**Files:**
- Create: `frontend/src/views/Bilanco.vue`

**Step 1: Create the new Bilanco component**

```vue
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { BilancoStats } from '@/types'
import { reportsApi } from '@/services/api'
import SmartInsightCard from '@/components/dashboard/SmartInsightCard.vue'

const router = useRouter()
const stats = ref<BilancoStats | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await reportsApi.getBilanco()
    stats.value = res.data
  } catch (error) {
    console.error('Failed to load bilanco:', error)
  } finally {
    loading.value = false
  }
})

function formatCurrency(value: number | string | null | undefined) {
  const num = Number(value) || 0
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0
  }).format(num)
}

function formatCompact(value: number | string | null | undefined) {
  const num = Number(value) || 0
  if (num >= 1000) {
    return `${(num / 1000).toFixed(0)}K`
  }
  return formatCurrency(num)
}

function formatPercent(value: number | null | undefined) {
  const num = Number(value) || 0
  const sign = num >= 0 ? '▲' : '▼'
  return `${sign} %${Math.abs(num).toFixed(0)}`
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' })
}

function formatDateRange(start: string, end: string) {
  const s = new Date(start)
  const e = new Date(end)
  return `${s.getDate()}-${e.getDate()} ${s.toLocaleDateString('tr-TR', { month: 'long' })}`
}

// Haftalık grafik için max değer
const weeklyMax = computed(() => {
  if (!stats.value) return 1
  const thisWeek = stats.value.this_week_daily.map(d => d.amount)
  const lastWeek = stats.value.last_week_daily.map(d => d.amount)
  return Math.max(...thisWeek, ...lastWeek, 1)
})

// Aylık grafik için max değer
const monthlyMax = computed(() => {
  if (!stats.value) return 1
  return Math.max(...stats.value.this_month_chart.map(d => d.amount), 1)
})
</script>

<template>
  <div v-if="loading" class="flex items-center justify-center h-64">
    <div class="text-gray-500">Yükleniyor...</div>
  </div>

  <div v-else-if="stats" class="space-y-6">
    <!-- AI Asistan -->
    <SmartInsightCard />

    <!-- Bölüm 1: Dün Özeti -->
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-800">
          Dün ({{ formatDate(stats.yesterday_date) }}, {{ stats.yesterday_day_name }})
        </h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <!-- Toplam Ciro -->
        <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 border border-green-200">
          <p class="text-sm text-green-600 font-medium">Toplam Ciro</p>
          <p class="text-2xl font-bold text-green-700">{{ formatCurrency(stats.yesterday_revenue) }}</p>
          <p :class="['text-sm mt-1', stats.yesterday_vs_previous_pct >= 0 ? 'text-green-600' : 'text-red-600']">
            {{ formatPercent(stats.yesterday_vs_previous_pct) }} önceki gün
          </p>
        </div>

        <!-- Toplam Gider -->
        <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 border border-orange-200">
          <p class="text-sm text-orange-600 font-medium">Toplam Gider</p>
          <p class="text-2xl font-bold text-orange-700">{{ formatCurrency(stats.yesterday_expenses) }}</p>
        </div>

        <!-- Net Kar -->
        <div :class="[
          'rounded-xl p-4 border',
          stats.yesterday_profit >= 0
            ? 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200'
            : 'bg-gradient-to-br from-red-50 to-red-100 border-red-200'
        ]">
          <p :class="['text-sm font-medium', stats.yesterday_profit >= 0 ? 'text-blue-600' : 'text-red-600']">
            Net Kâr
          </p>
          <p :class="['text-2xl font-bold', stats.yesterday_profit >= 0 ? 'text-blue-700' : 'text-red-700']">
            {{ formatCurrency(stats.yesterday_profit) }}
          </p>
        </div>
      </div>

      <!-- Detay Satırı -->
      <div class="text-sm text-gray-500 flex flex-wrap gap-x-4 gap-y-1">
        <span>Online {{ formatCurrency(stats.yesterday_breakdown.online) }}</span>
        <span>Mal Alımı {{ formatCurrency(stats.yesterday_breakdown.mal_alimi) }}</span>
        <span>Gider {{ formatCurrency(stats.yesterday_breakdown.gider) }}</span>
        <span>Staff {{ formatCurrency(stats.yesterday_breakdown.staff) }}</span>
        <span>Kurye {{ formatCurrency(stats.yesterday_breakdown.kurye) }}</span>
      </div>
    </div>

    <!-- Hızlı İşlemler -->
    <div class="card">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Hızlı İşlemler</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <button @click="router.push('/sales')" class="btn btn-primary flex items-center justify-center gap-2">
          <span>Satış Gir</span>
        </button>
        <button @click="router.push('/purchases/new')" class="btn btn-secondary flex items-center justify-center gap-2">
          <span>Mal Alımı</span>
        </button>
        <button @click="router.push('/expenses/new')" class="btn btn-secondary flex items-center justify-center gap-2">
          <span>Gider Ekle</span>
        </button>
        <button @click="router.push('/production')" class="btn btn-secondary flex items-center justify-center gap-2">
          <span>Üretim Gir</span>
        </button>
      </div>
    </div>

    <!-- Bölüm 2: Haftalık Karşılaştırma -->
    <div class="card">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Bu Hafta vs Geçen Hafta</h2>

      <!-- Hafta Toplamları -->
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="bg-indigo-50 rounded-xl p-4 border border-indigo-200">
          <p class="text-sm text-indigo-600">Bu Hafta ({{ formatDateRange(stats.this_week_start, stats.this_week_end) }})</p>
          <p class="text-2xl font-bold text-indigo-700">{{ formatCurrency(stats.this_week_total) }}</p>
          <p :class="['text-sm', stats.week_vs_week_pct >= 0 ? 'text-green-600' : 'text-red-600']">
            {{ formatPercent(stats.week_vs_week_pct) }}
          </p>
        </div>
        <div class="bg-gray-50 rounded-xl p-4 border border-gray-200">
          <p class="text-sm text-gray-600">Geçen Hafta ({{ formatDateRange(stats.last_week_start, stats.last_week_end) }})</p>
          <p class="text-2xl font-bold text-gray-700">{{ formatCurrency(stats.last_week_total) }}</p>
        </div>
      </div>

      <!-- Gün Bazlı Karşılaştırma -->
      <div class="flex items-end gap-2 h-40">
        <div v-for="(day, idx) in stats.this_week_daily" :key="day.date" class="flex-1 flex flex-col items-center">
          <!-- Bu hafta bar -->
          <div class="w-full flex flex-col items-center gap-1">
            <div
              class="w-3/4 bg-indigo-500 rounded-t transition-all"
              :style="{ height: `${Math.max(4, (day.amount / weeklyMax) * 100)}px` }"
            />
            <div
              v-if="stats.last_week_daily[idx]"
              class="w-3/4 bg-gray-300 rounded-t transition-all"
              :style="{ height: `${Math.max(4, (stats.last_week_daily[idx].amount / weeklyMax) * 100)}px` }"
            />
          </div>
          <p class="text-xs text-gray-500 mt-2">{{ day.day_name }}</p>
          <p class="text-xs font-medium">{{ formatCompact(day.amount) }}</p>
        </div>
      </div>

      <!-- En iyi / En kötü -->
      <div class="flex gap-4 mt-4 text-sm">
        <span v-if="stats.this_week_best_day" class="text-green-600">
          En iyi: {{ stats.this_week_best_day.day_name }} ({{ formatCurrency(stats.this_week_best_day.amount) }})
        </span>
        <span v-if="stats.this_week_worst_day" class="text-red-600">
          En düşük: {{ stats.this_week_worst_day.day_name }} ({{ formatCurrency(stats.this_week_worst_day.amount) }})
        </span>
      </div>
    </div>

    <!-- Bölüm 3: Aylık Özet -->
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-800">{{ stats.this_month_name }} Özeti</h2>
        <span class="text-sm text-gray-500">{{ stats.this_month_days_passed }}/{{ stats.this_month_days_total }} gün</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <!-- Toplam Ciro -->
        <div class="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-4 border border-emerald-200">
          <p class="text-sm text-emerald-600 font-medium">Toplam Ciro</p>
          <p class="text-2xl font-bold text-emerald-700">{{ formatCurrency(stats.this_month_revenue) }}</p>
          <p class="text-xs text-gray-500 mt-1">Geçen ay: {{ formatCurrency(stats.last_month_revenue) }}</p>
        </div>

        <!-- Toplam Gider -->
        <div class="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-4 border border-amber-200">
          <p class="text-sm text-amber-600 font-medium">Toplam Gider</p>
          <p class="text-2xl font-bold text-amber-700">{{ formatCurrency(stats.this_month_expenses) }}</p>
          <p class="text-xs text-gray-500 mt-1">Geçen ay: {{ formatCurrency(stats.last_month_expenses) }}</p>
        </div>

        <!-- Net Kar -->
        <div :class="[
          'rounded-xl p-4 border',
          stats.this_month_profit >= 0
            ? 'bg-gradient-to-br from-cyan-50 to-cyan-100 border-cyan-200'
            : 'bg-gradient-to-br from-rose-50 to-rose-100 border-rose-200'
        ]">
          <p :class="['text-sm font-medium', stats.this_month_profit >= 0 ? 'text-cyan-600' : 'text-rose-600']">
            Net Kâr
          </p>
          <p :class="['text-2xl font-bold', stats.this_month_profit >= 0 ? 'text-cyan-700' : 'text-rose-700']">
            {{ formatCurrency(stats.this_month_profit) }}
          </p>
          <p class="text-xs text-gray-500 mt-1">Geçen ay: {{ formatCurrency(stats.last_month_profit) }}</p>
        </div>
      </div>

      <!-- Aylık Grafik -->
      <div class="h-24 flex items-end gap-px">
        <div
          v-for="day in stats.this_month_chart"
          :key="day.date"
          class="flex-1 bg-emerald-400 rounded-t transition-all hover:bg-emerald-500"
          :style="{ height: `${Math.max(2, (day.amount / monthlyMax) * 100)}%` }"
          :title="`${day.day_name}: ${formatCurrency(day.amount)}`"
        />
      </div>

      <!-- Alt bilgiler -->
      <div class="flex flex-wrap gap-4 mt-4 text-sm text-gray-600">
        <span>Günlük Ortalama: <strong>{{ formatCurrency(stats.this_month_daily_avg) }}</strong></span>
        <span>Kalan Gün: <strong>{{ stats.this_month_days_total - stats.this_month_days_passed }}</strong></span>
        <span>Tahmini Ay Sonu: <strong>{{ formatCurrency(stats.this_month_forecast) }}</strong></span>
      </div>
    </div>
  </div>
</template>
```

**Step 2: Verify component compiles**

Run: `cd /Users/okan.yucel/cigkoftecibey-webapp/frontend && npm run build`
Expected: No errors

**Step 3: Commit**

```bash
git add frontend/src/views/Bilanco.vue
git commit -m "feat(frontend): add Bilanco.vue component"
```

---

## Task 6: Frontend - Update Router & Sidebar

**Files:**
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/views/Layout.vue`

**Step 1: Update router to use Bilanco**

In `frontend/src/router/index.ts`, change line 26-27:

```typescript
{
  path: '',
  name: 'bilanco',
  component: () => import('@/views/Bilanco.vue')
},
```

**Step 2: Update sidebar in Layout.vue**

In `frontend/src/views/Layout.vue`, find line 15 and change:

```typescript
const menuItems = [
  { path: '/', name: 'Bilanço', icon: '📊' },
  // ... rest stays the same
```

**Step 3: Test locally**

Run: `cd /Users/okan.yucel/cigkoftecibey-webapp/frontend && npm run dev`

Open browser: http://localhost:5173
Expected: See new Bilanço dashboard with Dün, Haftalık, Aylık sections

**Step 4: Commit**

```bash
git add frontend/src/router/index.ts frontend/src/views/Layout.vue
git commit -m "feat(frontend): rename Dashboard to Bilanço in router and sidebar"
```

---

## Task 7: Cleanup - Remove Old Dashboard

**Files:**
- Delete: `frontend/src/views/Dashboard.vue` (optional - keep for backup)

**Step 1: Optionally keep Dashboard.vue as backup**

```bash
mv frontend/src/views/Dashboard.vue frontend/src/views/Dashboard.vue.bak
```

Or delete if not needed:
```bash
rm frontend/src/views/Dashboard.vue
```

**Step 2: Final test**

Run full stack:
```bash
cd /Users/okan.yucel/cigkoftecibey-webapp
docker-compose up -d
cd frontend && npm run dev
```

Test all three sections:
1. Dün özeti kartları görünüyor mu?
2. Haftalık karşılaştırma çalışıyor mu?
3. Aylık grafik görünüyor mu?

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: cleanup old Dashboard.vue"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | BilancoStats Schema | `backend/app/schemas/__init__.py` |
| 2 | Bilanço API Endpoint | `backend/app/api/reports.py` |
| 3 | TypeScript Interface | `frontend/src/types/index.ts` |
| 4 | API Service Method | `frontend/src/services/api.ts` |
| 5 | Bilanco.vue Component | `frontend/src/views/Bilanco.vue` |
| 6 | Router & Sidebar | `frontend/src/router/index.ts`, `Layout.vue` |
| 7 | Cleanup | Remove old Dashboard.vue |

**Total commits: 7**
