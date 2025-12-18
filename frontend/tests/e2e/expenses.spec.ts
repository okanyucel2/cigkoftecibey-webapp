
import { test, expect } from '@playwright/test';
import { config } from './test_config';

test.describe('Isletme Giderleri UI', () => {

    test.beforeEach(async ({ page }) => {
        page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
        // Log Network
        page.on('request', request => {
            if (request.url().includes('/api/expenses')) {
                console.log(`>> ${request.method()} ${request.url()}`);
            }
        });
        page.on('response', response => {
            if (response.url().includes('/api/expenses')) {
                console.log(`<< ${response.status()} ${response.url()}`);
            }
        });

        await page.goto('/login');
        await page.fill('input[type="email"]', config.auth.email);
        await page.fill('input[type="password"]', config.auth.password);
        await page.click('button[type="submit"]');
        await expect(page).toHaveURL('/');
    });

    test('Gider Olusturma ve Silme', async ({ page, request }) => {
        // 2. Auth for Cleanup
        const token = await page.evaluate(() => {
            const auth = localStorage.getItem('auth');
            return auth ? JSON.parse(auth).token : localStorage.getItem('token');
        });

        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };

        // 3. Cleanup Expenses
        if (token) {
            console.log("Cleaning up Expenses...");
            try {
                const listUrl = `${config.backendUrl}/api/expenses?start_date=2025-12-01&end_date=2025-12-31`;
                const res = await request.get(listUrl, { headers });
                if (res.ok()) {
                    const data = await res.json();
                    console.log(`Cleanup: Found ${data.length} records.`);
                    for (const item of data) {
                        await request.delete(`${config.backendUrl}/api/expenses/${item.id}`, { headers });
                    }
                }
            } catch (e) { console.log('Cleanup error', e); }
        }

        console.log("Navigating to Expenses...");

        if (token) {
            console.log("Creating Test Data via API...");

            // 3.1 Create Category
            const catResp = await request.post(`${config.backendUrl}/api/expenses/categories`, {
                headers,
                data: {
                    name: `Test Cat ${Math.floor(Math.random() * 1000)}`,
                    is_fixed: false
                }
            });
            const category = await catResp.json();
            console.log(`Created Category ID: ${category.id}`);

            // 3.2 Create Expense
            const uniqueDesc = `Test Expense_${Math.floor(Math.random() * 1000)}`;
            const payload = {
                expense_date: '2025-12-15',
                category_id: category.id,
                description: uniqueDesc,
                amount: 500
            };

            const expResp = await request.post(`${config.backendUrl}/api/expenses`, { headers, data: payload });
            if (expResp.ok()) {
                console.log("Expense Created Successfully");
            } else {
                console.log(`Expense Create Failed: ${expResp.status()}`);
            }

            await page.goto('/expenses');

            // Select Year 2025, Month 12
            await page.locator('select').first().selectOption('12'); // Month
            await page.locator('select').nth(1).selectOption('2025'); // Year

            // Make sure filter is set
            await expect(page.locator('table')).toContainText(uniqueDesc);

            // Delete
            const row = page.locator('tr').filter({ hasText: uniqueDesc });
            await row.getByRole('button', { name: 'Sil' }).click();

            // Modal Interaction
            const modal = page.locator('div.fixed h3:has-text("Onay")');
            await expect(modal).toBeVisible();
            await page.click('button:has-text("Evet, Sil")');

            // Verify Empty State or Removal
            const emptyState = page.locator('text=Bu donemde gider bulunamadi');
            await expect(emptyState).toBeVisible();
            await expect(page.locator('table')).not.toBeVisible();

            console.log("Expense Delete Verified!");
        }
    });
});
