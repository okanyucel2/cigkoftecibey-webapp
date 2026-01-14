// @smoke @critical
// Pre-flight check: Dashboard KPI cards display correctly
import { test, expect } from '@playwright/test';
import { config } from '../_config/test_config';

test.describe('📊 Dashboard Functional', () => {
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

        // Navigate to DashboardV2 (KPI dashboard)
        await page.goto(config.frontendUrl + '/dashboard-v2')
        await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
    });

    test('Verify Dashboard KPI Grid Loads', async ({ page }) => {
        // Wait for KPI grid using data-testid (DashboardV2 structure)
        await expect(async () => {
            const kpiGrid = page.locator('[data-testid="kpi-grid"]')
            await expect(kpiGrid).toBeVisible()
        }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

        // Verify at least one KPI card is visible
        const kpiCards = page.locator('[data-testid^="kpi-"]')
        const count = await kpiCards.count()
        console.log(`Found ${count} KPI cards`)
        expect(count).toBeGreaterThan(0)

        // Verify specific KPIs exist
        const netCiro = page.locator('[data-testid="kpi-net-ciro"]')
        const kasaFarki = page.locator('[data-testid="kpi-kasa-farki"]')

        await expect(netCiro).toBeVisible()
        await expect(kasaFarki).toBeVisible()

        console.log('Dashboard KPI grid verified successfully')
    });

    test('Verify Hub Widgets Load', async ({ page }) => {
        // Wait for Hub grid using data-testid
        await expect(async () => {
            const hubGrid = page.locator('[data-testid="hub-grid"]')
            await expect(hubGrid).toBeVisible()
        }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

        // Verify hub widgets exist (using data-testid attribute)
        const hubs = page.locator('[data-testid^="hub-"]:not([data-testid="hub-grid"])')
        const hubCount = await hubs.count()
        console.log(`Found ${hubCount} hub widgets`)
        expect(hubCount).toBeGreaterThan(0)

        console.log('Dashboard hub widgets verified successfully')
    });
});
