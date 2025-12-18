
import { test, expect } from '@playwright/test';

test.describe('Kurye Giderleri UI', () => {

    test.beforeEach(async ({ page }) => {
        // Console logs
        page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));

        // Log Network
        page.on('request', request => {
            if (request.url().includes('/api/courier-expenses')) {
                console.log(`>> ${request.method()} ${request.url()}`);
            }
        });
        page.on('response', response => {
            if (response.url().includes('/api/courier-expenses')) {
                console.log(`<< ${response.status()} ${response.url()}`);
            }
        });

        // 1. Login
        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@cigkofte.com');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await expect(page).toHaveURL('/');
    });

    test('Kurye Gideri Ekleme ve Silme', async ({ page, request }) => {
        // 2. Auth for Cleanup
        const token = await page.evaluate(() => {
            const auth = localStorage.getItem('auth');
            return auth ? JSON.parse(auth).token : localStorage.getItem('token');
        });

        // 3. Cleanup Existing Data
        if (token) {
            console.log("Cleaning up Courier Expenses...");
            // List endpoint used: /api/courier-expenses?year=2025&month=12
            try {
                const headers = { 'Authorization': `Bearer ${token}` };
                const listUrl = 'http://localhost:8001/api/courier-expenses?year=2025&month=12';
                const res = await request.get(listUrl, { headers });
                if (res.ok()) {
                    const data = await res.json();
                    console.log(`Cleanup: Found ${data.length} records to delete.`);
                    for (const item of data) {
                        await request.delete(`http://localhost:8001/api/courier-expenses/${item.id}`, { headers });
                    }
                }
            } catch (e) { console.log('Cleanup error', e); }
        }

        // 4. Navigate
        console.log("Navigating to Courier Expenses...");
        await page.goto('/courier-expenses');

        // 5. Create New Record
        await page.click('button:has-text("+ Kayit Ekle")');
        await expect(page.locator('h2:has-text("Yeni Kurye Gideri")')).toBeVisible();

        const uniquePkg = 100 + Math.floor(Math.random() * 50);
        const uniqueAmt = 1250;

        console.log(`Creating record with Package Count: ${uniquePkg}`);
        await page.locator('input[type="date"]').fill('2025-12-15');
        // Use more specific selectors if possible, but existing ones worked for creation
        await page.locator('label:has-text("Paket Sayisi")').locator('..').locator('input').fill(uniquePkg.toString());
        await page.locator('label:has-text("Tutar (KDV Haric)")').locator('..').locator('input').fill(uniqueAmt.toString());
        await page.locator('button:has-text("Kaydet")').click();

        // 6. Verify Creation
        await expect(page.locator('table')).toContainText(uniquePkg.toString());

        // 7. Delete Record
        const row = page.locator('tr').filter({ hasText: uniquePkg.toString() });
        await row.getByRole('button', { name: 'Sil' }).click();

        // 8. Confirm Modal
        console.log("Waiting for Confirm Modal...");
        const modal = page.locator('div.fixed h3:has-text("Onay")');
        await expect(modal).toBeVisible();
        await page.click('button:has-text("Evet, Sil")');
        console.log("Clicked Confirm.");

        // 9. Verify Deletion
        // Check for empty state message instead of table visibility
        const emptyState = page.locator('div').filter({ hasText: 'Bu donemde kayit bulunamadi' }).first();
        await expect(emptyState).toBeVisible();

        // Also verify table is NOT visible (double check)
        await expect(page.locator('table')).not.toBeVisible();

        console.log("Courier Expense Delete Verified!");
    });
});
