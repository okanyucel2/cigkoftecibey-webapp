// @smoke
// Pre-flight check: Authentication must work before deploy
import { test, expect } from '@playwright/test';
import { config } from '../_config/test_config';

test.describe('🔐 Login', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    // Wait for the email input to be visible (more specific than just 'form')
    await expect(page.locator('[data-testid="input-email"]')).toBeVisible({ timeout: 10000 });
  });

  test('Verify login page UI elements', async ({ page }) => {
    // Check for essential inputs and buttons using data-testid selectors
    await expect(page.locator('[data-testid="input-email"]')).toBeVisible();
    await expect(page.locator('[data-testid="input-password"]')).toBeVisible();
    const loginButton = page.locator('[data-testid="btn-login"]');
    await expect(loginButton).toBeVisible();

    // Check if the page title contains "Login" or "Giriş" (Turkish equivalent)
    const title = await page.title();
    expect(title.toLowerCase()).toMatch(/login|giriş|panel|yonetim|sistemi/);
  });

  test('Verify error message for incorrect credentials', async ({ page }) => {
    // Fill with invalid data using data-testid selectors
    await page.fill('[data-testid="input-email"]', 'wrong@example.com');
    await page.fill('[data-testid="input-password"]', 'incorrect123');
    await page.click('[data-testid="btn-login"]');

    // Look for error message - using updated data-testid
    const errorMsg = page.locator('[data-testid="login-error-message"]');
    await expect(errorMsg).toBeVisible({ timeout: 10000 });

    // Check for common error texts (case-insensitive)
    const content = await errorMsg.textContent();
    expect(content?.toLowerCase()).toMatch(/invalid|incorrect|geçersiz|hata/);
  });

  test('Verify successful login and redirection', async ({ page }) => {
    // Use standardized credentials from test_config.ts
    console.log(`Attempting login with: ${config.auth.email}`);

    await page.fill('[data-testid="input-email"]', config.auth.email);
    await page.fill('[data-testid="input-password"]', config.auth.password);

    // Trigger login
    await page.click('[data-testid="btn-login"]');

    // Wait for navigation or success indicator
    // Wait for navigation or success indicator (allow root or dashboard)
    await page.waitForURL(url => {
      const path = new URL(url).pathname;
      return path === '/' || path.includes('/dashboard');
    }, { timeout: 15000 });

    // Verify we are no longer on the login page
    expect(page.url()).not.toContain('/login');
  });


  test('Test password visibility toggle', async ({ page }) => {
    const passwordInput = page.locator('[data-testid="input-password"]');
    const toggleButton = page.locator('.password-toggle, .toggle-password, [aria-label*="password"]').first();

    if (await toggleButton.isVisible()) {
      await passwordInput.fill('secret-pass');
      await expect(passwordInput).toHaveAttribute('type', 'password');

      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute('type', 'text');

      await toggleButton.click();
      await expect(passwordInput).toHaveAttribute('type', 'password');
    } else {
      test.skip(true, 'Password visibility toggle button not found on this UI.');
    }
  });

  test('Verify API login endpoint works', async ({ request }) => {
    // Test the API login directly (used by other tests for bypass)
    const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', {
      data: {
        email: config.auth.email,
        password: config.auth.password
      }
    })

    expect(loginRes.ok()).toBe(true)

    const data = await loginRes.json()
    expect(data.access_token).toBeDefined()
    expect(data.access_token.length).toBeGreaterThan(10)

    console.log('API Login verified - token obtained')
  })

  test('Verify API login rejects invalid credentials', async ({ request }) => {
    const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', {
      data: {
        email: 'invalid@test.com',
        password: 'wrongpassword'
      }
    })

    expect(loginRes.ok()).toBe(false)
    expect(loginRes.status()).toBe(401)
  })

});
