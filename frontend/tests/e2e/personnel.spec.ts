import { test, expect } from '@playwright/test';
import { config } from './test_config';

test.describe.configure({ mode: 'serial' });

test.describe('Personnel Management - Create Personnel', () => {

  test.beforeEach(async ({ page, request }) => {
    test.setTimeout(60000);

    // DEBUG LISTENERS
    page.on('console', msg => console.log(`BROWSER [${msg.type()}]: ${msg.text()}`));
    page.on('requestfailed', request => console.log(`NETWORK FAIL: ${request.url()} - ${request.failure()?.errorText}`));

    // API LOGIN BYPASS
    console.log('Attempting API Login...');
    const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', {
      data: {
        email: config.auth.email,
        password: config.auth.password
      }
    });

    if (!loginRes.ok()) {
      console.error('API Login Failed:', loginRes.status(), await loginRes.text());
      throw new Error('API Login Failed');
    }

    const loginData = await loginRes.json();
    const token = loginData.access_token;
    console.log('API Login Success. Token obtained.');

    // Inject Token into LocalStorage
    await page.goto(config.frontendUrl + '/login'); // Go to site to set LS
    await page.evaluate((t) => {
      localStorage.setItem('token', t);
      // Force Pinia persistence if needed? AuthStore reads on init.
    }, token);

    // Now navigate to target
    await page.goto(config.frontendUrl + '/personnel');
  });

  test('Create Personnel - Happy Path', async ({ page }) => {
    const uniqueId = Date.now().toString();
    const uniqueName = `Test Employee ${uniqueId}`;
    const testSalary = '5000';

    await page.goto(config.frontendUrl + '/personnel');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('[data-testid="personnel-list"]')).toBeVisible({ timeout: 10000 });

    await page.click('[data-testid="btn-add-personnel"]');
    await page.waitForTimeout(500);

    await page.fill('[data-testid="input-personnel-name"]', uniqueName);
    await page.fill('[data-testid="input-personnel-salary"]', testSalary);

    const roleField = page.locator('[data-testid="input-personnel-role"]');
    const isRoleVisible = await roleField.isVisible().catch(() => false);
    if (isRoleVisible) {
      await roleField.fill('Chef');
      console.log('NOTE: Role field found and filled with "Chef"');
    } else {
      console.log('NOTE: Role field not found in form, skipping as per plan');
    }

    await page.click('[data-testid="btn-save-personnel"]');

    await expect(async () => {
      const currentUrl = page.url();
      expect(currentUrl).not.toContain('/new');
      expect(currentUrl).not.toContain('/edit');
    }).toPass({ timeout: 10000 });

    await page.reload();
    await page.waitForLoadState('networkidle');

    await expect(async () => {
      const personnelList = page.locator('[data-testid="personnel-list"]');
      await expect(personnelList).toBeVisible();
      const nameCell = personnelList.locator('text=' + uniqueName);
      await expect(nameCell).toBeVisible();
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] });

    await expect(async () => {
      const personnelList = page.locator('[data-testid="personnel-list"]');
      const rows = personnelList.locator('tr:has-text("' + uniqueName + '")');
      await expect(rows.first()).toBeVisible();
      const salaryCell = rows.first().locator('text=/5[,.]?000/');
      await expect(salaryCell).toBeVisible();
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] });
  });
});