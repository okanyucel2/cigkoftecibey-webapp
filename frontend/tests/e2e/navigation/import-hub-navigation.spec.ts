// @smoke
// Import Hub Navigation E2E Tests
// Regression tests for Import Hub → Kasa Farkı navigation bug (fixed 2026-01-05)
// Bug: ImportHub.vue linked to /kasa-farki instead of /gelirler/kasa-farki

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
    test('Clicking "Import Et" navigates to /gelirler/kasa-farki (NOT /kasa-farki)', async ({ page }) => {
      // This test catches the exact bug: ImportHub.vue was linking to /kasa-farki
      // which redirected to /sales/verify (wrong) instead of /gelirler/kasa-farki (correct)

      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Find and click the Import Et button
      const importButton = page.locator('[data-testid="import-hub-kasa-raporu-btn"]')
      await expect(importButton).toBeVisible()
      await importButton.click()

      // Wait for navigation
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // CRITICAL: Should navigate to /gelirler/kasa-farki, NOT /sales/verify
      await expect(page).toHaveURL(config.frontendUrl + '/gelirler/kasa-farki')
    })

    test('Gelirler page shows Kasa Farkı tab when navigating from Import Hub', async ({ page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Click Import Et
      await page.locator('[data-testid="import-hub-kasa-raporu-btn"]').click()
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Verify Gelirler page loaded with correct tab
      await expect(page.locator('[data-testid="gelirler-page"]')).toBeVisible()
      await expect(page.locator('[data-testid="gelirler-tab-kasa-farki"]')).toBeVisible()
    })

    test('Direct navigation to /gelirler/kasa-farki shows Kasa Farkı content', async ({ page }) => {
      await page.goto(config.frontendUrl + '/gelirler/kasa-farki')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page).toHaveURL(config.frontendUrl + '/gelirler/kasa-farki')
      await expect(page.locator('[data-testid="gelirler-page"]')).toBeVisible()
      await expect(page.locator('[data-testid="gelirler-tab-kasa-farki"]')).toBeVisible()
    })
  })

  // ==========================================
  // NAVIGATION FLOW TESTS
  // ==========================================

  test.describe('Import Hub Navigation Flow', () => {
    test('Full flow: Dashboard → Import Hub → Kasa Farkı', async ({ page }) => {
      // Start at dashboard
      await page.goto(config.frontendUrl + '/')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Navigate to Import Hub via sidebar or direct URL
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      await expect(page.locator('[data-testid="import-hub-page"]')).toBeVisible()

      // Click Import Et for Kasa Raporu
      await page.locator('[data-testid="import-hub-kasa-raporu-btn"]').click()
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Verify we're on Gelirler page with Kasa Farkı tab
      await expect(page).toHaveURL(config.frontendUrl + '/gelirler/kasa-farki')
      await expect(page.locator('[data-testid="gelirler-page"]')).toBeVisible()
    })

    test('Import Hub "Import Et" button has correct href attribute', async ({ page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      const importButton = page.locator('[data-testid="import-hub-kasa-raporu-btn"]')

      // Verify the href is correct (not /kasa-farki)
      const href = await importButton.getAttribute('href')
      expect(href).toBe('/gelirler/kasa-farki')
      expect(href).not.toBe('/kasa-farki')
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
