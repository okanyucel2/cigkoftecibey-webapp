// @smoke
// Pre-flight check: Business expense CRUD operations
import { test, expect } from '@playwright/test'
import { config } from '../_config/test_config'

test.describe.configure({ mode: 'serial' })

test.describe('💸 İşletme Giderleri', () => {
  // Unique prefix 102x for business-expenses (100-199 range, subset 102)
  const uniquePrefix = '102'
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

    // Navigate to expenses page
    await page.goto(config.frontendUrl + '/expenses')
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
  });

  // TODO: ExpenseForm.vue needs data-testid attributes added for this test to work
  test.skip('should create expense, verify list entry and summary card update', async ({ page }) => {
    // Already navigated to /expenses in beforeEach
    await expect(page).toHaveURL(/\/expenses/)

    // Verify page loads and Total Expenses card is visible
    await expect(page.locator('[data-testid="total-expenses-card"]')).toBeVisible({ timeout: 8000 })

    // Wait for page to fully load
    await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {})

    // Get initial total from summary card
    const initialCardText = await page.locator('[data-testid="total-expenses-card"]').textContent()
    const initialMatches = initialCardText?.match(/[\d.,]+/)
    const initialTotal = initialMatches
      ? parseFloat(initialMatches[0].replace(/\./g, '').replace(',', '.'))
      : 0

    // Generate unique expense data using describe-level uniqueId
    const descriptionText = `E2E Test Gider ${uniqueId}`
    const expenseAmount = 1021  // 102 prefix + operation 1

    // Click '+ Yeni Gider' link to open add expense form (it's a router-link, not button)
    await expect(async () => {
      const addLink = page.locator('a:has-text("Yeni Gider"), [data-testid="btn-add-expense"]').first()
      await expect(addLink).toBeVisible()
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

    const addLink = page.locator('a:has-text("Yeni Gider"), [data-testid="btn-add-expense"]').first()
    await addLink.click()

    // Verify navigation to /expenses/new
    await expect(page).toHaveURL(/\/expenses\/new/)

    // Fill Category field with unique test value
    await page.selectOption('[data-testid="select-expense-category"]', { index: 1 })
    
    // Fill Description field with unique test value
    await page.fill('[data-testid="textarea-expense-description"]', descriptionText)

    // Fill Amount field with test amount (1500)
    await page.fill('[data-testid="input-expense-amount"]', expenseAmount.toString())

    // Fill date field with today's date
    const today = new Date().toISOString().split('T')[0]
    await page.fill('[data-testid="input-expense-date"]', today)

    // Click Save button to submit form
    await page.click('[data-testid="btn-save-expense"]')

    // Verify redirect to /expenses list
    await expect(page).toHaveURL(/\/expenses$/)

    // Reload page to ensure list is fresh
    await page.reload()

    // Wait for newly created expense to appear in list with retry logic
    await expect(async () => {
      const row = page.locator(`[data-testid="expense-row"]`).filter({ hasText: descriptionText })
      await expect(row).toBeVisible()
    }).toPass({ timeout: 10000 })

    // Verify expense row contains correct description text
    const expenseRow = page.locator(`[data-testid="expense-row"]`).filter({ hasText: descriptionText })
    await expect(expenseRow).toContainText(descriptionText)

    // Verify Total Expenses summary card updates and contains currency symbol
    await expect(async () => {
      const summaryCard = page.locator('[data-testid="total-expenses-card"]')
      const cardText = await summaryCard.textContent()
      expect(cardText).toContain('₺')
    }).toPass({ timeout: 8000 })

    // Extract and validate total expenses value is >= added amount
    const updatedCardText = await page.locator('[data-testid="total-expenses-card"]').textContent()
    const updatedMatches = updatedCardText?.match(/[\d.,]+/)
    const updatedTotal = updatedMatches 
      ? parseFloat(updatedMatches[0].replace(/\./g, '').replace(',', '.'))
      : 0

    // Verify total has increased
    expect(updatedTotal).toBeGreaterThanOrEqual(initialTotal + expenseAmount)
  })
})