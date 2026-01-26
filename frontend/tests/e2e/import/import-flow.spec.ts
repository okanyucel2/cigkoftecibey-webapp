// @smoke
// Task 5: Import Flow E2E Tests (TASK-4c634472)
// TDD: Tests written for Import Hub functionality
//
// NOTE: Uses mock-auth fixture for local dev speed (no Docker required)
// Constraint: Do NOT use TenantIsolationHelper - use mock-auth only

import { test, expect } from '../fixtures/mock-auth'
import { config } from '../_config/test_config'

/**
 * Import Flow E2E Tests
 * =====================
 *
 * Tests the complete import flow:
 * 1. Navigate to Import Hub via Operations submenu
 * 2. Verify import options are visible
 * 3. Test Processing state (optimistic UI)
 * 4. Test Completed status after success
 * 5. Test history table displays correctly
 */

test.describe('📥 Import Flow - Central Import Hub', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    test.setTimeout(30000)
  })

  // ==========================================
  // NAVIGATION TESTS
  // ==========================================

  test.describe('Navigation to Import Hub', () => {
    test('Navigate to Import Hub via top-level İçe Aktar button', async ({ authenticatedPage: page }) => {
      // Go to dashboard first
      await page.goto(config.frontendUrl + '/')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // İçe Aktar is a top-level nav item (not under Operasyon)
      const importBtn = page.locator('.nav-button:has-text("İçe Aktar")')
      await expect(importBtn).toBeVisible({ timeout: 5000 })
      await importBtn.click()

      // Should navigate to /import
      await expect(page).toHaveURL(config.frontendUrl + '/import')

      // Import Hub page should be visible
      const importHubPage = page.locator('[data-testid="import-hub-page"]')
      await expect(importHubPage).toBeVisible({ timeout: 5000 })
    })

    test('Import Hub title is displayed correctly', async ({ authenticatedPage: page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      const title = page.locator('[data-testid="import-hub-title"]')
      await expect(title).toBeVisible()
      await expect(title).toHaveText('Import Hub')
    })
  })

  // ==========================================
  // IMPORT OPTIONS TESTS
  // ==========================================

  test.describe('Import Options Display', () => {
    test('Kasa Raporu import option is visible and clickable', async ({ authenticatedPage: page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Find Kasa Raporu import button
      const kasaRaporuBtn = page.locator('[data-testid="import-hub-kasa-raporu-btn"]')
      await expect(kasaRaporuBtn).toBeVisible()
      await expect(kasaRaporuBtn).toHaveText('Import Et')

      // Click should navigate to sales/verify (import param may or may not be preserved)
      await kasaRaporuBtn.click()
      await expect(page).toHaveURL(/\/sales\/verify/)
    })

    test('Tab switching works between Import and History', async ({ authenticatedPage: page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Default should be Import tab (Yeni Import)
      const importTab = page.locator('button:has-text("Yeni Import")')
      const historyTab = page.locator('button:has-text("Gecmis")')

      await expect(importTab).toBeVisible()
      await expect(historyTab).toBeVisible()

      // Import tab should be active (has bg-blue-600)
      await expect(importTab).toHaveClass(/bg-blue-600/)

      // Click History tab
      await historyTab.click()

      // History tab should now be active
      await expect(historyTab).toHaveClass(/bg-blue-600/)

      // History table should be visible
      const historyTable = page.locator('table')
      await expect(historyTable).toBeVisible()
    })
  })

  // ==========================================
  // STATUS TESTS MOVED TO import-status.spec.ts
  // ==========================================
  // Pending/Completed/Failed status tests are now in import-status.spec.ts
  // using the seeded-import-data fixture for proper data mocking.
  // See: tests/e2e/import/import-status.spec.ts

  // ==========================================
  // HISTORY TABLE TESTS
  // ==========================================

  test.describe('History Table Display', () => {
    test('History table shows correct columns', async ({ authenticatedPage: page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Switch to History tab
      const historyTab = page.locator('button:has-text("Gecmis")')
      await historyTab.click()

      // Check table headers
      const headers = page.locator('thead th')
      await expect(headers.nth(0)).toContainText('Tarih')
      await expect(headers.nth(1)).toContainText('Tur')
      await expect(headers.nth(2)).toContainText('Dosya')
      await expect(headers.nth(3)).toContainText('Durum')
      await expect(headers.nth(4)).toContainText('Islemler')
    })

    // Empty history test moved to import-status.spec.ts (uses seeded-import-data fixture)

    test('History filters are functional', async ({ authenticatedPage: page }) => {
      await page.goto(config.frontendUrl + '/import')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Switch to History tab
      const historyTab = page.locator('button:has-text("Gecmis")')
      await historyTab.click()

      // Check filter controls exist
      const typeFilter = page.locator('select')
      const startDateFilter = page.locator('input[type="date"]').first()
      const filterBtn = page.locator('button:has-text("Filtrele")')

      await expect(typeFilter).toBeVisible()
      await expect(startDateFilter).toBeVisible()
      await expect(filterBtn).toBeVisible()

      // Select a filter option
      await typeFilter.selectOption('kasa_raporu')
      await expect(typeFilter).toHaveValue('kasa_raporu')
    })
  })

  // Failed status test moved to import-status.spec.ts (uses seeded-import-data fixture)
})
