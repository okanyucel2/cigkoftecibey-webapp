// @smoke @critical
// Pre-flight check: Dashboard KPI counters update with sales/expenses
import { test, expect } from '@playwright/test';
import { config } from '../_config/test_config';

test.describe('📊 Dashboard Functional', () => {
    // Unique prefix 901x for dashboard (900-999 range)
    const uniquePrefix = '901'
    const uniqueSuffix = Date.now().toString().slice(-4)
    const uniqueId = `${uniquePrefix}_${uniqueSuffix}`

    test.beforeEach(async ({ page, request }) => {
        test.setTimeout(60000)

        // DEBUG LISTENERS
        page.on('console', msg => console.log(`BROWSER [${msg.type()}]: ${msg.text()}`))
        page.on('requestfailed', request => console.log(`NETWORK FAIL: ${request.url()} - ${request.failure()?.errorText}`))

        // API LOGIN BYPASS
        console.log('Attempting API Login...')
        const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', {
            data: {
                email: config.auth.email,
                password: config.auth.password
            }
        })

        if (!loginRes.ok()) {
            console.error('API Login Failed:', loginRes.status(), await loginRes.text())
            throw new Error('API Login Failed')
        }

        const loginData = await loginRes.json()
        const token = loginData.access_token
        console.log('API Login Success. Token obtained.')

        // Inject Token into LocalStorage
        await page.goto(config.frontendUrl + '/login')
        await page.evaluate((t) => {
            localStorage.setItem('token', t)
        }, token)

        // Navigate to dashboard
        await page.goto(config.frontendUrl + '/')
        await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
    });

    test('Verify Sales and Expenses Impact Dashboard Counters', async ({ page, request }) => {
        // 1. Get Auth Token
        const token = await page.evaluate(() => {
            const auth = localStorage.getItem('auth');
            return auth ? JSON.parse(auth).token : localStorage.getItem('token');
        });
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };

        // 2. Fetch Initial Dashboard Values
        // Wait for counters to load using the correct class from Dashboard.vue
        // Note: The structure is <div class="kpi-card ...">
        await expect(page.locator('.kpi-card').first()).toBeVisible();

        // Capture initial values (Parsing currency like "1.250,00 ₺")
        const parseCurrency = (text: string) => {
            return parseFloat(text.replace('₺', '').replace(/\./g, '').replace(',', '.').trim()) || 0;
        };

        const getCounterValue = async (label: string) => {
            const card = page.locator('.kpi-card', { hasText: label }).first();
            await card.waitFor({ state: 'visible' });

            // The value is in a p tag with text-2xl class (from Dashboard.vue)
            const valueText = await card.locator('.text-2xl, .font-display, h2, h3').first().textContent();
            return parseCurrency(valueText || '0');
        };

        // Labels in Dashboard.vue: "Toplam Ciro", "Toplam Gider", "Net Kar"
        const initialSales = await getCounterValue("Toplam Ciro");
        const initialExpenses = await getCounterValue("Toplam Gider");
        const initialProfit = await getCounterValue("Net Kar");

        console.log(`Initial: Sales=${initialSales}, Expenses=${initialExpenses}, Profit=${initialProfit}`);

        // 3. Create Test Data
        const uniqueNote = `FuncTest_${uniqueId}`;
        const saleAmount = 9011;  // 901 prefix + operation 1
        const expenseAmount = 9012;  // 901 prefix + operation 2
        const testDate = new Date().toISOString().split('T')[0];

        // 3.1 Create Expense
        // Create Expense Category first
        const catResp = await request.post(`${config.backendUrl}/api/expenses/categories`, {
            headers,
            data: { name: `TestCat_${uniqueId}`, is_fixed: false }
        });
        const catId = (await catResp.json()).id;

        // Create Expense
        await request.post(`${config.backendUrl}/api/expenses`, {
            headers,
            data: {
                expense_date: testDate,
                category_id: catId,
                description: uniqueNote,
                amount: expenseAmount
            }
        });

        // 3.2 Create Online Sale
        // Create/Get Platform
        const platformResp = await request.get(`${config.backendUrl}/api/online-sales/channels`, { headers }); // Assuming 'channels' endpoint lists platforms
        let platformId;
        // The endpoint might be /online-sales/platforms based on unified_sales.spec.ts usage
        // Checking unified_sales.spec.ts: it uses /api/online-sales/platforms
        // Let's use that.
        const platRespCorrect = await request.get(`${config.backendUrl}/api/online-sales/platforms`, { headers });
        if (platRespCorrect.ok()) { // Use check if endpoint exists
            const platforms = await platRespCorrect.json();
            if (platforms.length > 0) {
                platformId = platforms[0].id;
            }
        }

        if (!platformId) {
            const newPlat = await request.post(`${config.backendUrl}/api/online-sales/platforms`, {
                headers, data: { name: `FuncTestPlat_${uniqueId}`, commission_rate: 0 }
            });
            platformId = (await newPlat.json()).id;
        }

        // Create Daily Sale Record (Non-destructive: Fetch current day first and add to it)
        const currentSalesResp = await request.get(`${config.backendUrl}/api/online-sales/today`, { headers });
        const currentSales = await currentSalesResp.json();

        // Find existing entry or create new one
        const entries = currentSales.entries.map((e: any) => ({
            platform_id: e.platform_id,
            amount: e.platform_id === platformId ? e.amount + saleAmount : e.amount
        }));

        const saleResp = await request.post(`${config.backendUrl}/api/online-sales/daily`, {
            headers,
            data: {
                sale_date: testDate,
                entries: entries
            }
        });
        console.log(`Sale Creation Status: ${saleResp.status()}`);
        if (!saleResp.ok()) {
            console.log(`Sale Creation Error: ${await saleResp.text()}`);
        }

        console.log(`Created Data: Added Sale +${saleAmount} to Platform ${platformId}, Added Expense +${expenseAmount}`);

        // 4. Refresh & Verify
        await page.reload();
        await expect(page.locator('.kpi-card').first()).toBeVisible();

        const finalSales = await getCounterValue("Toplam Ciro");
        const finalExpenses = await getCounterValue("Toplam Gider");
        const finalProfit = await getCounterValue("Net Kar");

        console.log(`Final: Sales=${finalSales}, Expenses=${finalExpenses}, Profit=${finalProfit}`);

        // 5. Assertions
        expect(finalSales).toBeCloseTo(initialSales + saleAmount, 1);
        expect(finalExpenses).toBeCloseTo(initialExpenses + expenseAmount, 1);
        expect(finalProfit).toBeCloseTo(initialProfit + (saleAmount - expenseAmount), 1);

        console.log("Test Passed! Logic holds up.");
    });
});
