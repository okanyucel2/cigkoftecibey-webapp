import { test, expect } from '@playwright/test';
import { config } from './test_config';

test.describe('Invitation Codes UI @smoke', () => {

    test.beforeEach(async ({ page }) => {
        page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
        await page.goto('/login');
        await page.fill('input[type="email"]', config.auth.email);
        await page.fill('input[type="password"]', config.auth.password);
        await page.click('button[type="submit"]');
        await expect(page).toHaveURL('/');
    });

    test('Robust Deactivation Test', async ({ page }) => {
        await page.goto('/invitation-codes');
        await page.waitForTimeout(3000); // Wait for load (Backend slow)

        // Ensure at least one code exists
        const activeRows = page.locator('table').first().locator('tbody tr');
        const count = await activeRows.count();

        if (count === 0) {
            await page.click('button:has-text("Yeni Kod")');
            await page.click('button:has-text("Olustur")');
            await page.waitForTimeout(1000);
        }

        // Get first code
        const firstRow = activeRows.first();
        const codeText = await firstRow.locator('code').innerText();
        console.log('Testing deactivation for code:', codeText);

        // Click Deactivate
        await firstRow.getByRole('button', { name: 'Devre Disi Birak' }).click();

        // Modal Check
        await expect(page.locator('div.fixed h3:has-text("Onay")')).toBeVisible();
        await page.click('button:has-text("Evet, Sil")'); // Or "Evet" if text is generic? Usually "Evet, Sil" or "Onayla"

        // Wait for update
        await page.waitForTimeout(1000);

        // Verify gone from first table (Optimistic check)
        // Verify gone from first table
        // If table is gone (empty list), that's also a pass for "not containing text"
        const table1 = page.locator('table').first();
        if (await table1.isVisible()) {
            await expect(table1).not.toContainText(codeText);
        } else {
            // Table gone implies empty list
            await expect(page.locator('text=Henuz aktif davet kodu yok')).toBeVisible();
        }
        console.log('Code removed from Active list');
    });
});
