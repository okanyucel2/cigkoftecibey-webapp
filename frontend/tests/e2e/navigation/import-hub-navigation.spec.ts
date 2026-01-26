// @smoke
// Import Hub Navigation E2E Tests
// Regression tests for Import Hub → Kasa Farkı navigation bug (fixed 2026-01-05)
// Bug 1: ImportHub.vue linked to /kasa-farki instead of /gelirler/kasa-farki
// Bug 2: Modal didn't auto-open when coming from Import Hub

import { test, expect } from '@playwright/test'
import { config } from '../_config/test_config'

test.describe('📥 Import Hub Navigation', () => {
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
  // IMPORT HUB PAGE TESTS
  // ==========================================

  test.describe('Import Hub Page', () => {
    test('Import Hub page loads correctly', async ({ page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/import')
      await expect(page.locator('[data-testid="import-hub-page"]')).toBeVisible()
      await expect(page.locator('[data-testid="import-hub-title"]')).toContainText('Import Hub')
    })

    test('Kasa Raporu import button is visible', async ({ page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      const importButton = page.locator('[data-testid="import-hub-kasa-raporu-btn"]')
      await expect(importButton).toBeVisible()
      await expect(importButton).toContainText('Import Et')
    })
  })

  // ==========================================
  // CRITICAL: NAVIGATION BUG REGRESSION TESTS
  // ==========================================

  test.describe('🔴 CRITICAL: Kasa Raporu Navigation', () => {
    test('Clicking "Import Et" navigates to /sales/verify', async ({ page }) => {
      // ImportHub.vue links to /sales/verify?import=true (Phase 1 route structure)

      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Find and click the Import Et button
      const importButton = page.locator('[data-testid="import-hub-kasa-raporu-btn"]')
      await expect(importButton).toBeVisible()
      await importButton.click()

      // Wait for navigation
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Should navigate to /sales/verify (query param gets cleaned up after modal opens)
      await expect(page).toHaveURL(config.frontendUrl + '/sales/verify')
    })

    test('Gelirler page shows Kasa Farkı tab when navigating from Import Hub', async ({ page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Click Import Et
      await page.locator('[data-testid="import-hub-kasa-raporu-btn"]').click()
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Verify Gelirler page loaded with Kasa Farkı tab
      await expect(page.locator('[data-testid="gelirler-page"]')).toBeVisible()
      await expect(page.locator('[data-testid="gelirler-tab-kasa-farki"]')).toBeVisible()
    })

    test('Direct navigation to /sales/verify shows Kasa Farkı content', async ({ page }) => {
      await page.goto(config.frontendUrl + '/sales/verify')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/sales/verify')
      await expect(page.locator('[data-testid="gelirler-page"]')).toBeVisible()
      await expect(page.locator('[data-testid="gelirler-tab-kasa-farki"]')).toBeVisible()
    })
  })

  // ==========================================
  // CRITICAL: MODAL AUTO-OPEN TESTS
  // ==========================================

  test.describe('🔴 CRITICAL: Import Modal Auto-Open', () => {
    test('Import Et opens Kasa Farkı modal automatically', async ({ page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Click Import Et
      await page.locator('[data-testid="import-hub-kasa-raporu-btn"]').click()

      // Wait for navigation AND modal
      await page.waitForURL('**/sales/verify**')
      await page.waitForTimeout(500) // Allow modal animation

      // CRITICAL: Modal should be visible with correct title
      const modalTitle = page.locator('text=Kasa Farki - Veri Yukleme')
      await expect(modalTitle).toBeVisible({ timeout: 5000 })
    })

    test('Import modal shows Excel upload section', async ({ page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await page.locator('[data-testid="import-hub-kasa-raporu-btn"]').click()
      await page.waitForURL('**/sales/verify**')
      await page.waitForTimeout(500)

      // Modal should have Excel upload section
      const excelSection = page.locator('text=Excel Kasa Raporu').or(page.locator('text=excel'))
      await expect(excelSection.first()).toBeVisible({ timeout: 5000 })
    })

    test('Direct navigation with ?import=true opens modal', async ({ page }) => {
      // Test direct URL with query param
      await page.goto(config.frontendUrl + '/sales/verify?import=true')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
      await page.waitForTimeout(500)

      // Modal should auto-open
      const modalTitle = page.locator('text=Kasa Farki - Veri Yukleme')
      await expect(modalTitle).toBeVisible({ timeout: 5000 })

      // URL should be cleaned up (no query param)
      await expect(page).toHaveURL(config.frontendUrl + '/sales/verify')
    })

    test('Direct navigation without ?import=true does NOT auto-open modal', async ({ page }) => {
      await page.goto(config.frontendUrl + '/sales/verify')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
      await page.waitForTimeout(500)

      // Modal should NOT be visible
      const modalTitle = page.locator('text=Kasa Farki - Veri Yukleme')
      await expect(modalTitle).not.toBeVisible()
    })
  })

  // ==========================================
  // NAVIGATION FLOW TESTS
  // ==========================================

  test.describe('Import Hub Navigation Flow', () => {
    test('Full flow: Dashboard → Import Hub → Kasa Farkı → Modal', async ({ page }) => {
      // Start at dashboard
      await page.goto(config.frontendUrl + '/')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Navigate to Import Hub via sidebar or direct URL
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page.locator('[data-testid="import-hub-page"]')).toBeVisible()

      // Click Import Et for Kasa Raporu
      await page.locator('[data-testid="import-hub-kasa-raporu-btn"]').click()
      await page.waitForURL('**/sales/verify**')
      await page.waitForTimeout(500)

      // Verify we're on Gelirler page with Kasa Farkı tab AND modal is open
      await expect(page.locator('[data-testid="gelirler-page"]')).toBeVisible()
      await expect(page.locator('text=Kasa Farki - Veri Yukleme')).toBeVisible({ timeout: 5000 })
    })

    test('Import Hub "Import Et" button has correct href with query param', async ({ page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      const importButton = page.locator('[data-testid="import-hub-kasa-raporu-btn"]')

      // Verify the href includes query param for modal auto-open (Phase 1 route)
      const href = await importButton.getAttribute('href')
      expect(href).toBe('/sales/verify?import=true')
      expect(href).not.toBe('/kasa-farki')
    })
  })

  // ==========================================
  // VISUAL VERIFICATION (Screenshots)
  // ==========================================

  test.describe('📸 Visual Verification', () => {
    test('Import flow visual verification', async ({ page }) => {
      // Step 1: Import Hub page
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
      await page.screenshot({ path: 'test-results/01-import-hub.png', fullPage: true })

      // Step 2: After clicking Import Et
      await page.locator('[data-testid="import-hub-kasa-raporu-btn"]').click()
      await page.waitForURL('**/sales/verify**')
      await page.waitForTimeout(1000) // Allow modal animation
      await page.screenshot({ path: 'test-results/02-after-click.png', fullPage: true })

      // Step 3: Verify modal is visible
      const modal = page.locator('text=Kasa Farki - Veri Yukleme')
      await expect(modal).toBeVisible({ timeout: 5000 })
      await page.screenshot({ path: 'test-results/03-modal-open.png', fullPage: true })
    })
  })

  // ==========================================
  // ROUTE REDIRECT TESTS
  // ==========================================

  test.describe('Route Redirects', () => {
    test('/kasa-farki should redirect to /sales/verify (legacy)', async ({ page }) => {
      // This documents the existing behavior - /kasa-farki redirects elsewhere
      // The Import Hub should NOT use this route!
      await page.goto(config.frontendUrl + '/kasa-farki')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // /kasa-farki redirects to /sales/verify (which is why the bug was problematic)
      await expect(page).toHaveURL(config.frontendUrl + '/sales/verify')
    })
  })
})
