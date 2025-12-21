// Genesis Auto-Fix Version: 5 (Last: 2025-12-21 00:40:43)
import { test, expect } from '@playwright/test'
import { config } from '../_config/test_config'

test.describe.configure({ mode: 'serial' })

test.describe('💸 İşletme Giderleri', () => {
  const baseURL = config.frontendUrl

  test.beforeEach(async ({ page }) => {
    page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
    
    // Skip login if backend API is not available
    try {
      await page.goto('/login');
      await page.fill('input[type="email"]', config.auth.email);
      await page.fill('input[type="password"]', config.auth.password);
      await page.click('button[type="submit"]');
      await page.waitForURL('/', { timeout: 10000 });
    } catch (error) {
      console.error('Login failed - backend API may not be running:', error.message);
      throw new Error('Test setup failed: Backend API connection refused (ECONNREFUSED). Ensure backend server is running before executing E2E tests.');
    }
  });

  test('should create expense, verify list entry and summary card update', async ({ page }) => {
    // Navigate to /expenses (authentication already done in beforeEach)
    await page.goto(`${baseURL}/expenses`)
    await expect(page).toHaveURL(/\/expenses/)

    // Verify page loads and Total Expenses card is visible
    await expect(page.locator('[data-testid="total-expenses-card"]')).toBeVisible({ timeout: 8000 })

    // Wait for page to fully load
    await page.waitForTimeout(3000);

    // Get initial total from summary card
    const initialCardText = await page.locator('[data-testid="total-expenses-card"]').textContent()
    const initialMatches = initialCardText?.match(/[\d.,]+/)
    const initialTotal = initialMatches 
      ? parseFloat(initialMatches[0].replace(/\./g, '').replace(',', '.'))
      : 0

    // Generate unique expense data
    const uniqueId = Date.now().toString()
    const categoryName = `Test Kategori ${uniqueId}`
    const descriptionText = `E2E Test Gider ${uniqueId}`
    const expenseAmount = 1500

    // Click '+ Yeni Gider' button to open add expense form
    // Use multiple selectors as fallback (button might have text, icon, or data-testid)
    const addButton = page.locator('[data-testid="btn-add-expense"]').or(page.locator('button:has-text("Yeni Gider")')).or(page.locator('button:has-text("+ Yeni")')).first()
    await addButton.waitFor({ timeout: 10000, state: 'visible' })
    await addButton.click()

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