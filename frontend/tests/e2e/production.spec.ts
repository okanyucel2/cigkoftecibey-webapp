
import { test, expect } from '@playwright/test';

test.describe('Gunluk Uretim UI', () => {

    test.beforeEach(async ({ page }) => {
        page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
        // Log Network
        page.on('request', request => {
            if (request.url().includes('/api/production')) {
                console.log(`>> ${request.method()} ${request.url()}`);
            }
        });
        page.on('response', response => {
            if (response.url().includes('/api/production')) {
                console.log(`<< ${response.status()} ${response.url()}`);
            }
        });

        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@cigkofte.com');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await expect(page).toHaveURL('/');
    });

    test('Uretim Girisi ve Silme', async ({ page, request }) => {
        // 2. Auth for Cleanup
        const token = await page.evaluate(() => {
            const auth = localStorage.getItem('auth');
            return auth ? JSON.parse(auth).token : localStorage.getItem('token');
        });

        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };

        const testDate = '2025-12-15';

        // 3. Cleanup existing for this date
        if (token) {
            console.log("Cleaning up Production...");
            try {
                const listUrl = `http://localhost:8001/api/production?month=12&year=2025`;
                const res = await request.get(listUrl, { headers });
                if (res.ok()) {
                    const data = await res.json();
                    console.log(`Cleanup: Found ${data.length} records.`);
                    for (const item of data) {
                        if (item.production_date === testDate) {
                            await request.delete(`http://localhost:8001/api/production/${item.id}`, { headers });
                        }
                    }
                }
            } catch (e) { console.log('Cleanup error', e); }
        }

        console.log("Navigating to Production...");

        if (token) {
            console.log("Creating Test Data via API...");
            const uniqueNotes = `Test Prod_${Math.floor(Math.random() * 1000)}`;
            const payload = {
                production_date: testDate,
                kneaded_kg: 200,
                legen_kg: 10,
                legen_cost: 500,
                notes: uniqueNotes
            };

            const resp = await request.post('http://localhost:8001/api/production', { headers, data: payload });
            if (resp.ok()) {
                console.log("Production Created Successfully");
            } else {
                console.log(`Production Create Failed: ${resp.status()} ${await resp.text()}`);
            }

            await page.goto('/production');

            // Select Year 2025, Month 12
            await page.locator('select').first().selectOption('12'); // Month
            await page.locator('select').nth(1).selectOption('2025'); // Year

            // Verify Row exists
            await expect(page.locator('table')).toContainText(uniqueNotes);

            // Delete
            const row = page.locator('tr').filter({ hasText: uniqueNotes });
            await row.getByRole('button', { name: 'Sil' }).click();

            // Modal Interaction
            const modal = page.locator('div.fixed h3:has-text("Onay")');
            await expect(modal).toBeVisible();
            await page.click('button:has-text("Evet, Sil")');

            // Verify specific item removal (list might not be empty)
            await expect(page.locator('table')).not.toContainText(uniqueNotes);

            console.log("Production Delete Verified!");
        }
    });
});
