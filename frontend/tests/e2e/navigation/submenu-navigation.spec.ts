// @smoke
// Phase 1 Task 1.2: Submenu Navigation Tests
// TDD: Tests written FIRST before implementation verification
// Tests verify VerticalNav component submenu behavior
//
// NOTE: Uses mock auth for local dev speed (no Docker required)
// TODO: CI Pipeline must verify against real backend with Docker/PostgreSQL
import { test, expect } from '../fixtures/mock-auth'
import { config } from '../_config/test_config'

/**
 * Submenu Navigation Tests
 * ========================
 *
 * Tests for navigation items with submenus (VerticalNav component)
 *
 * Groups with submenus:
 * - Operasyon: /operations/production, /operations/purchases
 * - Personel: /personnel, /personnel/meals, /personnel/payroll
 * - Giderler: /expenses, /expenses/courier
 * - Ciro: /sales, /sales/verify
 */

test.describe('🧭 Submenu Navigation - Phase 1.2', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    test.setTimeout(30000)

    // Go to dashboard and wait for nav to render (auth already injected by fixture)
    await authenticatedPage.goto(config.frontendUrl + '/')
    await authenticatedPage.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
  })

  // ==========================================
  // SUBMENU EXPANSION TESTS
  // ==========================================

  test.describe('Submenu Expansion/Collapse', () => {
    test('Operasyon parent click expands submenu (does not navigate)', async ({ authenticatedPage: page }) => {
      // Find Operasyon nav-item container (parent of both button and submenu)
      const operasyonItem = page.locator('.nav-item:has(.nav-button:has-text("Operasyon"))')
      const operasyonBtn = operasyonItem.locator('.nav-button').first()
      const operasyonSubmenu = operasyonItem.locator('.nav-subitems')

      await expect(operasyonBtn).toBeVisible({ timeout: 5000 })

      // Ensure submenu is collapsed first (click to collapse if expanded)
      const initialExpanded = await operasyonBtn.getAttribute('aria-expanded')
      if (initialExpanded === 'true') {
        await operasyonBtn.click()
        await expect(operasyonSubmenu).not.toBeVisible({ timeout: 3000 })
      }

      // Click to expand
      await operasyonBtn.click()

      // Should now show submenu items
      await expect(operasyonSubmenu).toBeVisible({ timeout: 3000 })

      // aria-expanded should be "true"
      await expect(operasyonBtn).toHaveAttribute('aria-expanded', 'true')

      // URL should NOT have changed (submenu parent doesn't navigate)
      await expect(page).toHaveURL(config.frontendUrl + '/')
    })

    test('Clicking expanded Operasyon collapses submenu', async ({ authenticatedPage: page }) => {
      // Find Operasyon nav-item container
      const operasyonItem = page.locator('.nav-item:has(.nav-button:has-text("Operasyon"))')
      const operasyonBtn = operasyonItem.locator('.nav-button').first()
      const operasyonSubmenu = operasyonItem.locator('.nav-subitems')

      // Ensure it's expanded first
      const initialExpanded = await operasyonBtn.getAttribute('aria-expanded')
      if (initialExpanded !== 'true') {
        await operasyonBtn.click()
        await expect(operasyonSubmenu).toBeVisible({ timeout: 3000 })
      }

      // Click to collapse
      await operasyonBtn.click()

      // Submenu should be hidden
      await expect(operasyonSubmenu).not.toBeVisible({ timeout: 3000 })

      // aria-expanded should be "false"
      await expect(operasyonBtn).toHaveAttribute('aria-expanded', 'false')
    })

    test('Expand icon rotates when expanded', async ({ authenticatedPage: page }) => {
      // Find Operasyon nav-item container
      const operasyonItem = page.locator('.nav-item:has(.nav-button:has-text("Operasyon"))')
      const operasyonBtn = operasyonItem.locator('.nav-button').first()
      const expandIcon = operasyonBtn.locator('.expand-icon')

      await expect(expandIcon).toBeVisible()

      // Ensure collapsed state first
      const initialExpanded = await operasyonBtn.getAttribute('aria-expanded')
      if (initialExpanded === 'true') {
        await operasyonBtn.click()
        await expect(expandIcon).not.toHaveClass(/expanded/)
      }

      // Initially should not have 'expanded' class
      await expect(expandIcon).not.toHaveClass(/expanded/)

      // Click to expand
      await operasyonBtn.click()

      // Should now have 'expanded' class
      await expect(expandIcon).toHaveClass(/expanded/)
    })
  })

  // ==========================================
  // SUBMENU ITEM NAVIGATION TESTS
  // ==========================================

  test.describe('Submenu Item Navigation', () => {
    test('Clicking "İçe Aktar" top-level item navigates to /import', async ({ authenticatedPage: page }) => {
      // İçe Aktar is a top-level nav item (not under Operasyon)
      const importBtn = page.locator('.nav-button:has-text("İçe Aktar")')
      await expect(importBtn).toBeVisible({ timeout: 5000 })
      await importBtn.click()

      // Should navigate to /import
      await expect(page).toHaveURL(config.frontendUrl + '/import')
    })

    test('Clicking "Üretim" submenu item navigates to /operations/production', async ({ authenticatedPage: page }) => {
      // Find Operasyon nav-item container
      const operasyonItem = page.locator('.nav-item:has(.nav-button:has-text("Operasyon"))')
      const operasyonBtn = operasyonItem.locator('.nav-button').first()
      const operasyonSubmenu = operasyonItem.locator('.nav-subitems')

      // Ensure expanded
      const expanded = await operasyonBtn.getAttribute('aria-expanded')
      if (expanded !== 'true') {
        await operasyonBtn.click()
      }
      await expect(operasyonSubmenu).toBeVisible({ timeout: 3000 })

      // Find and click Üretim submenu item
      const uretimBtn = operasyonSubmenu.locator('.subitem:has-text("Üretim")')
      await expect(uretimBtn).toBeVisible()
      await uretimBtn.click()

      // Should navigate to /operations/production
      await expect(page).toHaveURL(config.frontendUrl + '/operations/production')
    })

    test('Clicking "Mal Alım" submenu item navigates to /operations/purchases', async ({ authenticatedPage: page }) => {
      // Find Operasyon nav-item container
      const operasyonItem = page.locator('.nav-item:has(.nav-button:has-text("Operasyon"))')
      const operasyonBtn = operasyonItem.locator('.nav-button').first()
      const operasyonSubmenu = operasyonItem.locator('.nav-subitems')

      // Ensure expanded
      const expanded = await operasyonBtn.getAttribute('aria-expanded')
      if (expanded !== 'true') {
        await operasyonBtn.click()
      }
      await expect(operasyonSubmenu).toBeVisible({ timeout: 3000 })

      // Find and click Mal Alım submenu item
      const malAlimBtn = operasyonSubmenu.locator('.subitem:has-text("Mal Alım")')
      await expect(malAlimBtn).toBeVisible()
      await malAlimBtn.click()

      // Should navigate to /operations/purchases
      await expect(page).toHaveURL(config.frontendUrl + '/operations/purchases')
    })

    test('Clicking "Kurye" under Giderler navigates to /expenses/courier', async ({ authenticatedPage: page }) => {
      // Find Giderler nav-item container
      const giderlerItem = page.locator('.nav-item:has(.nav-button:has-text("Giderler"))')
      const giderlerBtn = giderlerItem.locator('.nav-button').first()
      const giderlerSubmenu = giderlerItem.locator('.nav-subitems')

      // Ensure expanded
      const expanded = await giderlerBtn.getAttribute('aria-expanded')
      if (expanded !== 'true') {
        await giderlerBtn.click()
      }
      await expect(giderlerSubmenu).toBeVisible({ timeout: 3000 })

      // Find and click Kurye submenu item
      const kuryeBtn = giderlerSubmenu.locator('.subitem:has-text("Kurye")')
      await expect(kuryeBtn).toBeVisible({ timeout: 3000 })
      await kuryeBtn.click()

      // Should navigate to /expenses/courier
      await expect(page).toHaveURL(config.frontendUrl + '/expenses/courier')
    })
  })

  // ==========================================
  // AUTO-EXPAND TESTS
  // ==========================================

  test.describe('Auto-Expand on Direct Navigation', () => {
    test('Direct navigation to /operations/production auto-expands Operasyon submenu', async ({ authenticatedPage: page }) => {
      // Navigate directly to subitem route
      await page.goto(config.frontendUrl + '/operations/production')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Find Operasyon nav-item container
      const operasyonItem = page.locator('.nav-item:has(.nav-button:has-text("Operasyon"))')
      const operasyonBtn = operasyonItem.locator('.nav-button').first()
      const operasyonSubmenu = operasyonItem.locator('.nav-subitems')

      // Operasyon submenu should be expanded
      await expect(operasyonBtn).toHaveAttribute('aria-expanded', 'true')
      await expect(operasyonSubmenu).toBeVisible()

      // Üretim item should have active class
      const uretimBtn = operasyonSubmenu.locator('.subitem:has-text("Üretim")')
      await expect(uretimBtn).toHaveClass(/active/)
    })

    test('Direct navigation to /expenses/courier auto-expands Giderler submenu', async ({ authenticatedPage: page }) => {
      // Navigate directly to subitem route
      await page.goto(config.frontendUrl + '/expenses/courier')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Find Giderler nav-item container
      const giderlerItem = page.locator('.nav-item:has(.nav-button:has-text("Giderler"))')
      const giderlerBtn = giderlerItem.locator('.nav-button').first()
      const giderlerSubmenu = giderlerItem.locator('.nav-subitems')

      // Giderler submenu should be expanded
      await expect(giderlerBtn).toHaveAttribute('aria-expanded', 'true')
      await expect(giderlerSubmenu).toBeVisible()

      // Kurye item should have active class
      const kuryeBtn = giderlerSubmenu.locator('.subitem:has-text("Kurye")')
      await expect(kuryeBtn).toHaveClass(/active/)
    })
  })

  // ==========================================
  // ACCESSIBILITY TESTS
  // ==========================================

  test.describe('Accessibility (A11y)', () => {
    test('Parent with subItems has aria-expanded attribute', async ({ authenticatedPage: page }) => {
      const operasyonItem = page.locator('.nav-item:has(.nav-button:has-text("Operasyon"))')
      const operasyonBtn = operasyonItem.locator('.nav-button').first()

      // Should have aria-expanded attribute
      const ariaExpanded = await operasyonBtn.getAttribute('aria-expanded')
      expect(ariaExpanded).toBeDefined()
      expect(['true', 'false']).toContain(ariaExpanded)
    })

    test('Active submenu item has aria-current="page"', async ({ authenticatedPage: page }) => {
      // Navigate to submenu item
      await page.goto(config.frontendUrl + '/operations/production')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Find active item within Operasyon submenu
      const operasyonItem = page.locator('.nav-item:has(.nav-button:has-text("Operasyon"))')
      const uretimBtn = operasyonItem.locator('.subitem:has-text("Üretim")')

      // Should have aria-current="page"
      await expect(uretimBtn).toHaveAttribute('aria-current', 'page')
    })

    test('Submenu items are focusable with keyboard', async ({ authenticatedPage: page }) => {
      // Find Operasyon and ensure expanded
      const operasyonItem = page.locator('.nav-item:has(.nav-button:has-text("Operasyon"))')
      const operasyonBtn = operasyonItem.locator('.nav-button').first()

      const expanded = await operasyonBtn.getAttribute('aria-expanded')
      if (expanded !== 'true') {
        await operasyonBtn.click()
      }

      // Tab to submenu item
      await page.keyboard.press('Tab')

      // Check that a submenu item received focus
      const focusedElement = page.locator(':focus')
      const classes = await focusedElement.getAttribute('class')

      // Should be a subitem or nav-button
      expect(classes).toMatch(/subitem|nav-button/)
    })
  })

  // ==========================================
  // ACTIVE STATE TESTS
  // ==========================================

  test.describe('Active State Indicators', () => {
    test('Submenu item shows active state when on that route', async ({ authenticatedPage: page }) => {
      await page.goto(config.frontendUrl + '/operations/production')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Find Operasyon nav-item
      const operasyonItem = page.locator('.nav-item:has(.nav-button:has-text("Operasyon"))')
      const operasyonSubmenu = operasyonItem.locator('.nav-subitems')

      // Üretim button should have active class
      const uretimBtn = operasyonSubmenu.locator('.subitem:has-text("Üretim")')
      await expect(uretimBtn).toHaveClass(/active/)

      // Other submenu items should NOT have active class
      const malAlimBtn = operasyonSubmenu.locator('.subitem:has-text("Mal Alım")')
      await expect(malAlimBtn).not.toHaveClass(/active/)
    })

    test('Parent nav item shows active state when child is active', async ({ authenticatedPage: page }) => {
      await page.goto(config.frontendUrl + '/operations/production')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Operasyon parent button should have active class
      const operasyonItem = page.locator('.nav-item:has(.nav-button:has-text("Operasyon"))')
      const operasyonBtn = operasyonItem.locator('.nav-button').first()
      await expect(operasyonBtn).toHaveClass(/active/)
    })

    test('Active state transfers when navigating between submenu items', async ({ authenticatedPage: page }) => {
      // Start at /operations/production
      await page.goto(config.frontendUrl + '/operations/production')
      await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

      // Find Operasyon nav-item
      const operasyonItem = page.locator('.nav-item:has(.nav-button:has-text("Operasyon"))')
      const operasyonSubmenu = operasyonItem.locator('.nav-subitems')

      // Verify Üretim is active
      const uretimBtn = operasyonSubmenu.locator('.subitem:has-text("Üretim")')
      await expect(uretimBtn).toHaveClass(/active/)

      // Click Mal Alım
      const malAlimBtn = operasyonSubmenu.locator('.subitem:has-text("Mal Alım")')
      await malAlimBtn.click()

      // Now Mal Alım should be active
      await expect(malAlimBtn).toHaveClass(/active/)

      // Üretim should NOT be active anymore
      await expect(uretimBtn).not.toHaveClass(/active/)
    })
  })

  // ==========================================
  // MOBILE RESPONSIVE TESTS
  // ==========================================

  test.describe('Mobile Responsive Behavior', () => {
    test.use({ viewport: { width: 375, height: 667 } }) // iPhone SE

    test('Submenu appears as dropdown on mobile', async ({ authenticatedPage: page }) => {
      // On mobile, sidebar is hidden - click hamburger menu to reveal
      // The hamburger button has class "lg:hidden" and contains ☰
      const hamburgerBtn = page.locator('header button:has-text("☰")').first()
      await expect(hamburgerBtn).toBeVisible({ timeout: 5000 })
      await hamburgerBtn.click()

      // Wait for sidebar to slide in (transform transition takes 200ms)
      await page.waitForTimeout(300)

      // Find Operasyon nav-item within the sidebar
      const operasyonItem = page.locator('aside .nav-item:has(.nav-button:has-text("Operasyon"))')
      const operasyonBtn = operasyonItem.locator('.nav-button').first()
      const operasyonSubmenu = operasyonItem.locator('.nav-subitems')

      // Wait for nav to be visible in sidebar
      await expect(operasyonBtn).toBeVisible({ timeout: 5000 })

      // Ensure expanded
      const expanded = await operasyonBtn.getAttribute('aria-expanded')
      if (expanded !== 'true') {
        await operasyonBtn.click()
      }

      // Submenu should be visible
      await expect(operasyonSubmenu).toBeVisible({ timeout: 3000 })

      // On mobile (< 640px per CSS), submenu should have dropdown styling (position: absolute)
      const position = await operasyonSubmenu.evaluate((el) => {
        return window.getComputedStyle(el).position
      })
      expect(position).toBe('absolute')
    })
  })
})
