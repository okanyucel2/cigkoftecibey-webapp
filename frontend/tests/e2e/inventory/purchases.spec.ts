// @smoke
// Pre-flight check: Purchase CRUD operations
import { test, expect } from '@playwright/test'

test.describe.configure({ mode: 'serial' })

import { config } from '../_config/test_config'

test.describe('📦 Mal Alımı', () => {
  // Unique prefix 301x for purchases (300-399 range)
  const uniquePrefix = '301'
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

    // Navigate to purchases page
    await page.goto(config.frontendUrl + '/purchases')
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
  })

  test('Navigate to Purchases page and verify page loads', async ({ page }) => {
    await expect(page).toHaveURL(/purchases/)
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Verify page loaded with retry pattern
    await expect(async () => {
      const pageLoaded = await page.locator('h1, h2, table').first().isVisible()
      expect(pageLoaded).toBe(true)
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })
  })

  test('Create Purchase via API and verify in UI', async ({ page, request }) => {
    // Get token for API calls
    const token = await page.evaluate(() => localStorage.getItem('token'))
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }

    // Create supplier first
    const supplierRes = await request.post(`${config.backendUrl}/api/purchases/suppliers`, {
      headers,
      data: {
        name: `Test Supplier ${uniqueId}`,
        phone: '05551234567'
      }
    })
    const supplier = await supplierRes.json()

    // Create purchase with unique notes
    const uniqueNotes = `Purchase_${uniqueId}`
    const purchaseRes = await request.post(`${config.backendUrl}/api/purchases`, {
      headers,
      data: {
        purchase_date: new Date().toISOString().split('T')[0],
        supplier_id: supplier.id,
        notes: uniqueNotes,
        items: [
          { product_id: 1, description: 'Test Item', quantity: 3011, unit: 'kg', unit_price: 100, vat_rate: 18 }
        ]
      }
    })

    expect(purchaseRes.ok()).toBe(true)
    console.log(`Created purchase with notes: ${uniqueNotes}`)

    // Reload page and verify in UI with retry
    await page.reload()
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Verify record appears with retry pattern
    await expect(async () => {
      const tableContent = await page.locator('table').textContent()
      expect(tableContent).toContain(uniqueNotes)
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

    // Persistence verification - reload again
    await page.reload()
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    await expect(async () => {
      const tableContent = await page.locator('table').textContent()
      expect(tableContent).toContain(uniqueNotes)
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })
  })
})
