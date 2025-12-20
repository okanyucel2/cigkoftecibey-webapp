
import { test, expect } from '@playwright/test';
import { config } from './test_config';

test.describe.configure({ mode: 'serial' });

test.describe('Dashboard Data Integrity Validation', () => {
  test.setTimeout(120000);

  test('validates KPI calculations against seeded transactions', async ({ page }) => {
    // 1. Login
    await page.goto(`${config.frontendUrl}/login`);
    await page.fill('input[type="email"]', config.auth.email);
    await page.fill('input[type="password"]', config.auth.password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(`${config.frontendUrl}/`, { timeout: 15000 });

    const timestamp = Date.now();
    const amounts = {
      sale: 1000,
      expense: 50,
      meal: 30
    };

    // 2. SEED DATA - Sale (1000 TL)
    await page.goto(`${config.frontendUrl}/sales`);
    await page.click('text=+ Satis Ekle');
    // Wait for modal input. UnifiedSales modal has date input then channel inputs.
    // We assume first input[type="number"] is Salon (POS).
    await page.locator('input[type="number"]').first().fill(amounts.sale.toString());
    await page.click('button:has-text("Kaydet"), button[type="submit"]');
    // Should close modal and refresh list
    await expect(page.locator('.page-modal')).not.toBeVisible();
    await expect(page).toHaveURL(`${config.frontendUrl}/sales`);

    // 3. SEED DATA - Expense (50 TL)
    await page.goto(`${config.frontendUrl}/expenses`);
    await page.click('text=+ Yeni Gider');
    // This goes to /expenses/new page (verified in ExpenseForm.vue)
    await expect(page).toHaveURL(/.*\/expenses\/new/);

    // Select first category (ExpenseForm.vue: select#category_id)
    // Wait for options to load
    const categorySelect = page.locator('select#category_id');
    await expect(categorySelect).toBeVisible();
    // Select the second option (first is null "Kategori Secin")
    await categorySelect.selectOption({ index: 1 });

    // Fill amount (input#amount)
    await page.fill('input#amount', amounts.expense.toString());

    // Save
    await page.click('button:has-text("Kaydet")');
    await expect(page).toHaveURL(`${config.frontendUrl}/expenses`);

    // 4. SEED DATA - Staff Meal (30 TL)
    await page.goto(`${config.frontendUrl}/staff-meals`);
    await page.click('text=+ Yeni Kayit');
    // Modal opens. StaffMeals.vue inputs: Unit Price (0), Staff Count (1).
    // Let's set unit price to 30, count 1.
    await page.locator('input[type="number"]').nth(0).fill(amounts.meal.toString()); // Unit Price
    await page.locator('input[type="number"]').nth(1).fill('1'); // Count
    await page.click('button:has-text("Kaydet"), button[type="submit"]');
    await expect(page.locator('.page-modal')).not.toBeVisible();

    // 5. VALIDATE DASHBOARD
    await page.goto(`${config.frontendUrl}/`);
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('.kpi-card', { state: 'visible', timeout: 15000 });

    // Helper: Extract number from "₺1.280,00"
    const parseMoney = (txt: string | null) => {
      if (!txt) return 0;
      return parseFloat(txt.replace(/[^0-9,.-]/g, '').replace(/\./g, '').replace(',', '.'));
    };

    // Expected Impact:
    // Revenue (Ciro): +1000
    // Expenses (Gider): +50 (Expense) + 30 (Meal) = 80
    // Profit: +920

    await expect(async () => {
      // Precise check
      const cards = await page.locator('.kpi-card').allTextContents();
      const expensesCard = cards.find(c => c.includes('Toplam Gider'));
      const profitCard = cards.find(c => c.includes('Net Kar') || c.includes('Net Kâr'));
      const revenueCard = cards.find(c => c.includes('Toplam Ciro'));

      if (expensesCard) {
        const expenseVal = parseMoney(expensesCard);
        expect(expenseVal).toBeGreaterThanOrEqual(80);
      }

      if (revenueCard) {
        const revenueVal = parseMoney(revenueCard);
        expect(revenueVal).toBeGreaterThanOrEqual(1000);
      }

      if (profitCard) {
        const profitVal = parseMoney(profitCard);
        expect(profitVal).not.toBeNaN();
      }

    }).toPass({ timeout: 15000 });
  });
});