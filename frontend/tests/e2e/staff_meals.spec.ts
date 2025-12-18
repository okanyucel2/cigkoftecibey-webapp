
import { test, expect } from '@playwright/test';

test.describe('Personel Yemek UI', () => {

    test.beforeEach(async ({ page }) => {
        page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
        // Log Network
        page.on('request', request => {
            if (request.url().includes('/api/staff-meals')) {
                console.log(`>> ${request.method()} ${request.url()}`);
            }
        });
        page.on('response', response => {
            if (response.url().includes('/api/staff-meals')) {
                console.log(`<< ${response.status()} ${response.url()}`);
            }
        });

        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@cigkofte.com');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await expect(page).toHaveURL('/');
    });

    test('Yemek Kaydi Olusturma ve Silme', async ({ page, request }) => {
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
            console.log("Cleaning up StaffMeals...");
            try {
                const listUrl = `http://localhost:8001/api/staff-meals?month=12&year=2025`;
                const res = await request.get(listUrl, { headers });
                if (res.ok()) {
                    const data = await res.json();
                    console.log(`Cleanup: Found ${data.length} records.`);
                    for (const item of data) {
                        if (item.meal_date === testDate) {
                            await request.delete(`http://localhost:8001/api/staff-meals/${item.id}`, { headers });
                        }
                    }
                }
            } catch (e) { console.log('Cleanup error', e); }
        }

        console.log("Navigating to StaffMeals...");

        if (token) {
            console.log("Creating Test Data via API...");
            const uniqueNotes = `Test Meal_${Math.floor(Math.random() * 1000)}`;
            const payload = {
                meal_date: testDate,
                unit_price: 150,
                staff_count: 5,
                notes: uniqueNotes
            };

            const resp = await request.post('http://localhost:8001/api/staff-meals', { headers, data: payload });
            if (resp.ok()) {
                console.log("StaffMeal Created Successfully");
            } else {
                console.log(`StaffMeal Create Failed: ${resp.status()} ${await resp.text()}`);
            }

            await page.goto('/staff-meals');

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

            // Verify Empty State
            // Since we cleaned up, it should be empty
            const emptyState = page.locator('text=Bu ay icin kayit bulunamadi');
            await expect(emptyState).toBeVisible();
            await expect(page.locator('table')).not.toBeVisible();

            console.log("StaffMeal Delete Verified!");
        }
    });
});
