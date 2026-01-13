// @smoke
// Phase 1 Task 1.1: Router Restructure Tests
// TDD: These tests define the TARGET route structure from the platform evolution roadmap
// Tests will FAIL until implementation is complete
import { test, expect } from '@playwright/test'
import { config } from '../_config/test_config'

/**
 * TDD Plan for Router Restructure
 * ================================
 *
 * TARGET STRUCTURE (from docs/plans/2025-12-24-platform-evolution-roadmap.md):
 *
 * 📊 Bilanço (/)           - Dashboard (EXISTING)
 * 📥 İçe Aktar (/import)   - Central Import Hub (EXISTING)
 * 💰 Ciro (/sales)         - Sales with /sales/verify
 * 🏭 Operasyon (/operations) - /operations/production, /operations/purchases
 * 👥 Personel (/personnel) - /personnel, /personnel/meals, /personnel/payroll
 * 💸 Giderler (/expenses)  - /expenses, /expenses/courier
 * ⚙️ Ayarlar (/settings)   - Admin settings (EXISTING)
 *
 * IMPLEMENTATION STEPS:
 * 1. Run these tests (all fail - RED)
 * 2. Implement route changes in frontend/src/router/index.ts
 * 3. Run tests again (pass - GREEN)
 * 4. Refactor and clean up legacy routes
 */

test.describe('🛣️ Router Structure - Phase 1', () => {
  let authToken: string

  test.beforeAll(async ({ request }) => {
    // Get auth token once for all tests
    const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', {
      data: {
        email: config.auth.email,
        password: config.auth.password
      }
    })

    if (loginRes.ok()) {
      const loginData = await loginRes.json()
      authToken = loginData.access_token
    }
  })

  test.beforeEach(async ({ page }) => {
    test.setTimeout(30000)

    // Inject token
    await page.goto(config.frontendUrl + '/login')
    await page.evaluate((t) => {
      localStorage.setItem('token', t)
    }, authToken)
  })

  // ==========================================
  // EXISTING ROUTES (should pass)
  // ==========================================

  test.describe('Existing Routes', () => {
    test('/ (Bilanço) - Dashboard loads', async ({ page }) => {
      await page.goto(config.frontendUrl + '/')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/')
      // Dashboard should have KPI cards or main content
      const mainContent = page.locator('.kpi-card, main, [class*="dashboard"]').first()
      await expect(mainContent).toBeVisible({ timeout: 10000 })
    })

    test('/import - Import Hub loads', async ({ page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/import')
    })

    test('/settings - Settings page loads (admin)', async ({ page }) => {
      await page.goto(config.frontendUrl + '/settings')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/settings')
    })
  })

  // ==========================================
  // NEW ROUTES - SALES (/sales)
  // ==========================================

  test.describe('💰 Sales Routes (/sales)', () => {
    test('/sales - Main sales page loads', async ({ page }) => {
      await page.goto(config.frontendUrl + '/sales')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Should not redirect to old /gelirler/kasa
      await expect(page).toHaveURL(config.frontendUrl + '/sales')

      // Should display sales content
      const salesContent = page.locator('[data-testid="sales-page"], .sales-content, main').first()
      await expect(salesContent).toBeVisible({ timeout: 10000 })
    })

    test('/sales/verify - Cash verification page loads', async ({ page }) => {
      await page.goto(config.frontendUrl + '/sales/verify')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/sales/verify')

      // Should display verification content (kasa farkı)
      const verifyContent = page.locator('[data-testid="verify-page"], .verify-content, main').first()
      await expect(verifyContent).toBeVisible({ timeout: 10000 })
    })
  })

  // ==========================================
  // NEW ROUTES - OPERATIONS (/operations)
  // ==========================================

  test.describe('🏭 Operations Routes (/operations)', () => {
    test('/operations - Redirects to /operations/production', async ({ page }) => {
      await page.goto(config.frontendUrl + '/operations')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Should redirect to production by default
      await expect(page).toHaveURL(config.frontendUrl + '/operations/production')
    })

    test('/operations/production - Production page loads', async ({ page }) => {
      await page.goto(config.frontendUrl + '/operations/production')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/operations/production')

      const productionContent = page.locator('[data-testid="production-page"], .production-content, main').first()
      await expect(productionContent).toBeVisible({ timeout: 10000 })
    })

    test('/operations/purchases - Purchases page loads', async ({ page }) => {
      await page.goto(config.frontendUrl + '/operations/purchases')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/operations/purchases')

      const purchasesContent = page.locator('[data-testid="purchases-page"], .purchases-content, main').first()
      await expect(purchasesContent).toBeVisible({ timeout: 10000 })
    })
  })

  // ==========================================
  // NEW ROUTES - PERSONNEL (/personnel)
  // ==========================================

  test.describe('👥 Personnel Routes (/personnel)', () => {
    test('/personnel - Personnel list page loads', async ({ page }) => {
      await page.goto(config.frontendUrl + '/personnel')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/personnel')

      const personnelContent = page.locator('[data-testid="personnel-page"], .personnel-content, main').first()
      await expect(personnelContent).toBeVisible({ timeout: 10000 })
    })

    test('/personnel/meals - Staff meals page loads', async ({ page }) => {
      await page.goto(config.frontendUrl + '/personnel/meals')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/personnel/meals')

      const mealsContent = page.locator('[data-testid="meals-page"], .meals-content, main').first()
      await expect(mealsContent).toBeVisible({ timeout: 10000 })
    })

    test('/personnel/payroll - Payroll page loads', async ({ page }) => {
      await page.goto(config.frontendUrl + '/personnel/payroll')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/personnel/payroll')

      const payrollContent = page.locator('[data-testid="payroll-page"], .payroll-content, main').first()
      await expect(payrollContent).toBeVisible({ timeout: 10000 })
    })
  })

  // ==========================================
  // NEW ROUTES - EXPENSES (/expenses)
  // ==========================================

  test.describe('💸 Expenses Routes (/expenses)', () => {
    test('/expenses - Business expenses page loads', async ({ page }) => {
      await page.goto(config.frontendUrl + '/expenses')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/expenses')

      const expensesContent = page.locator('[data-testid="expenses-page"], .expenses-content, main').first()
      await expect(expensesContent).toBeVisible({ timeout: 10000 })
    })

    test('/expenses/courier - Courier expenses page loads', async ({ page }) => {
      await page.goto(config.frontendUrl + '/expenses/courier')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/expenses/courier')

      const courierContent = page.locator('[data-testid="courier-page"], .courier-content, main').first()
      await expect(courierContent).toBeVisible({ timeout: 10000 })
    })
  })

  // ==========================================
  // LEGACY ROUTE REDIRECTS
  // ==========================================

  test.describe('🔀 Legacy Route Redirects', () => {
    test('/gelirler/kasa redirects to /sales', async ({ page }) => {
      await page.goto(config.frontendUrl + '/gelirler/kasa')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/sales')
    })

    test('/gelirler/kasa-farki redirects to /sales/verify', async ({ page }) => {
      await page.goto(config.frontendUrl + '/gelirler/kasa-farki')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/sales/verify')
    })

    test('/giderler/uretim redirects to /operations/production', async ({ page }) => {
      await page.goto(config.frontendUrl + '/giderler/uretim')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/operations/production')
    })

    test('/giderler/mal-alim redirects to /operations/purchases', async ({ page }) => {
      await page.goto(config.frontendUrl + '/giderler/mal-alim')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/operations/purchases')
    })

    test('/giderler/genel redirects to /expenses', async ({ page }) => {
      await page.goto(config.frontendUrl + '/giderler/genel')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/expenses')
    })

    test('/giderler/hizmet-alim/kurye redirects to /expenses/courier', async ({ page }) => {
      await page.goto(config.frontendUrl + '/giderler/hizmet-alim/kurye')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/expenses/courier')
    })

    test('/giderler/hizmet-alim/personel-iase redirects to /personnel/meals', async ({ page }) => {
      await page.goto(config.frontendUrl + '/giderler/hizmet-alim/personel-iase')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/personnel/meals')
    })
  })

  // ==========================================
  // NAVIGATION TESTS
  // ==========================================

  test.describe('🧭 Navigation', () => {
    test('Sidebar contains all 6 main navigation groups', async ({ page }) => {
      await page.goto(config.frontendUrl + '/')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Check for navigation items (adapt selectors based on actual implementation)
      const navGroups = [
        { label: 'Bilanço', path: '/' },
        { label: 'İçe Aktar', path: '/import' },
        { label: 'Ciro', path: '/sales' },
        { label: 'Operasyon', path: '/operations' },
        { label: 'Personel', path: '/personnel' },
        { label: 'Giderler', path: '/expenses' }
      ]

      for (const group of navGroups) {
        const navItem = page.locator(`nav a[href="${group.path}"], nav button:has-text("${group.label}"), [role="navigation"] a[href="${group.path}"]`).first()
        await expect(navItem).toBeVisible({ timeout: 5000 })
      }
    })

    test('Clicking Ciro navigates to /sales', async ({ page }) => {
      await page.goto(config.frontendUrl + '/')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      const salesNav = page.locator('nav a[href="/sales"], nav button:has-text("Ciro")').first()
      await salesNav.click()

      await expect(page).toHaveURL(config.frontendUrl + '/sales')
    })

    test('Clicking Operasyon expands submenu or navigates', async ({ page }) => {
      await page.goto(config.frontendUrl + '/')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      const operationsNav = page.locator('nav a[href="/operations"], nav button:has-text("Operasyon")').first()
      await operationsNav.click()

      // Should either show submenu or navigate to /operations/production
      await expect(page).toHaveURL(/\/operations/)
    })
  })
})
