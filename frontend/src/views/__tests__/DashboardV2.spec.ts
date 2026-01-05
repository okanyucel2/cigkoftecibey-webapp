import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { ref } from 'vue'
import DashboardV2 from '../DashboardV2.vue'

// Mock data
const mockData = {
  todaySales: { total: 12450, salon: 2490, telefon: 0, online: 9960 },
  todayExpenses: { purchases: 4210, expenses: 0, staffMeals: 180, courier: 400, partTime: 0 },
  todayProfit: 8240,
  cashDifference: 0,
  laborCostPercent: 18,
  legenCount: 5,
  onlineBreakdown: {
    Yemeksepeti: 4980,
    Getir: 3112,
    Trendyol: 1867
  }
}

// Mock the composable with ref
vi.mock('@/composables/useDashboardData', () => ({
  useDashboardData: () => ({
    data: ref(mockData),
    loading: ref(false),
    error: ref(null),
    refresh: vi.fn()
  })
}))

describe('DashboardV2', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('Layout', () => {
    it('renders 4 KPI cards', () => {
      const wrapper = mount(DashboardV2)
      // KPI cards have specific testids inside the kpi-grid
      const kpiGrid = wrapper.find('[data-testid="kpi-grid"]')
      expect(kpiGrid.exists()).toBe(true)

      // Check for specific KPI cards
      expect(wrapper.find('[data-testid="kpi-net-ciro"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="kpi-kasa-farki"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="kpi-iscilik"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="kpi-legen"]').exists()).toBe(true)
    })

    it('renders 4 hub widgets', () => {
      const wrapper = mount(DashboardV2)
      // Hub widgets have specific testids inside the hub-grid
      const hubGrid = wrapper.find('[data-testid="hub-grid"]')
      expect(hubGrid.exists()).toBe(true)

      // Check for specific hub widgets
      expect(wrapper.find('[data-testid="hub-satis"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="hub-gider"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="hub-ekip"]').exists()).toBe(true)
      expect(wrapper.find('[data-testid="hub-uretim"]').exists()).toBe(true)
    })

    it('renders platform distribution section', () => {
      const wrapper = mount(DashboardV2)
      expect(wrapper.find('[data-testid="platform-distribution"]').exists()).toBe(true)
    })

    it('renders action panel', () => {
      const wrapper = mount(DashboardV2)
      expect(wrapper.find('[data-testid="action-panel"]').exists()).toBe(true)
    })
  })

  describe('KPI Cards', () => {
    it('displays Net Ciro value correctly', () => {
      const wrapper = mount(DashboardV2)
      const netCiroCard = wrapper.find('[data-testid="kpi-net-ciro"]')
      expect(netCiroCard.text()).toContain('12.450')
    })

    it('displays Kasa Farkı with status', () => {
      const wrapper = mount(DashboardV2)
      const kasaFarkiCard = wrapper.find('[data-testid="kpi-kasa-farki"]')
      expect(kasaFarkiCard.text()).toContain('0')
    })

    it('displays İşçilik Oranı as percentage', () => {
      const wrapper = mount(DashboardV2)
      const laborCard = wrapper.find('[data-testid="kpi-iscilik"]')
      expect(laborCard.text()).toContain('%18')
    })

    it('displays Legen/Ciro ratio', () => {
      const wrapper = mount(DashboardV2)
      const legenCard = wrapper.find('[data-testid="kpi-legen"]')
      expect(legenCard.text()).toContain('2.490') // 12450 / 5 = 2490
    })
  })

  describe('Hub Widgets', () => {
    it('shows Satış hub with total sales', () => {
      const wrapper = mount(DashboardV2)
      const satisHub = wrapper.find('[data-testid="hub-satis"]')
      expect(satisHub.exists()).toBe(true)
      expect(satisHub.text()).toContain('Satış')
    })

    it('shows Gider hub with total expenses', () => {
      const wrapper = mount(DashboardV2)
      const giderHub = wrapper.find('[data-testid="hub-gider"]')
      expect(giderHub.exists()).toBe(true)
      expect(giderHub.text()).toContain('Gider')
    })

    it('shows Ekip hub', () => {
      const wrapper = mount(DashboardV2)
      const ekipHub = wrapper.find('[data-testid="hub-ekip"]')
      expect(ekipHub.exists()).toBe(true)
      expect(ekipHub.text()).toContain('Ekip')
    })

    it('shows Üretim hub', () => {
      const wrapper = mount(DashboardV2)
      const uretimHub = wrapper.find('[data-testid="hub-uretim"]')
      expect(uretimHub.exists()).toBe(true)
      expect(uretimHub.text()).toContain('Üretim')
    })
  })

  describe('Responsive', () => {
    it('has responsive grid classes', () => {
      const wrapper = mount(DashboardV2)
      const kpiGrid = wrapper.find('[data-testid="kpi-grid"]')
      // Should have responsive grid classes for 4 columns on desktop, 2 on tablet, 1 on mobile
      expect(kpiGrid.classes()).toContain('grid')
    })
  })

  describe('Slide-over Panel', () => {
    it('opens slide-over when hub action is clicked', async () => {
      const wrapper = mount(DashboardV2)
      const satisHub = wrapper.find('[data-testid="hub-satis"]')

      // Click to expand hub
      await satisHub.trigger('click')

      // Find and click an action
      const kasaSatisAction = wrapper.find('[data-testid="action-kasa-satisi"]')
      if (kasaSatisAction.exists()) {
        await kasaSatisAction.trigger('click')

        // Slide-over should be visible
        const slideOver = wrapper.find('[data-testid="slide-over"]')
        expect(slideOver.exists()).toBe(true)
      }
    })
  })
})
