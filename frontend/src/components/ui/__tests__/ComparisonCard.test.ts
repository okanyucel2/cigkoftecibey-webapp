/**
 * Unit Tests for ComparisonCard Component
 * Task 7: Bilanco Comparison View Implementation
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ComparisonCard from '../ComparisonCard.vue'
import type { BilancoPeriodData } from '@/types/comparison'

describe('ComparisonCard', () => {
  // Mock data for testing
  const mockData: BilancoPeriodData = {
    period_label: 'Bugün',
    start_date: '2025-01-15',
    end_date: '2025-01-15',
    revenue_breakdown: {
      visa: 15000,
      nakit: 8500,
      online: 12000
    },
    total_revenue: 35500,
    expense_breakdown: {
      mal_alimi: 12000,
      gider: 3500,
      staff: 2500,
      kurye: 1800,
      parttime: 1500,
      uretim: 2200
    },
    total_expenses: 23500,
    net_profit: 12000,
    profit_margin: 33.8
  }

  const mockDataLoss: BilancoPeriodData = {
    period_label: 'Dün',
    start_date: '2025-01-14',
    end_date: '2025-01-14',
    revenue_breakdown: {
      visa: 12000,
      nakit: 7000,
      online: 10000
    },
    total_revenue: 29000,
    expense_breakdown: {
      mal_alimi: 11000,
      gider: 3200,
      staff: 2300,
      kurye: 1600,
      parttime: 1400,
      uretim: 2000
    },
    total_expenses: 21500,
    net_profit: 7500,
    profit_margin: 25.9
  }

  const mockDataNegativeProfit: BilancoPeriodData = {
    period_label: 'Kayıp Hafta',
    start_date: '2025-01-08',
    end_date: '2025-01-14',
    revenue_breakdown: {
      visa: 8000,
      nakit: 4000,
      online: 6000
    },
    total_revenue: 18000,
    expense_breakdown: {
      mal_alimi: 10000,
      gider: 3000,
      staff: 2000,
      kurye: 1500,
      parttime: 1000,
      uretim: 1800
    },
    total_expenses: 19300,
    net_profit: -1300,
    profit_margin: -7.2
  }

  describe('Component Rendering', () => {
    it('should render the component correctly', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should display the period label', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      const label = wrapper.find('.text-lg.font-semibold')
      expect(label.text()).toBe('Bugün')
    })

    it('should display date range correctly for single day', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      const dateDisplay = wrapper.find('.text-xs.text-gray-400')
      // Single day should show formatted date
      expect(dateDisplay.exists()).toBe(true)
    })

    it('should display date range correctly for multiple days', () => {
      const multiDayData: BilancoPeriodData = {
        ...mockData,
        start_date: '2025-01-01',
        end_date: '2025-01-07'
      }

      const wrapper = mount(ComparisonCard, {
        props: {
          data: multiDayData,
          position: 'left'
        }
      })

      const dateDisplay = wrapper.find('.text-xs.text-gray-400')
      expect(dateDisplay.exists()).toBe(true)
      expect(dateDisplay.text()).toContain('-')
    })
  })

  describe('Revenue Channels Display', () => {
    it('should display all three revenue channels', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      // Should have Visa, Nakit, and Online channels
      expect(wrapper.text()).toContain('Visa')
      expect(wrapper.text()).toContain('Nakit')
      expect(wrapper.text()).toContain('Online')
    })

    it('should format revenue values as currency', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      const text = wrapper.text()

      // Turkish Lira format uses ₺ symbol
      expect(text).toContain('₺')
      expect(text).toContain('15.000') // Visa amount approx
      expect(text).toContain('8.500')  // Nakit amount approx
      expect(text).toContain('12.000') // Online amount approx
    })

    it('should display total revenue prominently', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      const text = wrapper.text()
      expect(text).toContain('Toplam Ciro')
      expect(text).toContain('35.500') // Total revenue formatted
    })

    it('should apply correct styling to total revenue section', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      // Total revenue should have green gradient background
      const totalRevenueSection = wrapper.findAll('.bg-gradient-to-br').find(el =>
        el.classes().includes('from-green-50')
      )

      expect(totalRevenueSection).toBeDefined()
    })
  })

  describe('Expenses Display', () => {
    it('should display all expense categories', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      const text = wrapper.text()

      // Should have all expense categories
      expect(text).toContain('Mal Alimi')
      expect(text).toContain('Isletme Giderleri')
      expect(text).toContain('Personel Yemekleri')
      expect(text).toContain('Kurye')
      expect(text).toContain('Part-Time')
      expect(text).toContain('Uretim')
    })

    it('should format expense values as currency', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      const text = wrapper.text()
      expect(text).toContain('₺')
      expect(text).toContain('12.000') // Mal alimi
      expect(text).toContain('3.500')  // Gider
    })

    it('should display total expenses prominently', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      const text = wrapper.text()
      expect(text).toContain('Toplam Gider')
      expect(text).toContain('23.500') // Total expenses formatted
    })

    it('should apply correct styling to total expenses section', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      // Total expenses should have orange gradient background
      const totalExpensesSection = wrapper.findAll('.bg-gradient-to-br').find(el =>
        el.classes().includes('from-orange-50')
      )

      expect(totalExpensesSection).toBeDefined()
    })
  })

  describe('Net Profit Display', () => {
    it('should display net profit amount', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      const text = wrapper.text()
      expect(text).toContain('Net Kar')
      expect(text).toContain('12.000') // Net profit formatted
    })

    it('should display profit margin percentage', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      const text = wrapper.text()
      expect(text).toContain('Karlilik')
      expect(text).toContain('%34') // Rounded profit margin
    })

    it('should use blue styling for positive profit', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      // Positive profit should have blue gradient
      const profitSection = wrapper.findAll('.bg-gradient-to-br').find(el =>
        el.classes().includes('from-blue-50')
      )

      expect(profitSection).toBeDefined()
    })

    it('should use red styling for negative profit', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockDataNegativeProfit,
          position: 'right'
        }
      })

      // Negative profit should have red gradient
      const profitSection = wrapper.findAll('.bg-gradient-to-br').find(el =>
        el.classes().includes('from-red-50')
      )

      expect(profitSection).toBeDefined()
    })

    it('should display negative profit amount correctly', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockDataNegativeProfit,
          position: 'right'
        }
      })

      const text = wrapper.text()
      // Turkish currency format for negative uses - sign
      expect(text).toContain('-') // Negative sign
      expect(text).toContain('1.300') // Amount (without checking exact format)
    })
  })

  describe('Profit Margin Color Coding', () => {
    it('should use green color for profit margin >= 50%', () => {
      const highMarginData: BilancoPeriodData = {
        ...mockData,
        profit_margin: 55.0
      }

      const wrapper = mount(ComparisonCard, {
        props: {
          data: highMarginData,
          position: 'left'
        }
      })

      // Should have text-green-600 class for high margin
      const marginElement = wrapper.findAll('.text-xs').find(el =>
        el.text().includes('Karlilik') && el.classes().includes('text-green-600')
      )

      expect(marginElement).toBeDefined()
    })

    it('should use yellow color for profit margin >= 30% and < 50%', () => {
      const mediumMarginData: BilancoPeriodData = {
        ...mockData,
        profit_margin: 33.8
      }

      const wrapper = mount(ComparisonCard, {
        props: {
          data: mediumMarginData,
          position: 'left'
        }
      })

      // Should have text-yellow-600 class for medium margin
      const marginElement = wrapper.findAll('.text-xs').find(el =>
        el.text().includes('Karlilik') && el.classes().includes('text-yellow-600')
      )

      expect(marginElement).toBeDefined()
    })

    it('should use red color for profit margin < 30%', () => {
      const lowMarginData: BilancoPeriodData = {
        ...mockData,
        profit_margin: 25.9
      }

      const wrapper = mount(ComparisonCard, {
        props: {
          data: lowMarginData,
          position: 'left'
        }
      })

      // Should have text-red-600 class for low margin
      const marginElement = wrapper.findAll('.text-xs').find(el =>
        el.text().includes('Karlilik') && el.classes().includes('text-red-600')
      )

      expect(marginElement).toBeDefined()
    })
  })

  describe('Position Prop', () => {
    it('should accept left position', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should accept right position', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'right'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should render correctly for both positions', () => {
      const leftWrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      const rightWrapper = mount(ComparisonCard, {
        props: {
          data: mockDataLoss,
          position: 'right'
        }
      })

      expect(leftWrapper.exists()).toBe(true)
      expect(rightWrapper.exists()).toBe(true)
    })
  })

  describe('Currency Formatting', () => {
    it('should format large numbers with Turkish locale', () => {
      const largeData: BilancoPeriodData = {
        ...mockData,
        total_revenue: 1234567
      }

      const wrapper = mount(ComparisonCard, {
        props: {
          data: largeData,
          position: 'left'
        }
      })

      const text = wrapper.text()
      // Turkish format uses dot as thousand separator
      expect(text).toContain('1.234.567')
    })

    it('should round to whole numbers (no decimal places)', () => {
      const decimalData: BilancoPeriodData = {
        ...mockData,
        total_revenue: 35500.67,
        profit_margin: 33.86
      }

      const wrapper = mount(ComparisonCard, {
        props: {
          data: decimalData,
          position: 'left'
        }
      })

      const text = wrapper.text()
      // Should be rounded, no decimals for currency
      expect(text).toContain('35.501') // Rounded
      // Profit margin is rounded in display
      expect(text).toContain('%34') // Rounded percentage
    })
  })

  describe('Layout and Structure', () => {
    it('should have consistent card structure', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      // Should have main card container
      const card = wrapper.find('.bg-white.rounded-xl')
      expect(card.exists()).toBe(true)

      // Should have shadow and border
      expect(card.classes()).toContain('shadow-sm')
      expect(card.classes()).toContain('border')
    })

    it('should organize sections in correct order', () => {
      const wrapper = mount(ComparisonCard, {
        props: {
          data: mockData,
          position: 'left'
        }
      })

      const html = wrapper.html()

      // Check order of sections (simplified check)
      const headerIndex = html.indexOf('Bugün')
      const revenueIndex = html.indexOf('Ciro Kanallari')
      const totalRevenueIndex = html.indexOf('Toplam Ciro')
      const expenseIndex = html.indexOf('Gider Detaylari')
      const totalExpenseIndex = html.indexOf('Toplam Gider')
      const profitIndex = html.indexOf('Net Kar')

      expect(headerIndex).toBeLessThan(revenueIndex)
      expect(revenueIndex).toBeLessThan(totalRevenueIndex)
      expect(totalRevenueIndex).toBeLessThan(expenseIndex)
      expect(expenseIndex).toBeLessThan(totalExpenseIndex)
      expect(totalExpenseIndex).toBeLessThan(profitIndex)
    })
  })

  describe('Edge Cases', () => {
    it('should handle zero values', () => {
      const zeroData: BilancoPeriodData = {
        period_label: 'Empty Period',
        start_date: '2025-01-01',
        end_date: '2025-01-01',
        revenue_breakdown: {
          visa: 0,
          nakit: 0,
          online: 0
        },
        total_revenue: 0,
        expense_breakdown: {
          mal_alimi: 0,
          gider: 0,
          staff: 0,
          kurye: 0,
          parttime: 0,
          uretim: 0
        },
        total_expenses: 0,
        net_profit: 0,
        profit_margin: 0
      }

      const wrapper = mount(ComparisonCard, {
        props: {
          data: zeroData,
          position: 'left'
        }
      })

      expect(wrapper.exists()).toBe(true)
      const text = wrapper.text()
      expect(text).toContain('₺0')
    })

    it('should handle very small margins', () => {
      const tinyMarginData: BilancoPeriodData = {
        ...mockData,
        profit_margin: 0.5 // Very small positive margin
      }

      const wrapper = mount(ComparisonCard, {
        props: {
          data: tinyMarginData,
          position: 'left'
        }
      })

      // Should render without error
      expect(wrapper.exists()).toBe(true)

      // Should show red color for < 30%
      const marginElement = wrapper.findAll('.text-xs').find(el =>
        el.text().includes('Karlilik') && el.classes().includes('text-red-600')
      )

      expect(marginElement).toBeDefined()
    })

    it('should handle negative profit margins', () => {
      const negativeMarginData: BilancoPeriodData = {
        ...mockDataNegativeProfit,
        profit_margin: -7.2
      }

      const wrapper = mount(ComparisonCard, {
        props: {
          data: negativeMarginData,
          position: 'left'
        }
      })

      // Should render without error
      expect(wrapper.exists()).toBe(true)

      // Should show red color for < 30% (including negative)
      const marginElement = wrapper.findAll('.text-xs').find(el =>
        el.text().includes('Karlilik') && el.classes().includes('text-red-600')
      )

      expect(marginElement).toBeDefined()
    })
  })
})
