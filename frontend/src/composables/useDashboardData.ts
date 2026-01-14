import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { reportsApi } from '@/services/api'
import type { DashboardComparison } from '@/types'

export interface DashboardData {
  todaySales: {
    total: number
    salon: number
    telefon: number
    online: number
  }
  todayExpenses: {
    purchases: number
    expenses: number
    staffMeals: number
    courier: number
    partTime: number
  }
  todayProfit: number
  cashDifference: number
  laborCostPercent: number
  legenCount: number
  onlineBreakdown: Record<string, number>
  comparison: DashboardComparison | null
}

export function useDashboardData() {
  const data = ref<DashboardData | null>(null)
  const loading = ref(true)
  const error = ref<string | null>(null)

  const netCiro = computed(() => data.value?.todaySales.total ?? 0)
  const kasaFarki = computed(() => data.value?.cashDifference ?? 0)
  const iscilikOrani = computed(() => data.value?.laborCostPercent ?? 0)
  const legenCiro = computed(() => {
    if (!data.value || data.value.legenCount === 0) return 0
    return Math.round(data.value.todaySales.total / data.value.legenCount)
  })

  const totalExpenses = computed(() => {
    if (!data.value) return 0
    const exp = data.value.todayExpenses
    return exp.purchases + exp.expenses + exp.staffMeals + exp.courier + exp.partTime
  })

  async function fetchDashboardData() {
    loading.value = true
    error.value = null

    try {
      // Fetch main dashboard data (api.ts baseURL already includes /api)
      const dashboardRes = await api.get('/reports/dashboard')
      const dashboardData = dashboardRes.data

      // Fetch cash difference
      let cashDiff = 0
      try {
        const cashRes = await api.get('/cash-difference', {
          params: { date: new Date().toISOString().split('T')[0] }
        })
        cashDiff = cashRes.data?.difference ?? 0
      } catch {
        // Cash difference may not exist for today
      }

      // Fetch production (legen count)
      let legenCount = 0
      try {
        const productionRes = await api.get('/production', {
          params: { date: new Date().toISOString().split('T')[0] }
        })
        legenCount = productionRes.data?.reduce(
          (sum: number, p: { legen_count: number }) => sum + (p.legen_count || 0),
          0
        )
      } catch {
        // Production may not exist for today
      }

      // Fetch comparison data for trend badges
      let comparison: DashboardComparison | null = null
      try {
        const comparisonRes = await reportsApi.getComparison()
        comparison = comparisonRes.data
      } catch {
        // Comparison may fail if no previous data exists
      }

      // Calculate labor cost percentage
      // Labor = (Part-time + Monthly Payroll/30) / Revenue
      const partTimeCost = dashboardData.today_expenses?.part_time ?? 0
      const revenue = dashboardData.today_sales?.total ?? 1 // Avoid division by zero
      const laborCostPercent = Math.round((partTimeCost / revenue) * 100)

      data.value = {
        todaySales: {
          total: dashboardData.today_sales?.total ?? 0,
          salon: dashboardData.today_sales?.salon ?? 0,
          telefon: dashboardData.today_sales?.telefon ?? 0,
          online: dashboardData.today_sales?.online ?? 0
        },
        todayExpenses: {
          purchases: dashboardData.today_expenses?.purchases ?? 0,
          expenses: dashboardData.today_expenses?.expenses ?? 0,
          staffMeals: dashboardData.today_expenses?.staff_meals ?? 0,
          courier: dashboardData.today_expenses?.courier ?? 0,
          partTime: dashboardData.today_expenses?.part_time ?? 0
        },
        todayProfit: dashboardData.today_profit ?? 0,
        cashDifference: cashDiff,
        laborCostPercent,
        legenCount,
        onlineBreakdown: dashboardData.online_breakdown ?? {},
        comparison
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load dashboard data'
    } finally {
      loading.value = false
    }
  }

  function refresh() {
    fetchDashboardData()
  }

  onMounted(() => {
    fetchDashboardData()
  })

  return {
    data,
    loading,
    error,
    netCiro,
    kasaFarki,
    iscilikOrani,
    legenCiro,
    totalExpenses,
    refresh
  }
}
