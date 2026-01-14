<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { Employee, MonthlyPayroll, PayrollSummary, PartTimeCost, PartTimeCostSummary, DateRangeValue } from '@/types'
import { extractErrorMessage } from '@/types'
import { personnelApi } from '@/services/api'

// Composables
import { useFormatters, useConfirmModal, MONTHS } from '@/composables'

// UI Components
import { ConfirmModal, ErrorAlert, LoadingState, PageModal, SummaryCard } from '@/components/ui'
import { TabBar, UnifiedFilterBar } from '@/components/ui'
import type { Tab, EntityConfig } from '@/components/ui'

// Use composables
const { formatCurrency, formatDate } = useFormatters()
const confirmModal = useConfirmModal()

// Tab state
const activeTab = ref<string>('employees')

// Common state
const loading = ref(true)
const error = ref('')
const submitting = ref(false)

// Date Range Filter (replaces MonthYearFilter)
const dateRangeFilter = ref<DateRangeValue>({
  mode: 'month',
  start: new Date().toISOString().split('T')[0],
  end: new Date().toISOString().split('T')[0],
  month: new Date().getMonth() + 1,
  year: new Date().getFullYear()
})

// Get month/year from dateRangeFilter for backward compatibility
const selectedMonth = computed(() => dateRangeFilter.value.month || new Date().getMonth() + 1)
const selectedYear = computed(() => dateRangeFilter.value.year || new Date().getFullYear())

// Employee state
const employees = ref<Employee[]>([])

// Sorted employees (alphabetically by name)
const sortedEmployees = computed(() => {
  return [...employees.value].sort((a, b) => a.name.localeCompare(b.name, 'tr'))
})

const showEmployeeForm = ref(false)
const editingEmployeeId = ref<number | null>(null)
const employeeForm = ref({
  name: '',
  base_salary: 0,
  has_sgk: true,
  sgk_amount: 7524.46,
  daily_rate: 0,
  hourly_rate: 110,
  payment_type: 'monthly' as 'monthly' | 'weekly',
  is_part_time: false
})

// Payroll state
const payrolls = ref<MonthlyPayroll[]>([])
const payrollSummary = ref<PayrollSummary | null>(null)
const showPayrollForm = ref(false)
const editingPayrollId = ref<number | null>(null)
const selectedEmployeeFilter = ref<number | null>(null)
const payrollForm = ref({
  employee_id: 0,
  payment_date: new Date().toISOString().split('T')[0],
  record_type: 'salary' as 'salary' | 'advance' | 'weekly' | 'sgk' | 'prim',
  base_salary: 0,
  sgk_amount: 0,
  bonus: 0,
  premium: 0,
  overtime_hours: 0,
  overtime_amount: 0,
  advance: 0,
  absence_days: 0,
  absence_deduction: 0,
  notes: ''
})

const recordTypes = [
  { value: 'salary', label: 'Maas Odemesi' },
  { value: 'advance', label: 'Avans' },
  { value: 'weekly', label: 'Haftalik Odeme' },
  { value: 'sgk', label: 'SGK Odemesi' },
  { value: 'prim', label: 'Prim Odemesi' }
]

// Part-time state
const partTimeCosts = ref<PartTimeCost[]>([])
const partTimeSummary = ref<PartTimeCostSummary | null>(null)
const showPartTimeForm = ref(false)
const editingPartTimeId = ref<number | null>(null)
const partTimeForm = ref({
  cost_date: new Date().toISOString().split('T')[0],
  amount: 0,
  notes: ''
})


onMounted(async () => {
  await loadEmployees()
})

watch(activeTab, () => {
  if (activeTab.value === 'payroll') {
    loadPayrolls()
  } else if (activeTab.value === 'parttime') {
    loadPartTimeCosts()
  }
})

watch(() => dateRangeFilter.value, () => {
  if (activeTab.value === 'payroll') {
    loadPayrolls()
  } else if (activeTab.value === 'parttime') {
    loadPartTimeCosts()
  }
}, { deep: true })

watch(selectedEmployeeFilter, () => {
  if (activeTab.value === 'payroll') {
    loadPayrolls()
  }
})

// record_type degisince form alanlarini sifirla
watch(() => payrollForm.value.record_type, (newType, oldType) => {
  if (newType !== oldType && !editingPayrollId.value) {
    // Sadece yeni kayit icin sifirla, edit modunda dokunma
    if (newType === 'advance') {
      // Avans: sadece avans alani kalsin
      payrollForm.value.base_salary = 0
      payrollForm.value.sgk_amount = 0
      payrollForm.value.bonus = 0
      payrollForm.value.premium = 0
      payrollForm.value.overtime_hours = 0
      payrollForm.value.overtime_amount = 0
      payrollForm.value.absence_days = 0
      payrollForm.value.absence_deduction = 0
    } else if (newType === 'weekly') {
      // Haftalik: sgk, bonus, prim vs. sifir - sadece odeme tutari ve mesai girilecek
      payrollForm.value.base_salary = 0
      payrollForm.value.sgk_amount = 0
      payrollForm.value.bonus = 0
      payrollForm.value.premium = 0
      payrollForm.value.absence_days = 0
      payrollForm.value.absence_deduction = 0
    } else if (newType === 'salary') {
      // Maas: personel seciliyse bilgileri tekrar yukle
      if (payrollForm.value.employee_id) {
        onEmployeeSelect(payrollForm.value.employee_id)
      }
    }
  }
})

// ==================== EMPLOYEES ====================

async function loadEmployees() {
  loading.value = true
  error.value = ''
  try {
    const res = await personnelApi.getEmployees()
    employees.value = res.data
  } catch (e: unknown) {
    error.value = extractErrorMessage(e, 'Personel listesi yuklenemedi')
  } finally {
    loading.value = false
  }
}

function openEmployeeForm(employee?: Employee) {
  if (employee) {
    editingEmployeeId.value = employee.id
    employeeForm.value = {
      name: employee.name,
      base_salary: Number(employee.base_salary),
      has_sgk: employee.has_sgk,
      sgk_amount: Number(employee.sgk_amount),
      daily_rate: Number(employee.daily_rate),
      hourly_rate: Number(employee.hourly_rate),
      payment_type: employee.payment_type,
      is_part_time: employee.is_part_time
    }
  } else {
    editingEmployeeId.value = null
    employeeForm.value = {
      name: '',
      base_salary: 0,
      has_sgk: true,
      sgk_amount: 7524.46,
      daily_rate: 0,
      hourly_rate: 110,
      payment_type: 'monthly',
      is_part_time: false
    }
  }
  showEmployeeForm.value = true
}

async function submitEmployeeForm() {
  if (!employeeForm.value.name) {
    error.value = 'Personel adi zorunlu'
    return
  }

  submitting.value = true
  error.value = ''
  try {
    if (editingEmployeeId.value) {
      await personnelApi.updateEmployee(editingEmployeeId.value, employeeForm.value)
    } else {
      await personnelApi.createEmployee(employeeForm.value)
    }
    showEmployeeForm.value = false
    await loadEmployees()
  } catch (e: unknown) {
    error.value = extractErrorMessage(e, 'Kayit basarisiz')
  } finally {
    submitting.value = false
  }
}

async function deleteEmployee(id: number) {
  confirmModal.confirm('Bu personeli pasif yapmak istediginize emin misiniz?', async () => {
    try {
      await personnelApi.deleteEmployee(id)
      await loadEmployees()
    } catch (e: unknown) {
      error.value = extractErrorMessage(e, 'Silme basarisiz')
    }
  })
}

// ==================== PAYROLL ====================

async function loadPayrolls() {
  loading.value = true
  error.value = ''
  try {
    const params: { year: number; month: number; employee_id?: number } = {
      year: dateRangeFilter.value.year || new Date().getFullYear(),
      month: dateRangeFilter.value.month || new Date().getMonth() + 1
    }
    if (selectedEmployeeFilter.value) {
      params.employee_id = selectedEmployeeFilter.value
    }
    const [payrollRes, summaryRes] = await Promise.all([
      personnelApi.getPayrolls(params),
      personnelApi.getPayrollSummary(
        dateRangeFilter.value.year || new Date().getFullYear(),
        dateRangeFilter.value.month || new Date().getMonth() + 1,
        selectedEmployeeFilter.value || undefined
      )
    ])
    payrolls.value = payrollRes.data
    payrollSummary.value = summaryRes.data
  } catch (e: unknown) {
    error.value = extractErrorMessage(e, 'Bordro yuklenemedi')
  } finally {
    loading.value = false
  }
}

function openPayrollForm(payroll?: MonthlyPayroll) {
  if (payroll) {
    editingPayrollId.value = payroll.id
    payrollForm.value = {
      employee_id: payroll.employee_id,
      payment_date: payroll.payment_date,
      record_type: payroll.record_type,
      base_salary: Number(payroll.base_salary),
      sgk_amount: Number(payroll.sgk_amount),
      bonus: Number(payroll.bonus),
      premium: Number(payroll.premium),
      overtime_hours: Number(payroll.overtime_hours),
      overtime_amount: Number(payroll.overtime_amount),
      advance: Number(payroll.advance),
      absence_days: Number(payroll.absence_days),
      absence_deduction: Number(payroll.absence_deduction),
      notes: payroll.notes || ''
    }
  } else {
    editingPayrollId.value = null
    payrollForm.value = {
      employee_id: 0,
      payment_date: new Date().toISOString().split('T')[0],
      record_type: 'salary',
      base_salary: 0,
      sgk_amount: 0,
      bonus: 0,
      premium: 0,
      overtime_hours: 0,
      overtime_amount: 0,
      advance: 0,
      absence_days: 0,
      absence_deduction: 0,
      notes: ''
    }
  }
  showPayrollForm.value = true
}

function onEmployeeSelect(employeeId: number) {
  const employee = employees.value.find(e => e.id === employeeId)
  if (employee) {
    // Sadece maas odemesinde tam bilgileri doldur
    if (payrollForm.value.record_type === 'salary') {
      payrollForm.value.base_salary = Number(employee.base_salary)
      payrollForm.value.sgk_amount = employee.has_sgk ? Number(employee.sgk_amount) : 0
    } else if (payrollForm.value.record_type === 'weekly') {
      // Haftalik odemede SGK yok, maas olarak gunluk/haftalik ucret kullanilabilir
      payrollForm.value.base_salary = 0
      payrollForm.value.sgk_amount = 0
    }
    // Avans icin hicbir sey doldurma
  }
}

// Mesai tutari hesapla (saat * saatlik ucret)
function calculateOvertimeAmount() {
  const employee = employees.value.find(e => e.id === payrollForm.value.employee_id)
  if (employee) {
    payrollForm.value.overtime_amount = payrollForm.value.overtime_hours * Number(employee.hourly_rate)
  }
}

// Secili personelin bu ay aldigi avanslar
const employeeMonthlyAdvances = computed(() => {
  if (!payrollForm.value.employee_id || payrollForm.value.record_type !== 'salary') {
    return 0
  }
  // Mevcut kayitlardan bu ay, bu personelin avanslarini topla
  return payrolls.value
    .filter(p =>
      p.employee_id === payrollForm.value.employee_id &&
      p.record_type === 'advance'
    )
    .reduce((sum, p) => sum + Number(p.total), 0)
})

// Brut toplam (kesintisiz)
const payrollGross = computed(() => {
  const f = payrollForm.value
  if (f.record_type === 'advance') {
    return f.advance
  }
  return f.base_salary + f.sgk_amount + f.bonus + f.premium + f.overtime_amount
})

// Kesintiler toplami (ay icinde alinan avanslar dahil)
const payrollDeductions = computed(() => {
  const f = payrollForm.value
  if (f.record_type === 'advance') {
    return 0
  }
  return f.advance + f.absence_deduction + employeeMonthlyAdvances.value
})

// Net toplam (kesintili)
const payrollTotal = computed(() => {
  return payrollGross.value - payrollDeductions.value
})

async function submitPayrollForm() {
  if (!payrollForm.value.employee_id) {
    error.value = 'Personel secimi zorunlu'
    return
  }

  submitting.value = true
  error.value = ''
  try {
    if (editingPayrollId.value) {
      await personnelApi.updatePayroll(editingPayrollId.value, payrollForm.value)
    } else {
      await personnelApi.createPayroll({
        ...payrollForm.value,
        year: dateRangeFilter.value.year || new Date().getFullYear(),
        month: dateRangeFilter.value.month || new Date().getMonth() + 1
      })
    }
    showPayrollForm.value = false
    await loadPayrolls()
  } catch (e: unknown) {
    error.value = extractErrorMessage(e, 'Kayit basarisiz')
  } finally {
    submitting.value = false
  }
}

async function deletePayroll(id: number) {
  confirmModal.confirm('Bu bordro kaydini silmek istediginize emin misiniz?', async () => {
    try {
      await personnelApi.deletePayroll(id)
      await loadPayrolls()
    } catch (e: unknown) {
      error.value = extractErrorMessage(e, 'Silme basarisiz')
    }
  })
}

// ==================== PART-TIME ====================

async function loadPartTimeCosts() {
  loading.value = true
  error.value = ''
  try {
    const [costsRes, summaryRes] = await Promise.all([
      personnelApi.getPartTimeCosts({
        year: dateRangeFilter.value.year || new Date().getFullYear(),
        month: dateRangeFilter.value.month || new Date().getMonth() + 1
      }),
      personnelApi.getPartTimeSummary({
        year: dateRangeFilter.value.year || new Date().getFullYear(),
        month: dateRangeFilter.value.month || new Date().getMonth() + 1
      })
    ])
    partTimeCosts.value = costsRes.data
    partTimeSummary.value = summaryRes.data
  } catch (e: unknown) {
    error.value = extractErrorMessage(e, 'Part-time giderleri yuklenemedi')
  } finally {
    loading.value = false
  }
}

function openPartTimeForm(cost?: PartTimeCost) {
  if (cost) {
    editingPartTimeId.value = cost.id
    partTimeForm.value = {
      cost_date: cost.cost_date,
      amount: Number(cost.amount),
      notes: cost.notes || ''
    }
  } else {
    editingPartTimeId.value = null
    partTimeForm.value = {
      cost_date: new Date().toISOString().split('T')[0],
      amount: 0,
      notes: ''
    }
  }
  showPartTimeForm.value = true
}

async function submitPartTimeForm() {
  if (partTimeForm.value.amount <= 0) {
    error.value = 'Tutar 0 dan buyuk olmali'
    return
  }

  submitting.value = true
  error.value = ''
  try {
    if (editingPartTimeId.value) {
      await personnelApi.updatePartTimeCost(editingPartTimeId.value, partTimeForm.value)
    } else {
      await personnelApi.createPartTimeCost(partTimeForm.value)
    }
    showPartTimeForm.value = false
    await loadPartTimeCosts()
  } catch (e: unknown) {
    error.value = extractErrorMessage(e, 'Kayit basarisiz')
  } finally {
    submitting.value = false
  }
}

async function deletePartTimeCost(id: number) {
  confirmModal.confirm('Bu kaydi silmek istediginize emin misiniz?', async () => {
    try {
      await personnelApi.deletePartTimeCost(id)
      await loadPartTimeCosts()
    } catch (e: unknown) {
      error.value = extractErrorMessage(e, 'Silme basarisiz')
    }
  })
}

// Aktif full-time personeller (form dropdown için)
const activeEmployees = computed(() => {
  return employees.value.filter(e => !e.is_part_time && e.is_active)
})

// Bordroda kaydi olmayan personeller (uyarı için)
const employeesWithoutPayroll = computed(() => {
  const payrollEmployeeIds = new Set(payrolls.value.map(p => p.employee_id))
  return employees.value.filter(e => !payrollEmployeeIds.has(e.id) && !e.is_part_time && e.is_active)
})

// Tab configuration
const tabs = computed<Tab[]>(() => [
  { id: 'employees', label: 'Personel Listesi', icon: '👤' },
  { id: 'payroll', label: 'Personel Ödemeleri', icon: '💳' },
  { id: 'parttime', label: 'Part-time Giderler', icon: '⏱️' }
])

// Primary action changes based on active tab
const primaryAction = computed(() => {
  switch (activeTab.value) {
    case 'employees':
      return { label: 'Yeni Personel', onClick: openEmployeeForm }
    case 'payroll':
      return { label: 'Ödeme Ekle', onClick: openPayrollForm }
    case 'parttime':
      return { label: 'Part-time Gider Ekle', onClick: openPartTimeForm }
    default:
      return undefined
  }
})

// Employee entity selector config for payroll tab
const employeeEntities = computed<EntityConfig>(() => ({
  items: activeEmployees.value.map(emp => ({
    id: emp.id,
    label: emp.name,
    icon: '👤'
  })),
  allLabel: 'Tüm Personel',
  showSettings: false,
  showCount: false
}))

// Show entity selector only in payroll tab
const showEntitySelector = computed(() => activeTab.value === 'payroll')
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="personnel-header">
      <h1 class="page-title">👤 Personel Yönetimi</h1>
      <p class="page-description">Çalışan bilgileri, maaş ödemeleri ve part-time giderleri</p>
    </div>

    <!-- Error -->
    <ErrorAlert :message="error" @dismiss="error = ''" />

    <!-- Tabs -->
    <TabBar v-model="activeTab" :tabs="tabs" />

    <!-- Unified Filter Bar - Single date filter for all tabs -->
    <UnifiedFilterBar
      v-model:date-range="dateRangeFilter"
      v-model:entity-id="selectedEmployeeFilter"
      :entities="showEntitySelector ? employeeEntities : undefined"
      :primary-action="primaryAction"
    />

    <!-- ==================== EMPLOYEES TAB ==================== -->
    <div v-if="activeTab === 'employees'">
      <div class="bg-white rounded-lg shadow overflow-hidden" data-testid="personnel-list">
        <LoadingState v-if="loading" />

        <div v-else-if="employees.length === 0" class="p-8 text-center text-gray-500">
          Henuz personel eklenmemis
        </div>

        <table v-else class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Isim</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Maas</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">SGK</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">SGK Tutari</th>
              <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Saat Ucret</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Tip</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Islemler</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="emp in sortedEmployees" :key="emp.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ emp.name }}</td>
              <td class="px-4 py-3 text-right text-sm text-gray-900">{{ formatCurrency(emp.base_salary) }}</td>
              <td class="px-4 py-3 text-center text-sm">
                <span :class="emp.has_sgk ? 'text-green-600' : 'text-gray-400'">
                  {{ emp.has_sgk ? 'Var' : 'Yok' }}
                </span>
              </td>
              <td class="px-4 py-3 text-right text-sm text-gray-900">
                {{ emp.has_sgk ? formatCurrency(emp.sgk_amount) : '-' }}
              </td>
              <td class="px-4 py-3 text-right text-sm text-gray-900">{{ formatCurrency(emp.hourly_rate) }}/saat</td>
              <td class="px-4 py-3 text-center text-xs">
                <span :class="[
                  'px-2 py-1 rounded-full',
                  emp.payment_type === 'weekly' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'
                ]">
                  {{ emp.payment_type === 'weekly' ? 'Haftalik' : 'Aylik' }}
                </span>
              </td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center justify-center gap-2">
                  <button @click="openEmployeeForm(emp)"
                    class="text-blue-600 hover:text-blue-800 text-sm">Duzenle</button>
                  <button @click="deleteEmployee(emp.id)" class="text-red-600 hover:text-red-800 text-sm">Sil</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ==================== PAYROLL TAB ==================== -->
    <div v-if="activeTab === 'payroll'">
      <!-- Ozet Kartlari - Satir 1 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
        <div class="bg-white rounded-lg shadow p-3">
          <p class="text-xs text-gray-500">Maas</p>
          <p class="text-lg font-bold text-gray-900">{{ formatCurrency(payrollSummary?.total_base_salary || 0) }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-3">
          <p class="text-xs text-gray-500">SGK</p>
          <p class="text-lg font-bold text-gray-900">{{ formatCurrency(payrollSummary?.total_sgk || 0) }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-3">
          <p class="text-xs text-gray-500">Avans</p>
          <p class="text-lg font-bold text-orange-600">{{ formatCurrency(payrollSummary?.total_advance || 0) }}</p>
        </div>
        <div class="bg-white rounded-lg shadow p-3">
          <p class="text-xs text-gray-500">Mesai + Prim + Ek Od.</p>
          <p class="text-lg font-bold text-gray-900">
            {{ formatCurrency(Number(payrollSummary?.total_overtime || 0) + Number(payrollSummary?.total_premium || 0) +
              Number(payrollSummary?.total_bonus || 0)) }}
          </p>
        </div>
      </div>
      <!-- Ozet Kartlari - Satir 2: Toplam -->
      <div class="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow p-4 mb-6">
        <div class="flex justify-between items-center text-white">
          <div>
            <p class="text-sm opacity-90">Toplam Odeme</p>
            <p class="text-xs opacity-75">{{ payrollSummary?.employee_count || 0 }} kayit</p>
          </div>
          <p class="text-2xl font-bold">{{ formatCurrency(payrollSummary?.total_payroll || 0) }}</p>
        </div>
      </div>

      <!-- Kaydi olmayan personel uyarisi -->
      <div v-if="employeesWithoutPayroll.length > 0" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
        <p class="text-sm text-yellow-800">
          <strong>Bilgi:</strong> Bu ayda henuz odeme kaydi olmayan personeller:
          {{employeesWithoutPayroll.map(e => e.name).join(', ')}}
        </p>
      </div>

      <div class="bg-white rounded-lg shadow overflow-x-auto">
        <LoadingState v-if="loading" />

        <div v-else-if="payrolls.length === 0" class="p-8 text-center text-gray-500">
          Bu ay icin bordro kaydi bulunamadi
        </div>

        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
              <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Personel</th>
              <th class="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase">Tip</th>
              <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase">Maas</th>
              <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase">SGK</th>
              <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase">Ek Od.</th>
              <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase">Prim</th>
              <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase">Mesai</th>
              <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase">Avans</th>
              <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase">Kesinti</th>
              <th class="px-3 py-3 text-right text-xs font-medium text-gray-500 uppercase font-bold">Toplam</th>
              <th class="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase">Islem</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="p in payrolls" :key="p.id" class="hover:bg-gray-50">
              <td class="px-3 py-3 text-sm text-gray-600">{{ formatDate(p.payment_date) }}</td>
              <td class="px-3 py-3 font-medium text-gray-900">{{ p.employee?.name || '-' }}</td>
              <td class="px-3 py-3 text-center">
                <span :class="[
                  'px-2 py-0.5 rounded-full text-xs',
                  p.record_type === 'salary' ? 'bg-green-100 text-green-700' :
                    p.record_type === 'advance' ? 'bg-blue-100 text-blue-700' :
                      p.record_type === 'sgk' ? 'bg-orange-100 text-orange-700' :
                        p.record_type === 'prim' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-purple-100 text-purple-700'
                ]">
                  {{
                    p.record_type === 'salary' ? 'Maas' :
                      p.record_type === 'advance' ? 'Avans' :
                        p.record_type === 'sgk' ? 'SGK' :
                          p.record_type === 'prim' ? 'Prim' :
                            'Haftalik'
                  }}
                </span>
              </td>
              <td class="px-3 py-3 text-right text-gray-900">{{ formatCurrency(p.base_salary) }}</td>
              <td class="px-3 py-3 text-right text-gray-900">{{ formatCurrency(p.sgk_amount) }}</td>
              <td class="px-3 py-3 text-right text-gray-900">{{ formatCurrency(p.bonus) }}</td>
              <td class="px-3 py-3 text-right text-gray-900">{{ formatCurrency(p.premium) }}</td>
              <td class="px-3 py-3 text-right text-gray-900">
                <span v-if="p.overtime_hours > 0" class="text-xs text-gray-500">{{ p.overtime_hours }}s</span>
                {{ formatCurrency(p.overtime_amount) }}
              </td>
              <td class="px-3 py-3 text-right text-orange-600">-{{ formatCurrency(p.advance) }}</td>
              <td class="px-3 py-3 text-right text-red-600">-{{ formatCurrency(p.absence_deduction) }}</td>
              <td class="px-3 py-3 text-right font-bold text-green-600">{{ formatCurrency(p.total) }}</td>
              <td class="px-3 py-3 text-center">
                <button @click="openPayrollForm(p)"
                  class="text-blue-600 hover:text-blue-800 text-xs mr-2">Duzenle</button>
                <button @click="deletePayroll(p.id)" class="text-red-600 hover:text-red-800 text-xs">Sil</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ==================== PART-TIME TAB ==================== -->
    <div v-if="activeTab === 'parttime'">
      <!-- Ozet -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <SummaryCard label="Toplam Gider" :value="formatCurrency(partTimeSummary?.total_cost || 0)" />
        <SummaryCard label="Kayit Sayisi" :value="`${partTimeSummary?.days_count || 0} gun`" variant="primary" />
        <SummaryCard label="Gunluk Ortalama" :value="formatCurrency(partTimeSummary?.avg_daily_cost || 0)"
          variant="info" />
      </div>

      <div class="bg-white rounded-lg shadow overflow-hidden">
        <LoadingState v-if="loading" />

        <div v-else-if="partTimeCosts.length === 0" class="p-8 text-center text-gray-500">
          Bu ay icin part-time gideri bulunamadi
        </div>

        <table v-else class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tarih</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Tutar</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Not</th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Islemler</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="cost in partTimeCosts" :key="cost.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 text-sm text-gray-900">{{ formatDate(cost.cost_date) }}</td>
              <td class="px-6 py-4 text-right font-semibold text-gray-900">{{ formatCurrency(cost.amount) }}</td>
              <td class="px-6 py-4 text-sm text-gray-500">{{ cost.notes || '-' }}</td>
              <td class="px-6 py-4 text-center">
                <button @click="openPartTimeForm(cost)"
                  class="text-blue-600 hover:text-blue-800 text-sm mr-2">Duzenle</button>
                <button @click="deletePartTimeCost(cost.id)"
                  class="text-red-600 hover:text-red-800 text-sm">Sil</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ==================== EMPLOYEE FORM MODAL ==================== -->
    <PageModal :show="showEmployeeForm" :title="editingEmployeeId ? 'Personel Duzenle' : 'Yeni Personel'"
      size="lg"
      @close="showEmployeeForm = false">
      <form @submit.prevent="submitEmployeeForm" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Isim *</label>
          <input v-model="employeeForm.name" data-testid="input-personnel-name" type="text"
            class="w-full border rounded-lg px-3 py-2" required />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Aylik Maas (TL) *</label>
          <input v-model.number="employeeForm.base_salary" data-testid="input-personnel-salary" type="number"
            step="0.01" class="w-full border rounded-lg px-3 py-2" required />
        </div>

        <div class="flex items-center gap-4">
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="employeeForm.has_sgk" type="checkbox" class="rounded text-red-600" />
            <span class="text-sm">SGK Var</span>
          </label>
        </div>

        <div v-if="employeeForm.has_sgk">
          <label class="block text-sm font-medium text-gray-700 mb-1">SGK Tutari (TL)</label>
          <input v-model.number="employeeForm.sgk_amount" type="number" step="0.01"
            class="w-full border rounded-lg px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Saatlik Ucret (Mesai icin)</label>
          <input v-model.number="employeeForm.hourly_rate" type="number" step="0.01"
            class="w-full border rounded-lg px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Odeme Tipi</label>
          <select v-model="employeeForm.payment_type" class="w-full border rounded-lg px-3 py-2">
            <option value="monthly">Aylik</option>
            <option value="weekly">Haftalik</option>
          </select>
        </div>
      </form>

      <template #footer>
        <div class="flex justify-end gap-3">
          <button type="button" @click="showEmployeeForm = false"
            class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100">
            Iptal
          </button>
          <button @click="submitEmployeeForm" data-testid="btn-save-personnel" :disabled="submitting"
            class="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50">
            {{ submitting ? 'Kaydediliyor...' : (editingEmployeeId ? 'Guncelle' : 'Kaydet') }}
          </button>
        </div>
      </template>
    </PageModal>

    <!-- ==================== PAYROLL FORM MODAL ==================== -->
    <PageModal :show="showPayrollForm"
      :title="`${editingPayrollId ? 'Odeme Duzenle' : 'Yeni Odeme'} - ${MONTHS[selectedMonth - 1].label} ${selectedYear}`"
      size="lg" @close="showPayrollForm = false">
      <form @submit.prevent="submitPayrollForm" class="p-6 space-y-4">
        <div v-if="!editingPayrollId">
          <label class="block text-sm font-medium text-gray-700 mb-1">Personel *</label>
          <select v-model.number="payrollForm.employee_id" @change="onEmployeeSelect(payrollForm.employee_id)"
            class="w-full border rounded-lg px-3 py-2" required>
            <option value="0" disabled>Personel Seciniz</option>
            <option v-for="emp in activeEmployees" :key="emp.id" :value="emp.id">
              {{ emp.name }}
            </option>
          </select>
        </div>
        <div v-else class="bg-gray-100 rounded-lg px-3 py-2">
          <span class="text-sm text-gray-500">Personel:</span>
          <span class="font-medium ml-2">{{payrolls.find(p => p.id === editingPayrollId)?.employee?.name}}</span>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Odeme Tarihi *</label>
            <input v-model="payrollForm.payment_date" type="date" class="w-full border rounded-lg px-3 py-2" required />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Odeme Tipi *</label>
            <select v-model="payrollForm.record_type" class="w-full border rounded-lg px-3 py-2" required>
              <option v-for="rt in recordTypes" :key="rt.value" :value="rt.value">{{ rt.label }}</option>
            </select>
          </div>
        </div>

        <!-- AVANS: Sadece avans tutarı -->
        <div v-if="payrollForm.record_type === 'advance'" class="space-y-4">
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p class="text-sm text-blue-700">Avans odemesi - sadece tutar giriniz</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Avans Tutari *</label>
            <input v-model.number="payrollForm.advance" type="number" step="0.01" min="0"
              class="w-full border rounded-lg px-3 py-2 text-lg" required />
          </div>
        </div>

        <!-- MAAS: Sadece maas, sgk, ek odenek, prim -->
        <div v-else-if="payrollForm.record_type === 'salary'" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Maas</label>
              <input v-model.number="payrollForm.base_salary" type="number" step="0.01"
                class="w-full border rounded-lg px-3 py-2" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">SGK</label>
              <input v-model.number="payrollForm.sgk_amount" type="number" step="0.01"
                class="w-full border rounded-lg px-3 py-2" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Ek Odenek</label>
              <input v-model.number="payrollForm.bonus" type="number" step="0.01"
                class="w-full border rounded-lg px-3 py-2" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Prim</label>
              <input v-model.number="payrollForm.premium" type="number" step="0.01"
                class="w-full border rounded-lg px-3 py-2" />
            </div>
          </div>
        </div>

        <!-- HAFTALIK: Basit odeme -->
        <div v-else-if="payrollForm.record_type === 'weekly'" class="space-y-4">
          <div class="bg-purple-50 border border-purple-200 rounded-lg p-3">
            <p class="text-sm text-purple-700">Haftalik odeme - temel tutar ve varsa mesai giriniz</p>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Odeme Tutari</label>
              <input v-model.number="payrollForm.base_salary" type="number" step="0.01"
                class="w-full border rounded-lg px-3 py-2" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Mesai (saat)</label>
              <input v-model.number="payrollForm.overtime_hours" @input="calculateOvertimeAmount" type="number"
                step="0.5" class="w-full border rounded-lg px-3 py-2" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Mesai Tutari</label>
              <input v-model.number="payrollForm.overtime_amount" type="number" step="0.01"
                class="w-full border rounded-lg px-3 py-2 bg-gray-50" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Avans (kesinti)</label>
              <input v-model.number="payrollForm.advance" type="number" step="0.01"
                class="w-full border rounded-lg px-3 py-2" />
            </div>
          </div>
        </div>

        <!-- SGK & PRIM: Tekil tutar girisi -->
        <div v-else-if="['sgk', 'prim'].includes(payrollForm.record_type)" class="space-y-4">
          <div :class="[
            'border rounded-lg p-3',
            payrollForm.record_type === 'sgk' ? 'bg-orange-50 border-orange-200 text-orange-700' : 'bg-yellow-50 border-yellow-200 text-yellow-700'
          ]">
            <p class="text-sm">
              {{ payrollForm.record_type === 'sgk' ? 'SGK Odemesi - tutari giriniz' : 'Prim Odemesi - tutari giriniz' }}
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              {{ payrollForm.record_type === 'sgk' ? 'SGK Tutari' : 'Prim Tutari' }} *
            </label>
            <input v-if="payrollForm.record_type === 'sgk'" v-model.number="payrollForm.sgk_amount" type="number"
              step="0.01" min="0" class="w-full border rounded-lg px-3 py-2 text-lg" required />
            <input v-else v-model.number="payrollForm.premium" type="number" step="0.01" min="0"
              class="w-full border rounded-lg px-3 py-2 text-lg" required />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Not</label>
          <input v-model="payrollForm.notes" type="text" class="w-full border rounded-lg px-3 py-2"
            placeholder="Opsiyonel..." />
        </div>

        <!-- Toplam -->
        <div v-if="payrollForm.record_type === 'advance'" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p class="text-sm text-blue-600">Avans Tutari</p>
          <p class="text-2xl font-bold text-blue-700">{{ formatCurrency(payrollTotal) }}</p>
        </div>
        <div v-else class="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Brut Toplam</span>
            <span class="text-lg font-semibold text-gray-900">{{ formatCurrency(payrollGross) }}</span>
          </div>
          <!-- Ay ici avanslar -->
          <div v-if="employeeMonthlyAdvances > 0" class="flex justify-between items-center text-orange-600">
            <span class="text-sm">Ay Ici Alinan Avans</span>
            <span class="text-lg font-semibold">-{{ formatCurrency(employeeMonthlyAdvances) }}</span>
          </div>
          <!-- Diger kesintiler -->
          <div v-if="payrollForm.advance > 0 || payrollForm.absence_deduction > 0"
            class="flex justify-between items-center text-red-600">
            <span class="text-sm">Diger Kesintiler</span>
            <span class="text-lg font-semibold">-{{ formatCurrency(payrollForm.advance + payrollForm.absence_deduction)
            }}</span>
          </div>
          <!-- Net Odeme -->
          <div class="border-t pt-2 flex justify-between items-center">
            <span class="text-sm text-green-600 font-medium">Odenecek Tutar</span>
            <span class="text-xl font-bold text-green-700">{{ formatCurrency(payrollTotal) }}</span>
          </div>
        </div>

      </form>

      <template #footer>
        <div class="flex justify-end gap-3">
          <button type="button" @click="showPayrollForm = false"
            class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100">
            Iptal
          </button>
          <button @click="submitPayrollForm" :disabled="submitting"
            class="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50">
            {{ submitting ? 'Kaydediliyor...' : (editingPayrollId ? 'Guncelle' : 'Kaydet') }}
          </button>
        </div>
      </template>
    </PageModal>

    <!-- ==================== PART-TIME FORM MODAL ==================== -->
    <PageModal :show="showPartTimeForm" :title="editingPartTimeId ? 'Kayit Duzenle' : 'Part-time Gider Ekle'"
      size="lg"
      @close="showPartTimeForm = false">
      <form @submit.prevent="submitPartTimeForm" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tarih *</label>
          <input v-model="partTimeForm.cost_date" type="date" class="w-full border rounded-lg px-3 py-2" required />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Tutar (TL) *</label>
          <input v-model.number="partTimeForm.amount" type="number" step="0.01" min="0"
            class="w-full border rounded-lg px-3 py-2" required />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Not</label>
          <input v-model="partTimeForm.notes" type="text" class="w-full border rounded-lg px-3 py-2"
            placeholder="Opsiyonel..." />
        </div>
      </form>

      <template #footer>
        <div class="flex justify-end gap-3">
          <button type="button" @click="showPartTimeForm = false"
            class="px-4 py-2 border rounded-lg text-gray-700 hover:bg-gray-100">
            Iptal
          </button>
          <button @click="submitPartTimeForm" :disabled="submitting"
            class="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50">
            {{ submitting ? 'Kaydediliyor...' : (editingPartTimeId ? 'Guncelle' : 'Kaydet') }}
          </button>
        </div>
      </template>
    </PageModal>

    <ConfirmModal :show="confirmModal.isOpen.value" :message="confirmModal.message.value"
      @confirm="confirmModal.handleConfirm" @cancel="confirmModal.handleCancel" />
  </div>
</template>

<style scoped>
.personnel-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  font-family: 'font-display', sans-serif;
  color: #111827;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}
</style>
