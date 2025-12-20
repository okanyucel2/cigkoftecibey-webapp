import { test, expect } from '@playwright/test';
import { config } from './test_config';

test.describe('Login Page Tests @smoke', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    // Wait for the form to be visible
    await expect(page.locator('form')).toBeVisible({ timeout: 10000 });
  });

  test('Verify login page UI elements', async ({ page }) => {
    // Check for essential inputs and buttons
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    const loginButton = page.locator('button[type="submit"]');
    await expect(loginButton).toBeVisible();

    // Check if the page title contains "Login" or "Giriş" (Turkish equivalent)
    const title = await page.title();
    expect(title.toLowerCase()).toMatch(/login|giriş|panel|yonetim|sistemi/);
  });

  test('Verify error message for incorrect credentials', async ({ page }) => {
    // Fill with invalid data
    await page.fill('input[type="email"]', 'wrong@example.com');
    await page.fill('input[type="password"]', 'incorrect123');
    await page.click('button[type="submit"]');

    // Look for error message - using robust data-testid
    const errorMsg = page.locator('[data-testid="error-message"]').first();
    await expect(errorMsg).toBeVisible({ timeout: 10000 });

    // Check for common error texts (case-insensitive)
    const content = await errorMsg.textContent();
    expect(content?.toLowerCase()).toMatch(/invalid|incorrect|geçersiz|hata/);
  });

  test('Verify successful login and redirection', async ({ page }) => {
    // Use standardized credentials from test_config.ts
    console.log(`Attempting login with: ${config.auth.email}`);

    await page.fill('input[type="email"]', config.auth.email);
    await page.fill('input[type="password"]', config.auth.password);

    // Trigger login
    await page.click('button[type="submit"]');

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
    const passwordInput = page.locator('input[type="password"]');
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

});
