
import { test, expect } from '@playwright/test';

test.describe('SGK ve Prim Yönetimi', () => {
    // Login before each test
    test.beforeEach(async ({ page }) => {
        await page.goto('/login');
        // Using default test credentials or mocked auth if possible
        // For E2E against real dev server, we need valid creds.
        // Assuming 'admin@cigkoftecibey.com' / '123123' or similiar from seed
        await page.fill('input[type="email"]', 'admin@cigkoftecibey.com');
        await page.fill('input[type="password"]', '123123'); // Adjust if needed
        await page.click('button[type="submit"]');
        await expect(page).toHaveURL('/dashboard');
    });

    test('SGK Primi Ekleme ve Görüntüleme', async ({ page }) => {
        // 1. Navigate to Personnel/Payment page
        // Assuming sidebar link exists or direct URL
        await page.goto('/personnel/payroll');

        // 2. Click "Add Payroll"
        await page.getByRole('button', { name: 'Yeni Ödeme/Bordro' }).click();

        // 3. Fill Form
        // Needs selectors based on the actual Vue component
        // Assuming standard inputs
        await page.getByLabel('Personel').click();
        await page.getByRole('option').first().click(); // Select first employee

        await page.getByLabel('SGK Tutarı').fill('5500');
        await page.getByLabel('Prim').fill('1000');

        // 4. Submit
        await page.getByRole('button', { name: 'Kaydet' }).click();

        // 5. Verify in Table
        await expect(page.getByText('5.500,00 ₺')).toBeVisible();
        await expect(page.getByText('1.000,00 ₺')).toBeVisible();
    });
});
