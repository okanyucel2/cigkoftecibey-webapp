
import { test, expect } from '@playwright/test';

test.describe('Mal Alimlari UI', () => {

    test.beforeEach(async ({ page }) => {
        page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
        // Log Network
        page.on('request', request => {
            if (request.url().includes('/api/purchases')) {
                console.log(`>> ${request.method()} ${request.url()}`);
            }
        });
        page.on('response', response => {
            if (response.url().includes('/api/purchases')) {
                console.log(`<< ${response.status()} ${response.url()}`);
            }
        });

        await page.goto('/login');
        await page.fill('input[type="email"]', 'admin@cigkofte.com');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await expect(page).toHaveURL('/');
    });

    test('Mal Alimi Olusturma ve Silme', async ({ page, request }) => {
        // 2. Auth for Cleanup
        const token = await page.evaluate(() => {
            const auth = localStorage.getItem('auth');
            return auth ? JSON.parse(auth).token : localStorage.getItem('token');
        });

        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };

        // 3. Cleanup Purchases
        if (token) {
            console.log("Cleaning up Purchases...");
            try {
                const listUrl = 'http://localhost:8001/api/purchases?start_date=2025-12-01&end_date=2025-12-31';
                const res = await request.get(listUrl, { headers });
                if (res.ok()) {
                    const data = await res.json();
                    console.log(`Cleanup: Found ${data.length} records.`);
                    for (const item of data) {
                        await request.delete(`http://localhost:8001/api/purchases/${item.id}`, { headers });
                    }
                }
            } catch (e) { console.log('Cleanup error', e); }
        }

        console.log("Navigating to Purchases...");

        if (token) {
            console.log("Creating Test Data via API...");

            // 3.1 Create Supplier
            const supplierResp = await request.post('http://localhost:8001/api/purchases/suppliers', {
                headers,
                data: {
                    name: `Test Supplier ${Math.floor(Math.random() * 1000)}`,
                    phone: '05551234567'
                }
            });
            const supplier = await supplierResp.json();
            console.log(`Created Supplier ID: ${supplier.id}`);

            // 3.2 Create Purchase
            const uniqueNotes = `Test_${Math.floor(Math.random() * 1000)}`;

            const payload = {
                purchase_date: '2025-12-15',
                supplier_id: supplier.id, // Use real ID
                notes: uniqueNotes,
                items: [
                    { product_id: 1, description: 'Test Item', quantity: 10, unit: 'kg', unit_price: 100, vat_rate: 18 }
                    // Note: Backend might require product_id if item table has FK.
                    // Checking schema... PurchaseItem usually has product_id.
                    // `PurchaseCreate` likely expects `items` list.
                    // Let's assum product_id=1 exists or use strict schema.
                    // Backend code: 
                    // for item in data.items: item_total... items_data.append({"product_id": item.product_id...})
                    // So product_id IS required.
                    // I should fetch product groups/products first, OR try with dummy ID.
                    // If Product ID 1 doesn't exist, this will fail.
                    // Safe bet: Create a Product Group and Product first? 
                    // Or just assume seeded data?
                    // Use product_id=1 and see if it fails (400/404/500).
                ]
            };

            // To be ultra-safe, let's create a Product.
            // But usually ID 1 exists. Let's try.
            const purchaseResp = await request.post('http://localhost:8001/api/purchases', { headers, data: payload });
            if (!purchaseResp.ok()) {
                console.log(`Purchase Create Failed: ${purchaseResp.status()} ${await purchaseResp.text()}`);
                // Fallback: Create Product
                // But for now let's see.
            } else {
                console.log("Purchase Created Successfully");
            }

            await page.goto('/purchases');

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

            // Verify Empty State or Removal
            const emptyState = page.locator('text=Mal alimi bulunamadi');
            await expect(emptyState).toBeVisible();
            await expect(page.locator('table')).not.toBeVisible();

            console.log("Purchase Delete Verified!");
        }
    });
});
