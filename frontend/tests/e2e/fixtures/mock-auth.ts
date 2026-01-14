// mock-auth.ts
// Mock authentication fixture for E2E tests (Docker not required)
// NOTE: This is for LOCAL DEV SPEED only - CI must verify against real backend

import { test as base, Page, expect } from '@playwright/test'
import { config } from '../_config/test_config'

// Mock user for testing (matches backend User schema)
const MOCK_USER = {
  id: 1,
  email: 'test@cigkoftecibey.com',
  name: 'Test User',
  role: 'admin',
  is_super_admin: true,
  current_branch_id: 1,
  accessible_branches: [
    { id: 1, name: 'Ana Şube', code: 'MAIN' }
  ]
}

// Mock JWT token (not real, just for frontend state)
const MOCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwibmFtZSI6IlRlc3QgVXNlciIsInJvbGUiOiJhZG1pbiJ9.mock'

export const test = base.extend<{ authenticatedPage: Page }>({
  authenticatedPage: async ({ page, context }, use) => {
    // Set localStorage BEFORE any page loads using addInitScript
    await context.addInitScript((mockData) => {
      localStorage.setItem('token', mockData.token)
      localStorage.setItem('currentBranchId', '1')
    }, { token: MOCK_TOKEN })

    // Intercept API calls BEFORE navigating
    // Mock /api/auth/me endpoint - this MUST return before router guard checks
    await page.route('**/api/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_USER)
      })
    })

    // Mock other API endpoints to prevent failures
    await page.route('**/api/**', async (route, request) => {
      const url = request.url()
      // Skip if already handled by specific route
      if (url.includes('/api/auth/me')) {
        return route.fallback()
      }
      // For other API calls, return empty data
      if (request.method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ data: [], total: 0 })
        })
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true })
        })
      }
    })

    // Navigate to dashboard - localStorage is already set, API is mocked
    await page.goto(config.frontendUrl + '/')

    // Wait for auth to be processed and navigation to render
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Verify we're not on login page (auth worked)
    const currentUrl = page.url()
    if (currentUrl.includes('/login')) {
      // Auth didn't work - try waiting for redirect
      await page.waitForURL('**/', { timeout: 5000 }).catch(() => {})
    }

    await use(page)
  }
})

export { expect }

// TODO: CI Pipeline must verify against real backend
// GitHub Actions should run with Docker/PostgreSQL
// This mock is for LOCAL DEV SPEED only
