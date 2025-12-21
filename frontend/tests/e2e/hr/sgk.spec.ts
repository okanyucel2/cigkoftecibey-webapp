// @smoke
// Pre-flight check: SGK (Social Security) and payroll operations
import { test, expect } from '@playwright/test'

test.describe.configure({ mode: 'serial' })

import { config } from '../_config/test_config'

test.describe('📋 SGK ve Prim', () => {
  // Unique prefix 501x for sgk (500-599 range)
  const uniquePrefix = '501'
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

    // Navigate to personnel page
    await page.goto(config.frontendUrl + '/personnel')
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
  })

  test('Navigate to Personnel page and verify page loads', async ({ page }) => {
    await expect(page).toHaveURL(/personnel/)
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Verify page loaded with retry pattern
    await expect(async () => {
      const pageLoaded = await page.locator('h1, h2, table, [data-testid="heading-personnel"]').first().isVisible()
      expect(pageLoaded).toBe(true)
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })
  })

  test('Switch to Payroll tab and verify', async ({ page }) => {
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Switch to Payroll tab - use flexible text matching
    await expect(async () => {
      const payrollTab = page.locator('text=/Personel.*demeleri|Odeme|Payroll/i')
      await expect(payrollTab.first()).toBeVisible()
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })

    await page.locator('text=/Personel.*demeleri|Odeme|Payroll/i').first().click()
    await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {})

    // Verify tab content loaded
    await expect(async () => {
      const addButton = page.locator('button:has-text("Odeme Ekle"), [data-testid="btn-add-payment"]')
      await expect(addButton.first()).toBeVisible()
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })

    console.log('Payroll tab loaded successfully')
  })

  test('Add SGK payment record', async ({ page }) => {
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Switch to Payroll tab first
    await page.locator('text=/Personel.*demeleri|Odeme|Payroll/i').first().click()
    await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {})

    // Click Add Payment button
    const addButton = page.locator('button:has-text("Odeme Ekle"), [data-testid="btn-add-payment"]')
    await expect(addButton.first()).toBeVisible({ timeout: 10000 })
    await addButton.first().click()

    // Wait for modal to appear
    await expect(async () => {
      const modal = page.locator('div.fixed.z-50, [data-testid="payment-modal"]').filter({ hasText: /Yeni.*Odeme|Payment/i })
      await expect(modal.first()).toBeVisible()
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })

    const modal = page.locator('div.fixed.z-50, [data-testid="payment-modal"]').filter({ hasText: /Yeni.*Odeme|Payment/i }).first()

    // Select employee (first select in modal)
    const personnelSelect = modal.locator('select').first()
    await personnelSelect.waitFor({ state: 'visible', timeout: 5000 })
    await personnelSelect.selectOption({ index: 1 })
    await page.waitForTimeout(300)

    // Fill SGK amount with unique prefix value
    const sgkAmount = '5501'  // Prefix 550 + operation 1
    await modal.locator('label:has-text("SGK")').locator('..').locator('input').fill(sgkAmount)

    // Fill Prim amount
    const primAmount = '1501'  // Prefix 150 + operation 1
    await modal.locator('label:has-text("Prim")').locator('..').locator('input').fill(primAmount)

    // Click save button
    const saveButton = modal.locator('button:has-text("Kaydet"), button:has-text("Save"), [data-testid="btn-save-payment"]')

    // Wait for API response
    const responsePromise = page.waitForResponse(response =>
      response.url().includes('/api/personnel/payroll') && response.request().method() === 'POST'
    , { timeout: 15000 }).catch(() => null)

    await saveButton.first().click()

    const response = await responsePromise
    if (response) {
      const status = response.status()
      if (status === 200 || status === 201) {
        console.log('Payment record created successfully')
      } else if (status === 400) {
        console.log('Record may already exist (idempotent)')
      }
    }

    // Wait for modal to close
    await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {})

    // Reload and verify
    await page.reload()
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Switch to payroll tab again
    await page.locator('text=/Personel.*demeleri|Odeme|Payroll/i').first().click()
    await page.waitForTimeout(1000)

    // Verify record appears (flexible currency format)
    await expect(async () => {
      const table = page.locator('table').first()
      const tableText = await table.textContent()
      expect(tableText).toMatch(/5[.,]?501|5501/)
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

    console.log('SGK payment verified in table')
  })
})
