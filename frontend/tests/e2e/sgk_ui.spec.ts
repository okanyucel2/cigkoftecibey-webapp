
import { test, expect } from '@playwright/test';
import { config } from './test_config';

test.describe('SGK ve Prim Yönetimi UI', () => {

    test.beforeEach(async ({ page }) => {
        // Enable console log capture
        page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));

        // Log Network
        page.on('response', async response => {
            const url = response.url();
            if (url.includes('/api/personnel/payroll')) {
                const status = response.status();
                const method = response.request().method();
                console.log(`NETWORK: ${method} ${url} [${status}]`);
                if (method === 'GET' && status === 200) {
                    try {
                        const json = await response.json();
                        console.log(`LIST RESPONSE: Found ${json.length} records`);
                    } catch (e) { }
                }
                if (method === 'POST' && (status === 200 || status === 201)) {
                    try {
                        const json = await response.json();
                        console.log(`CREATE RESPONSE: ID=${json.id} AMOUNT=${json.sgk_amount}`);
                    } catch (e) { }
                }
            }
        });

        // 1. LOGIN IS FIRST to get Token
        await page.goto('/login');
        await page.fill('input[type="email"]', config.auth.email);
        await page.fill('input[type="password"]', config.auth.password);
        await page.click('button[type="submit"]');
        await expect(page).toHaveURL('/');
    });

    test('SGK Ödemesi Ekleme ve Silme (UI Kontrolü)', async ({ page, request }) => {

        // 2. Get Token for Cleanup
        const token = await page.evaluate(() => {
            const auth = localStorage.getItem('auth');
            return auth ? JSON.parse(auth).token : localStorage.getItem('token');
        });

        // 3. CLEANUP
        if (token) {
            console.log("Cleaning up for fresh test (Authenticated)...");
            try {
                const headers = { 'Authorization': `Bearer ${token}` };
                const apiUrl = `${config.backendUrl}/api/personnel/payroll`;
                const response = await request.get(`${apiUrl}?year=2025&month=12`, { headers });

                if (response.ok()) {
                    const records = await response.json();
                    console.log(`Cleanup: Found ${records.length} records.`);
                    for (const rec of records) {
                        const del = await request.delete(`${apiUrl}/${rec.id}`, { headers });
                        console.log(`Deleted ID ${rec.id}: ${del.status()}`);
                    }
                } else {
                    console.log(`Cleanup GET failed: ${response.status()}`);
                }
            } catch (e) {
                console.log("Cleanup failed:", e);
            }
        }

        console.log("Navigating to Personnel page...");
        await page.goto('/personnel');

        // 4. Switch to Payroll Tab
        await page.click('button:has-text("Personel Odemeleri")');

        // 5. Click "Add Payment"
        await page.click('button:has-text("+ Odeme Ekle")');

        // 6. Fill Form
        console.log("Filling Payment Form...");

        // Wait for modal
        await expect(page.locator('h2:has-text("Yeni Odeme")')).toBeVisible();

        // Standard wait for animation
        await page.waitForTimeout(500);

        // Select first employee
        await page.locator('form select').first().selectOption({ index: 1 });

        // Select SGK type
        await page.locator('form select').nth(1).selectOption('sgk');

        // Fixed Date (Dec 15)
        const targetDate = '2025-12-15';
        await page.locator('input[type="date"]').fill(targetDate);

        // Wait for SGK input
        await expect(page.locator('label:has-text("SGK Tutari")')).toBeVisible();

        // Unique Amount
        const uniqueVal = 7337;
        const amountStr = uniqueVal.toString();
        const formattedAmount = new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 0 }).format(uniqueVal);

        console.log(`Testing with Amount: ${amountStr} (Checking for: ${formattedAmount})`);

        // Fill SGK Amount
        await page.locator('input[type="number"]').last().fill(amountStr);

        // Fill Notes
        await page.locator('input[placeholder="Opsiyonel..."]').fill(`Test Delete UI`);

        // 7. Submit
        await page.click('button:has-text("Kaydet")');

        // 8. Verify it appears in table
        console.log("Verifying Row Creation...");
        await page.waitForTimeout(1000); // Wait for refresh

        // Assert visibility
        await expect(page.locator('tbody')).toContainText(formattedAmount);

        // 9. Delete it
        console.log("Attempting Delete...");

        // Find row specifically
        const row = page.locator('tr').filter({ hasText: formattedAmount });

        // Verify delete button exists
        await expect(row.getByRole('button', { name: 'Sil' })).toBeVisible();

        // Click Delete button on ROW
        await row.getByRole('button', { name: 'Sil' }).click();

        // *** NEW: Handle Custom Modal ***
        console.log("Waiting for Custom Confirmation Modal...");
        const confirmModal = page.locator('div.fixed h3:has-text("Onay")');
        await expect(confirmModal).toBeVisible();

        // CLick "Evet, Sil"
        console.log("Clicking Confirm...");
        await page.click('button:has-text("Evet, Sil")');

        // Wait for potential network request
        await page.waitForTimeout(1000);

        // 10. Verify deletion
        const emptyState = page.locator('text=Bu ay icin bordro kaydi bulunamadi');

        // Either empty state visible OR row gone
        if (await emptyState.isVisible()) {
            console.log("Empty state found.");
        } else {
            await expect(page.locator('tbody')).not.toContainText(formattedAmount);
        }

        console.log("Deletion Verified!");
    });
});
