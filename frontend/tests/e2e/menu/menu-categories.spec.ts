// @smoke @menu
// Menu Categories CRUD E2E Tests (Genesis Gold Standard)
import { test, expect } from '@playwright/test'

test.describe.configure({ mode: 'serial' })

import { config } from '../_config/test_config'

test.describe('Menu Kategorileri', () => {
  const uniquePrefix = '201'
  const uniqueSuffix = Date.now().toString().slice(-4)
  const uniqueId = `${uniquePrefix}_${uniqueSuffix}`

  const testCategories = [
    { name: `Cigkofte Cesitleri ${uniqueId}`, description: 'Tum cigkofte urunleri', order: 1 },
    { name: `Icecekler ${uniqueId}`, description: 'Soguk ve sicak icecekler', order: 2 },
    { name: `Tatlilar ${uniqueId}`, description: 'Tatli cesitleri', order: 3 },
    { name: `Yan Urunler ${uniqueId}`, description: 'Ek urunler ve soslar', order: 4 },
  ]

  test.beforeEach(async ({ page, request }) => {
    test.setTimeout(30000)  // 30s max per test
    
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

  test('Navigate to Menu page and verify Categories tab', async ({ page }) => {
    await expect(page).toHaveURL(/menu/)
    await expect(page.locator('main h1')).toContainText('Menu', { timeout: 3000 })
    await expect(page.locator('button:has-text("Kategoriler")')).toBeVisible({ timeout: 3000 })
    await expect(page.locator('button:has-text("+ Yeni Kategori")')).toBeVisible({ timeout: 3000 })
  })

  test('Create Menu Category (Happy Path)', async ({ page }) => {
    const category = testCategories[0]
    
    await page.click('button:has-text("+ Yeni Kategori")')
    await expect(page.locator('h2:has-text("Yeni Kategori")')).toBeVisible({ timeout: 3000 })
    
    // Fill form - first text input is category name
    const modal = page.locator('.fixed.inset-0 .bg-white')
    await modal.locator('input[type="text"]').first().fill(category.name)
    await modal.locator('textarea').first().fill(category.description)
    
    await page.screenshot({ path: `/tmp/menu-category-create-${uniqueId}.png`, fullPage: true })
    await modal.locator('button:has-text("Kaydet")').click()
    
    await expect(page.locator('h2:has-text("Yeni Kategori")')).not.toBeVisible({ timeout: 5000 })
    await expect(page.locator(`text=${category.name}`)).toBeVisible({ timeout: 5000 })
    
    console.log('Created category:', category.name)
  })

  test('Create Bulk Bogus Categories via API', async ({ page, request }) => {
    const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', {
      data: { email: config.auth.email, password: config.auth.password }
    })
    const { access_token: token } = await loginRes.json()

    for (const category of testCategories) {
      const res = await request.post(config.backendUrl + '/api/v1/menu-categories', {
        headers: { Authorization: `Bearer ${token}` },
        data: { name: category.name, description: category.description, display_order: category.order }
      })
      if (res.ok()) {
        const data = await res.json()
        console.log('Created:', category.name, '(ID:', data.id, ')')
      }
    }
    
    await page.reload()
    await page.waitForLoadState('networkidle', { timeout: 3000 }).catch(() => {})
    await page.screenshot({ path: `/tmp/menu-categories-all-${uniqueId}.png`, fullPage: true })
  })
})
