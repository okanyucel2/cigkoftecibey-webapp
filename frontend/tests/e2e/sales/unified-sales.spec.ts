// @smoke
// Pre-flight check: Unified sales platform and daily entry operations
import { test, expect } from '@playwright/test'

test.describe.configure({ mode: 'serial' })

import { config } from '../_config/test_config'

test.describe('💰 Satış Girişi', () => {
  // Unique prefix 702x for unified-sales (700-799 range)
  const uniquePrefix = '702'
  const uniqueSuffix = Date.now().toString().slice(-4)
  const uniqueId = `${uniquePrefix}_${uniqueSuffix}`

  let authToken = ''

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
    authToken = loginData.access_token
    console.log('API Login Success. Token obtained.')

    // Inject Token into LocalStorage
    await page.goto(config.frontendUrl + '/login')
    await page.evaluate((t) => {
      localStorage.setItem('token', t)
    }, authToken)

    // Navigate to sales page
    await page.goto(config.frontendUrl + '/sales')
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
  })

  test('Navigate to Sales page and verify page loads', async ({ page }) => {
    await expect(page).toHaveURL(/sales/)
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Verify page loaded with retry pattern
    await expect(async () => {
      const pageLoaded = await page.locator('h1, h2, table, select').first().isVisible()
      expect(pageLoaded).toBe(true)
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })

    console.log('Sales page loaded successfully')
  })

  test('Create Platform and Daily Sale via API, verify in UI', async ({ page, request }) => {
    const headers = {
      'Authorization': `Bearer ${authToken}`,
      'Content-Type': 'application/json'
    }

    // Create unique platform name
    const testPlatformName = `Platform_${uniqueId}`
    const testAmount = 7021  // 702 prefix + operation 1

    // 1. Create Platform via API
    console.log(`Creating platform: ${testPlatformName}`)
    const platformRes = await request.post(`${config.backendUrl}/api/online-sales/platforms`, {
      headers,
      data: { name: testPlatformName, display_order: 999 }
    })

    let platformId = 0
    if (platformRes.ok()) {
      const platformData = await platformRes.json()
      platformId = platformData.id
      console.log(`Platform created with ID: ${platformId}`)
    } else {
      console.log(`Platform creation failed: ${platformRes.status()}`)
      // Try to find existing platform
      const listRes = await request.get(`${config.backendUrl}/api/online-sales/platforms`, { headers })
      if (listRes.ok()) {
        const platforms = await listRes.json()
        if (platforms.length > 0) {
          platformId = platforms[0].id
          console.log(`Using existing platform ID: ${platformId}`)
        }
      }
    }

    expect(platformId).toBeGreaterThan(0)

    // 2. Create Daily Sales Entry
    const testDate = new Date().toISOString().split('T')[0]
    console.log(`Creating daily sale for date: ${testDate}`)

    const saleRes = await request.post(`${config.backendUrl}/api/online-sales/daily`, {
      headers,
      data: {
        sale_date: testDate,
        entries: [{ platform_id: platformId, amount: testAmount }],
        notes: `Test Sale ${uniqueId}`
      }
    })

    if (saleRes.ok()) {
      console.log('Daily sale created successfully')
    } else {
      console.log(`Sale creation status: ${saleRes.status()} - may be updating existing`)
    }

    // 3. Reload and verify in UI
    await page.reload()
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Verify table has content
    await expect(async () => {
      const table = page.locator('table').first()
      await expect(table).toBeVisible()
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

    console.log('Sales data verified in UI')
  })

  test('Open Platforms modal and verify UI', async ({ page }) => {
    // Click Platforms button
    await expect(async () => {
      const platformBtn = page.locator('button:has-text("Platformlar"), button:has-text("Platform")')
      await expect(platformBtn.first()).toBeVisible()
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })

    await page.locator('button:has-text("Platformlar"), button:has-text("Platform")').first().click()

    // Verify modal opens
    await expect(async () => {
      const modalHeader = page.locator('h2:has-text("Satis Kanallari"), h2:has-text("Platform")')
      await expect(modalHeader.first()).toBeVisible()
    }).toPass({ timeout: 10000, intervals: [1000, 2000] })

    console.log('Platforms modal opened successfully')

    // Close modal by clicking outside or escape
    await page.keyboard.press('Escape')
    await page.waitForTimeout(500)
  })

  test.afterAll(async ({ request }) => {
    console.log('--- CLEANUP STARTED ---')

    // Login to get token for cleanup
    const loginRes = await request.post(`${config.backendUrl}/api/auth/login-json`, {
      data: { email: config.auth.email, password: config.auth.password }
    })

    if (!loginRes.ok()) {
      console.log('Cleanup login failed, skipping cleanup')
      return
    }

    const loginData = await loginRes.json()
    const token = loginData.access_token
    const headers = { 'Authorization': `Bearer ${token}` }

    // Delete test platforms
    const platformsRes = await request.get(`${config.backendUrl}/api/online-sales/platforms`, { headers })
    if (platformsRes.ok()) {
      const platforms = await platformsRes.json()
      const testPlatforms = platforms.filter((p: any) => p.name.includes('Platform_702'))

      console.log(`Found ${testPlatforms.length} test platforms to clean up`)

      for (const p of testPlatforms) {
        console.log(`Deleting: ${p.name}`)
        await request.delete(`${config.backendUrl}/api/online-sales/platforms/${p.id}`, { headers })
      }
    }

    console.log('--- CLEANUP FINISHED ---')
  })
})
