import { test, expect } from '@playwright/test'
import { config } from '../_config/test_config'

test.describe('Menu Management E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login first with correct demo credentials
    await page.goto(`${config.frontendUrl}/login`)
    await page.fill('input[type="email"]', config.auth.email)
    await page.fill('input[type="password"]', config.auth.password)
    await page.click('button[type="submit"]')

    // Wait for redirect to dashboard
    await page.waitForURL(`${config.frontendUrl}/`, { timeout: 15000 })
  })

  test('should display menu management page with tabs', async ({ page }) => {
    // Navigate to menu page
    await page.goto(`${config.frontendUrl}/menu`)
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Take screenshot
    await page.screenshot({ path: '/tmp/menu-management-page.png', fullPage: true });
    
    // Verify page title
    await expect(page.locator('main h1')).toContainText('Menu Yonetimi');
    
    // Verify tabs exist
    await expect(page.locator('button:has-text("Kategoriler")')).toBeVisible();
    await expect(page.locator('button:has-text("Urunler")')).toBeVisible();
    
    // Click on Items tab
    await page.click('button:has-text("Urunler")');
    await page.waitForTimeout(500);
    await page.screenshot({ path: '/tmp/menu-items-tab.png', fullPage: true });
    
    // Verify items tab content
    await expect(page.locator('button:has-text("+ Yeni Urun")')).toBeVisible();
    
    console.log('✅ Menu Management page loaded successfully');
    console.log('✅ Categories tab visible');
    console.log('✅ Items tab visible');
    console.log('📸 Screenshots saved to /tmp/');
  });

  test('should open category modal', async ({ page }) => {
    await page.goto(`${config.frontendUrl}/menu`);
    await page.waitForLoadState('networkidle');
    
    // Click new category button
    await page.click('button:has-text("+ Yeni Kategori")');
    
    // Wait for modal
    await page.waitForTimeout(300);
    
    // Verify modal opens
    await expect(page.locator('h2:has-text("Yeni Kategori")')).toBeVisible();
    
    // Take screenshot of modal
    await page.screenshot({ path: '/tmp/category-modal.png', fullPage: true });
    
    console.log('✅ Category modal opens correctly');
  });
});
