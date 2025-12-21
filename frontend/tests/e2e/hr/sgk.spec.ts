import { test, expect } from '@playwright/test';
import { config } from '../_config/test_config';

test.describe('📋 SGK ve Prim', () => {
    // Login before each test
    test.beforeEach(async ({ page }) => {
        await page.goto('/login');
        await page.fill('input[type="email"]', config.auth.email);
        await page.fill('input[type="password"]', config.auth.password);
        await page.click('button[type="submit"]');
        await expect(page).toHaveURL('/');
    });

    test('SGK Primi Ekleme ve Görüntüleme', async ({ page }) => {
        page.on('console', msg => console.log('Browser log:', msg.text()));
        // 1. Navigate to Personnel/Payment page
        await page.goto('/personnel');
        await page.waitForLoadState('networkidle');

        // 2. Click "Add Payroll"        // Create button usually appears after data load
        // First switch to Payroll tab
        // First switch to Payroll tab
        await page.locator('text=/Personel.*demeleri/i').click();

        const addButton = page.getByRole('button', { name: '+ Odeme Ekle' });
        await addButton.waitFor({ state: 'visible', timeout: 30000 });
        await addButton.click({ force: true });

        // 3. Fill Form - wait for form to appear
        await page.waitForLoadState('networkidle');
        const modal = page.locator('div.fixed.z-50 > div.bg-white').filter({ hasText: /Yeni.*Odeme/i });
        await modal.waitFor({ state: 'visible', timeout: 15000 });

        // Select employee (Scoped to Modal)
        // Use layout-based locator: Find label "Personel *" inside modal, get next select
        // Or simpler: First select in modal
        const personnelSelect = modal.locator('select').first();
        await personnelSelect.waitFor({ state: 'visible', timeout: 5000 });
        await personnelSelect.selectOption({ index: 1 });
        await page.waitForTimeout(500);

        // Ensure correct payment type (Salary includes SGK & Prim)
        await modal.locator('select').filter({ hasText: 'Maas Odemesi' }).selectOption('salary');
        await page.waitForTimeout(500);

        // Fill SGK and Prim amounts (Scoped to Modal Labels)
        await modal.locator('label').filter({ hasText: 'SGK' }).locator('..').locator('input').fill('5500', { force: true });
        await modal.locator('label').filter({ hasText: 'Prim' }).locator('..').locator('input').fill('1000', { force: true });

        // 4. Submit
        const saveButton = modal.getByRole('button', { name: /kaydet|save/i });

        // Wait for response to verify backend success
        const responsePromise = page.waitForResponse(response =>
            response.url().includes('/api/personnel/payroll') && response.request().method() === 'POST'
        );

        await saveButton.click();

        const response = await responsePromise;

        if (response.status() === 400) {
            const body = await response.json();
            if (JSON.stringify(body).includes('zaten kayit var')) {
                console.log('Record already exists (Idempotent), proceeding to verification.');
            } else {
                console.log('Creation Response Body:', body);
                expect(response.status()).toBe(200);
            }
        } else {
            expect(response.status()).toBe(200);
        }

        // Wait for submission to complete
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);

        // Reload to ensure table updates (force sync)
        await page.reload();
        await page.waitForLoadState('networkidle');
        // Switch to tab again after reload
        await page.locator('text=/Personel.*demeleri/i').click();
        await page.waitForTimeout(1000);

        // 5. Verify in Table using Row Scope
        const row = page.locator('tr').filter({ hasText: 'Ahmet Yilmaz' });
        await expect(row).toBeVisible({ timeout: 10000 });

        // Flexible verification for currency formats (₺5.500 or 5.500)
        await expect(row).toContainText(/5[.,]500/);
        await expect(row).toContainText(/1[.,]000/);
    });
});
