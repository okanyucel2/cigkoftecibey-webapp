import { test, expect } from '@playwright/test'

test.describe('Import Hub Modal Auto-Open', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('http://localhost:19049/login')
    await page.fill('input[type="email"]', 'admin@cigkofte.com')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    // App redirects to "/" after login, not "/dashboard"
    await page.waitForURL('http://localhost:19049/', { timeout: 10000 })
  })

  test('Import Et button opens Kasa Farki modal', async ({ page }) => {
    // Go to Import Hub
    await page.goto('http://localhost:19049/import')
    await page.waitForLoadState('networkidle')

    // Take screenshot before click
    await page.screenshot({ path: 'test-results/01-import-hub.png' })

    // Click Import Et button
    await page.click('[data-testid="import-hub-kasa-raporu-btn"]')

    // Wait for navigation
    await page.waitForURL('**/sales/verify**', { timeout: 5000 })

    // Wait a moment for modal to open
    await page.waitForTimeout(1000)

    // Take screenshot after click
    await page.screenshot({ path: 'test-results/02-after-import-click.png' })

    // Verify modal is visible - look for the modal or import component
    const modal = page.locator('text=Kasa Farki').or(page.locator('text=Veri Yukleme')).or(page.locator('[data-testid="import-modal"]'))
    await expect(modal).toBeVisible({ timeout: 5000 })

    // Take screenshot with modal
    await page.screenshot({ path: 'test-results/03-modal-open.png' })

    console.log('Modal opened successfully!')
  })
})
