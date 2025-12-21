// @smoke
// Pre-flight check: System settings and user management
import { test, expect } from '@playwright/test'

test.describe.configure({ mode: 'serial' })

import { config } from '../_config/test_config'

test.describe('⚙️ Sistem Ayarları', () => {
  // Unique prefix 401x for settings (400-499 range)
  const uniquePrefix = '401'
  const uniqueSuffix = Date.now().toString().slice(-4)
  const uniqueId = `${uniquePrefix}_${uniqueSuffix}`

  test.beforeEach(async ({ page, request }) => {
    test.setTimeout(60000)

    // DEBUG LISTENERS
    page.on('console', msg => console.log(`BROWSER [${msg.type()}]: ${msg.text()}`))
    page.on('requestfailed', request => console.log(`NETWORK FAIL: ${request.url()} - ${request.failure()?.errorText}`))

    // API LOGIN BYPASS
    console.log('Attempting API Login...')
    const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', {
      data: {
        email: config.auth.email,
        password: config.auth.password
      }
    })

    if (!loginRes.ok()) {
      console.error('API Login Failed:', loginRes.status(), await loginRes.text())
      throw new Error('API Login Failed')
    }

    const loginData = await loginRes.json()
    const token = loginData.access_token
    console.log('API Login Success. Token obtained.')

    // Inject Token into LocalStorage
    await page.goto(config.frontendUrl + '/login')
    await page.evaluate((t) => {
      localStorage.setItem('token', t)
    }, token)

    // Navigate to settings page
    await page.goto(config.frontendUrl + '/settings')
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
  })

  test('Navigate to Settings page and verify page loads', async ({ page }) => {
    await expect(page).toHaveURL(/settings/)
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Verify page heading with retry pattern
    await expect(async () => {
      const heading = page.locator('h1, h2, [data-testid="heading-settings"]').filter({ hasText: /Sistem|Ayarlar|Settings/i })
      await expect(heading.first()).toBeVisible()
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })

    console.log('Settings page loaded successfully')
  })

  test('Switch to Users tab and verify content', async ({ page }) => {
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Wait for settings page to fully load
    await expect(async () => {
      const heading = page.locator('h1, h2').filter({ hasText: /Sistem|Ayarlar|Settings/i })
      await expect(heading.first()).toBeVisible()
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })

    // Click Users tab
    await page.click('button:has-text("Kullanicilar"), [data-testid="tab-users"]')
    await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {})

    // Verify users table is visible
    await expect(async () => {
      const table = page.locator('table')
      await expect(table.first()).toBeVisible()
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })

    console.log('Users tab loaded with table')
  })

  test('Branch removal modal flow', async ({ page }) => {
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Wait for settings page to load
    await expect(async () => {
      const heading = page.locator('h1, h2').filter({ hasText: /Sistem|Ayarlar|Settings/i })
      await expect(heading.first()).toBeVisible()
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })

    // Switch to Users Tab
    await page.click('button:has-text("Kullanicilar"), [data-testid="tab-users"]')
    await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {})

    // Wait for users table
    await expect(page.locator('table').first()).toBeVisible({ timeout: 10000 })

    // Look for branch removal button
    const removeBtn = page.locator('button[title="Subeden Cikar"], [data-testid="btn-remove-branch"]').first()

    // Check if any exists
    const count = await removeBtn.count()
    if (count === 0) {
      console.log('Skipping test: No users with branches found to remove.')
      test.skip(true, 'No users with branches found')
      return
    }

    // Click Remove
    await removeBtn.click()

    // Verify confirmation modal appears
    await expect(async () => {
      const modal = page.locator('div.fixed h3:has-text("Onay"), [data-testid="confirm-modal"]')
      await expect(modal.first()).toBeVisible()
    }).toPass({ timeout: 5000, intervals: [500, 1000] })

    // Click confirm button
    await page.click('button:has-text("Evet"), button:has-text("Sil"), [data-testid="btn-confirm"]')

    // Verify modal closed
    await expect(async () => {
      const modal = page.locator('div.fixed h3:has-text("Onay")')
      const isVisible = await modal.isVisible().catch(() => false)
      expect(isVisible).toBe(false)
    }).toPass({ timeout: 5000, intervals: [500, 1000] })

    console.log('Branch removal modal flow completed')
  })
})
