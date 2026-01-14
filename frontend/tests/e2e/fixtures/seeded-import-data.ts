// seeded-import-data.ts
// Fixture that provides seeded import history data for E2E tests
// Extends mock-auth with specific import API mocking
//
// TASK-CI-01: Enable E2E Tests for Import Status

import { test as base, Page, expect } from '@playwright/test'
import { config } from '../_config/test_config'

// Mock user (same as mock-auth)
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

const MOCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.mock'

// Seeded import history data with various statuses
// Field names match ImportHub.vue expectations (source_filename, not file_name)
export const SEEDED_IMPORT_HISTORY = {
  pending: [
    {
      id: 1,
      import_type: 'kasa_raporu',
      status: 'pending',
      import_date: '2026-01-09T10:00:00Z',
      source_filename: 'rapor_pending.xlsx',
      branch_id: 1,
      created_by: 1
    }
  ],
  completed: [
    {
      id: 2,
      import_type: 'kasa_raporu',
      status: 'completed',
      import_date: '2026-01-08T15:30:00Z',
      source_filename: 'rapor_completed.xlsx',
      branch_id: 1,
      created_by: 1,
      completed_at: '2026-01-08T15:31:00Z',
      records_processed: 150
    }
  ],
  failed: [
    {
      id: 3,
      import_type: 'kasa_raporu',
      status: 'failed',
      import_date: '2026-01-07T09:00:00Z',
      source_filename: 'rapor_failed.xlsx',
      branch_id: 1,
      created_by: 1,
      error_message: 'Invalid file format'
    }
  ],
  mixed: [
    {
      id: 1,
      import_type: 'kasa_raporu',
      status: 'pending',
      import_date: '2026-01-09T10:00:00Z',
      source_filename: 'rapor_pending.xlsx',
      branch_id: 1,
      created_by: 1
    },
    {
      id: 2,
      import_type: 'kasa_raporu',
      status: 'completed',
      import_date: '2026-01-08T15:30:00Z',
      source_filename: 'rapor_completed.xlsx',
      branch_id: 1,
      created_by: 1,
      completed_at: '2026-01-08T15:31:00Z',
      records_processed: 150
    },
    {
      id: 3,
      import_type: 'kasa_raporu',
      status: 'failed',
      import_date: '2026-01-07T09:00:00Z',
      source_filename: 'rapor_failed.xlsx',
      branch_id: 1,
      created_by: 1,
      error_message: 'Invalid file format'
    }
  ],
  empty: []
}

// Scenario type for different test cases
export type ImportScenario = 'pending' | 'completed' | 'failed' | 'mixed' | 'empty'

// Extended fixture with scenario support
export const test = base.extend<{
  seededPage: Page
  scenario: ImportScenario
}>({
  // Default scenario
  scenario: ['mixed', { option: true }],

  seededPage: async ({ page, context, scenario }, use) => {
    // Set localStorage before any page loads
    await context.addInitScript((mockData) => {
      localStorage.setItem('token', mockData.token)
      localStorage.setItem('currentBranchId', '1')
    }, { token: MOCK_TOKEN })

    // Mock /api/auth/me
    await page.route('**/api/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_USER)
      })
    })

    // Mock /api/import-history with seeded data based on scenario
    // API returns array directly (not wrapped in {data: [...]})
    await page.route('**/api/import-history**', async (route) => {
      const importData = SEEDED_IMPORT_HISTORY[scenario] || SEEDED_IMPORT_HISTORY.mixed
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(importData)
      })
    })

    // Mock /api/import-history/:id/undo
    await page.route('**/api/import-history/*/undo', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, message: 'Import undone' })
      })
    })

    // Mock other API endpoints with generic response
    await page.route('**/api/**', async (route, request) => {
      const url = request.url()
      // Skip if already handled
      if (url.includes('/api/auth/me') || url.includes('/api/import-history')) {
        return route.fallback()
      }
      // Generic response
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

    // Navigate to dashboard
    await page.goto(config.frontendUrl + '/')
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    await use(page)
  }
})

export { expect }
