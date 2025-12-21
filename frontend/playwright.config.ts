import { defineConfig, devices } from '@playwright/test';
import { config } from './tests/e2e/_config/test_config';

/**
 * Cigkoftecibey Webapp - Playwright Test Configuration
 *
 * Test Categories:
 * - @auth     : Authentication tests
 * - @dashboard: Dashboard & reporting
 * - @sales    : Sales entry
 * - @inventory: Production & purchases
 * - @expenses : All expense types
 * - @hr       : Personnel & SGK
 * - @admin    : Settings & admin features
 *
 * Run specific category:
 *   npx playwright test --grep @expenses
 *   npx playwright test --grep @smoke
 *
 * Run specific folder:
 *   npx playwright test tests/e2e/expenses/
 */

export default defineConfig({
    testDir: './tests/e2e',

    /* Run tests in files in parallel */
    fullyParallel: false,  // Serial for data-dependent tests

    /* Fail the build on CI if you accidentally left test.only in the source code */
    forbidOnly: !!process.env.CI,

    /* Retry on CI only */
    retries: process.env.CI ? 2 : 1,

    /* Single worker for serial execution */
    workers: 1,

    /* Reporter to use */
    reporter: [
        ['list'],
        ['html', { open: 'never' }],
    ],

    /* Global timeout */
    timeout: 60000,

    /* Shared settings for all projects */
    use: {
        baseURL: config.frontendUrl,
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
    },

    /* Configure projects for different test suites */
    projects: [
        // Main browser - all tests
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },

        // Smoke tests - critical paths only
        {
            name: 'smoke',
            use: { ...devices['Desktop Chrome'] },
            grep: /@smoke/,
            testDir: './tests/e2e',
        },

        // Auth tests only
        {
            name: 'auth',
            use: { ...devices['Desktop Chrome'] },
            testDir: './tests/e2e/auth',
        },

        // Dashboard tests only
        {
            name: 'dashboard',
            use: { ...devices['Desktop Chrome'] },
            testDir: './tests/e2e/dashboard',
        },

        // Sales tests only
        {
            name: 'sales',
            use: { ...devices['Desktop Chrome'] },
            testDir: './tests/e2e/sales',
        },

        // Inventory tests only
        {
            name: 'inventory',
            use: { ...devices['Desktop Chrome'] },
            testDir: './tests/e2e/inventory',
        },

        // Expense tests only
        {
            name: 'expenses',
            use: { ...devices['Desktop Chrome'] },
            testDir: './tests/e2e/expenses',
        },

        // HR tests only
        {
            name: 'hr',
            use: { ...devices['Desktop Chrome'] },
            testDir: './tests/e2e/hr',
        },

        // Admin tests only
        {
            name: 'admin',
            use: { ...devices['Desktop Chrome'] },
            testDir: './tests/e2e/admin',
        },
    ],

    /* Run your local dev server before starting the tests */
    webServer: {
        command: `npm run dev -- --port ${config.frontendPort}`,
        url: config.frontendUrl,
        reuseExistingServer: !process.env.CI,
        timeout: 120000,
    },
});
