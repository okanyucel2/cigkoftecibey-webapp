// @smoke
// Pre-flight check: Invitation code management
import { test, expect } from '@playwright/test'

test.describe.configure({ mode: 'serial' })

import { config } from '../_config/test_config'

test.describe('🔑 Davet Kodları', () => {
  // Unique prefix 601x for invitation-codes (600-699 range)
  const uniquePrefix = '601'
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

    // Navigate to invitation codes page
    await page.goto(config.frontendUrl + '/invitation-codes')
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
  })

  test('Navigate to Invitation Codes page and verify page loads', async ({ page }) => {
    await expect(page).toHaveURL(/invitation-codes/)
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Verify page loaded with retry pattern
    await expect(async () => {
      const pageLoaded = await page.locator('h1, h2, table, [data-testid="heading-invitation-codes"]').first().isVisible()
      expect(pageLoaded).toBe(true)
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })
  })

  test('Create new invitation code', async ({ page }) => {
    // Wait for page to fully load
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Click create button
    await expect(async () => {
      const createBtn = page.locator('button:has-text("Yeni Kod"), [data-testid="btn-create-code"]')
      await expect(createBtn.first()).toBeVisible()
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })

    await page.click('button:has-text("Yeni Kod"), [data-testid="btn-create-code"]')

    // Wait for modal/form
    await page.waitForTimeout(500)

    // Click create/generate button
    await page.click('button:has-text("Olustur"), button:has-text("Kaydet"), [data-testid="btn-generate-code"]')

    // Wait for response
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Verify code appears in table
    await expect(async () => {
      const table = page.locator('table').first()
      const rowCount = await table.locator('tbody tr').count()
      expect(rowCount).toBeGreaterThan(0)
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

    console.log('Invitation code created successfully')
  })

  test('Deactivate invitation code', async ({ page }) => {
    // Wait for page to load with codes
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Ensure at least one code exists
    const activeRows = page.locator('table').first().locator('tbody tr')

    await expect(async () => {
      const count = await activeRows.count()
      expect(count).toBeGreaterThan(0)
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

    // Get first code text for verification
    const firstRow = activeRows.first()
    const codeText = await firstRow.locator('code, td:first-child').first().innerText()
    console.log('Testing deactivation for code:', codeText)

    // Click Deactivate button
    await firstRow.locator('button:has-text("Devre Disi"), [data-testid^="btn-deactivate"]').first().click()

    // Wait for confirmation modal
    await expect(async () => {
      const modal = page.locator('div.fixed h3:has-text("Onay"), [data-testid="confirm-modal"]')
      await expect(modal.first()).toBeVisible()
    }).toPass({ timeout: 5000, intervals: [500, 1000] })

    // Confirm deactivation
    await page.click('button:has-text("Evet"), button:has-text("Onayla"), [data-testid="btn-confirm"]')

    // Wait for update
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Verify code removed from active table
    await expect(async () => {
      const table = page.locator('table').first()
      if (await table.isVisible()) {
        const tableText = await table.textContent()
        expect(tableText).not.toContain(codeText)
      }
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })

    console.log('Code deactivated successfully')
  })
})
