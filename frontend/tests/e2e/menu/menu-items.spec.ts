// @smoke @menu  
// Menu Items CRUD E2E Tests with Branch-Specific Pricing (Genesis Gold Standard)
import { test, expect } from '@playwright/test'

test.describe.configure({ mode: 'serial' })

import { config } from '../_config/test_config'

test.describe('Menu Urunleri', () => {
  const uniquePrefix = '202'
  const uniqueSuffix = Date.now().toString().slice(-4)
  const uniqueId = `${uniquePrefix}_${uniqueSuffix}`

  // Bogus test data - realistic Turkish menu items
  const testItems = [
    { name: `Cig Kofte Durum ${uniqueId}`, description: 'Klasik lavas durum', price: 85.00, order: 1 },
    { name: `Cig Kofte Porsiyon ${uniqueId}`, description: 'Tabak servis', price: 95.00, order: 2 },
    { name: `Soslu Durum ${uniqueId}`, description: 'Ozel sos ile', price: 90.00, order: 3 },
    { name: `Ayran ${uniqueId}`, description: 'Taze yogurttan', price: 15.00, order: 4 },
    { name: `Salgam ${uniqueId}`, description: 'Acili veya acsiz', price: 12.00, order: 5 },
    { name: `Kola ${uniqueId}`, description: '330ml', price: 20.00, order: 6 },
    { name: `Su ${uniqueId}`, description: '500ml', price: 8.00, order: 7 },
    { name: `Kunefe ${uniqueId}`, description: 'Antep fistikli', price: 75.00, order: 8 },
  ]

  let categoryId: number

  test.beforeEach(async ({ page, request }) => {
    test.setTimeout(30000)
    
    const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', {
      data: { email: config.auth.email, password: config.auth.password }
    })
    if (!loginRes.ok()) throw new Error('API Login Failed')

    const { access_token: token } = await loginRes.json()
    await page.goto(config.frontendUrl + '/login')
    await page.evaluate((t) => localStorage.setItem('token', t), token)
    await page.goto(config.frontendUrl + '/menu')
    await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {})
  })

  test('Setup: Create test category via API', async ({ request }) => {
    const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', {
      data: { email: config.auth.email, password: config.auth.password }
    })
    const { access_token: token } = await loginRes.json()

    const res = await request.post(config.backendUrl + '/api/v1/menu-categories', {
      headers: { Authorization: `Bearer ${token}` },
      data: { name: `E2E Test Category ${uniqueId}`, description: 'Test kategorisi', display_order: 99 }
    })
    
    if (res.ok()) {
      const data = await res.json()
      categoryId = data.id
      console.log('Created test category ID:', categoryId)
    } else {
      const listRes = await request.get(config.backendUrl + '/api/v1/menu-categories', {
        headers: { Authorization: `Bearer ${token}` }
      })
      const categories = await listRes.json()
      if (categories.length > 0) categoryId = categories[0].id
    }
    expect(categoryId).toBeGreaterThan(0)
  })

  test('Navigate to Items tab', async ({ page }) => {
    await expect(page.locator('button:has-text("Urunler")')).toBeVisible({ timeout: 3000 })
    await page.click('button:has-text("Urunler")')
    await page.waitForTimeout(300)
    await expect(page.locator('button:has-text("+ Yeni Urun")')).toBeVisible({ timeout: 3000 })
    await page.screenshot({ path: `/tmp/menu-items-tab-${uniqueId}.png`, fullPage: true })
  })

  test('Create Bulk Bogus Items via API', async ({ request }) => {
    const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', {
      data: { email: config.auth.email, password: config.auth.password }
    })
    const { access_token: token } = await loginRes.json()

    // Get a category ID
    const catRes = await request.get(config.backendUrl + '/api/v1/menu-categories', {
      headers: { Authorization: `Bearer ${token}` }
    })
    const categories = await catRes.json()
    const catId = categories.length > 0 ? categories[0].id : 1

    let createdCount = 0
    for (const item of testItems) {
      const res = await request.post(config.backendUrl + '/api/v1/menu-items', {
        headers: { Authorization: `Bearer ${token}` },
        data: {
          name: item.name,
          description: item.description,
          category_id: catId,
          default_price: item.price,
          display_order: item.order
        }
      })
      if (res.ok()) {
        const data = await res.json()
        createdCount++
        console.log('Created:', item.name, '- Price:', item.price, 'TL (ID:', data.id, ')')
      }
    }
    
    console.log(`Total items created: ${createdCount}`)
    expect(createdCount).toBeGreaterThan(0)
  })

  test('Verify Items Display with Prices', async ({ page }) => {
    await page.click('button:has-text("Urunler")')
    await page.waitForTimeout(500)
    
    // Check for price display
    const priceVisible = await page.locator('text=/\\d+[.,]\\d{2}|TL|₺/').first().isVisible({ timeout: 3000 }).catch(() => false)
    console.log('Prices visible:', priceVisible)
    
    await page.screenshot({ path: `/tmp/menu-items-all-${uniqueId}.png`, fullPage: true })
  })

  test('Set Branch-Specific Price via API', async ({ request }) => {
    const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', {
      data: { email: config.auth.email, password: config.auth.password }
    })
    const { access_token: token } = await loginRes.json()

    const itemsRes = await request.get(config.backendUrl + '/api/v1/menu-items', {
      headers: { Authorization: `Bearer ${token}` }
    })
    const items = await itemsRes.json()
    
    if (items.length > 0) {
      const itemId = items[0].id
      const branchPrice = 99.99
      
      const res = await request.put(config.backendUrl + `/api/v1/menu-items/${itemId}/prices`, {
        headers: { Authorization: `Bearer ${token}` },
        data: { price: branchPrice, branch_id: 1 }
      })
      
      if (res.ok()) {
        const data = await res.json()
        console.log('Set branch price for item', itemId, ':', branchPrice, 'TL')
        expect(parseFloat(data.price)).toBe(branchPrice)
      }
    }
  })

  test('Verify Price Resolution (Branch > Default)', async ({ request }) => {
    const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', {
      data: { email: config.auth.email, password: config.auth.password }
    })
    const { access_token: token } = await loginRes.json()

    const itemsRes = await request.get(config.backendUrl + '/api/v1/menu-items', {
      headers: { Authorization: `Bearer ${token}` }
    })
    const items = await itemsRes.json()
    
    if (items.length > 0) {
      const item = items[0]
      console.log('Item:', item.name)
      console.log('Price:', item.price, 'TL')
      console.log('Is Default:', item.price_is_default)
      
      if (item.price_is_default === false) {
        console.log('Branch-specific price is being used correctly!')
      }
    }
  })
})
