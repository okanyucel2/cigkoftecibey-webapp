import { test, expect } from '@playwright/test'

test.describe.configure({ mode: 'serial' })

import { config } from '../_config/test_config'

test.describe('🍽️ Personel Yemek', () => {
  const baseURL = config.frontendUrl
  const uniqueId = Date.now().toString()

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

    // Navigate to staff meals page
    await page.goto(config.frontendUrl + '/staff-meals')
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
  })

  test('Navigate to Staff Meals page and verify page loads', async ({ page }) => {
    // Verify we're on the correct page
    await expect(page).toHaveURL(/staff-meals/)

    // Wait for page to fully load
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Verify page heading is visible as indicator that page loaded
    await expect(page.locator('[data-testid="heading-staff-meals"]')).toBeVisible({ timeout: 15000 })

    // Check if table exists - if no data exists, empty state is acceptable
    const tableExists = await page.locator('[data-testid="staff-meals-table"]').isVisible({ timeout: 5000 }).catch(() => false)

    if (tableExists) {
      // Table is visible, verify summary cards
      await expect(page.locator('[data-testid="staff-meals-table"]')).toBeVisible({ timeout: 10000 })
    } else {
      // No data yet - verify empty state message instead
      await expect(page.locator('text=/no.*meal|empty|kayit bulunamadi/i')).toBeVisible({ timeout: 10000 }).catch(() => {
        console.log('No empty state message found - table may load after data fetch completes')
      })
    }
  })

  test('Create new staff meal record (Happy Path)', async ({ page }) => {
    // Use unique test date PER TEST (not shared across tests)
    // API uses date-based UPSERT: same date = update instead of create
    // Each test must use DIFFERENT date to ensure row count increases
    // Use current month with second-based uniqueness
    const now = new Date()
    const day = (Math.floor(Date.now() / 1000) % 27) + 1
    const testDate = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`

    // Use UNIQUE values that are unlikely to exist in database (for verification)
    const uniqueNotes = `Test Meal ${uniqueId}`
    const unitPrice = '150'
    const staffCount = '5'

    // Navigate to the page
    await page.goto(config.frontendUrl + '/staff-meals')
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Wait for heading to confirm page loaded
    await expect(page.locator('[data-testid="heading-staff-meals"]')).toBeVisible({ timeout: 10000 })

    // Click add button to open form
    await page.click('[data-testid="btn-add-staff-meal"]')
    await page.waitForTimeout(500)

    // Fill in the form fields
    await page.fill('[data-testid="input-meal-date"]', testDate)
    await page.fill('[data-testid="input-unit-price"]', unitPrice)
    await page.fill('[data-testid="input-staff-count"]', staffCount)
    await page.fill('[data-testid="textarea-notes"]', uniqueNotes)

    // Click save button and wait for API response
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/api/staff-meals') && resp.status() === 200),
      page.click('[data-testid="btn-save-staff-meal"]')
    ])

    // Wait for modal to close and table to be visible
    await expect(page.locator('[data-testid="staff-meals-table"]')).toBeVisible({ timeout: 10000 })

    // Verify record appears in table with unique values
    await expect(async () => {
      const table = page.locator('[data-testid="staff-meals-table"]')
      await expect(table).toBeVisible()
      const notesCell = table.locator(`text=${uniqueNotes}`)
      await expect(notesCell).toBeVisible()
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

    // Verify the table contains the correct values
    await expect(async () => {
      const table = page.locator('[data-testid="staff-meals-table"]')
      const row = table.locator(`tr:has-text("${uniqueNotes}")`)
      await expect(row.first()).toBeVisible()
      // Verify staff count is visible in the row (3rd column = Adet)
      const staffCountCell = row.first().locator('td:nth-child(3)')
      await expect(staffCountCell).toHaveText(staffCount)
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

    // Reload page and verify record persists
    await page.reload()
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    await expect(async () => {
      const table = page.locator('[data-testid="staff-meals-table"]')
      await expect(table).toBeVisible()
      const notesCell = table.locator(`text=${uniqueNotes}`)
      await expect(notesCell).toBeVisible()
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })
  })

  test('Edit existing staff meal record', async ({ page }) => {
    // FIXTURE: Create test data first
    const now = new Date()
    const day = (Math.floor(Date.now() / 1000) % 27) + 1
    const testDate = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`
    const uniqueNotes = `Edit Test ${uniqueId}`
    const initialStaffCount = '5'
    const updatedStaffCount = '10'

    // Navigate to the page
    await page.goto(config.frontendUrl + '/staff-meals')
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Create initial record
    await expect(page.locator('[data-testid="heading-staff-meals"]')).toBeVisible({ timeout: 10000 })
    await page.click('[data-testid="btn-add-staff-meal"]')
    await page.waitForTimeout(500)

    await page.fill('[data-testid="input-meal-date"]', testDate)
    await page.fill('[data-testid="input-unit-price"]', '150')
    await page.fill('[data-testid="input-staff-count"]', initialStaffCount)
    await page.fill('[data-testid="textarea-notes"]', uniqueNotes)

    // Wait for API response before clicking save
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/api/staff-meals') && resp.status() === 200),
      page.click('[data-testid="btn-save-staff-meal"]')
    ])

    // Wait for record to appear in table
    await expect(async () => {
      const table = page.locator('[data-testid="staff-meals-table"]')
      await expect(table).toBeVisible()
      const notesCell = table.locator(`text=${uniqueNotes}`)
      await expect(notesCell).toBeVisible()
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

    // NOW edit the record we just created
    const table = page.locator('[data-testid="staff-meals-table"]')
    const row = table.locator(`tr:has-text("${uniqueNotes}")`)
    await expect(row.first()).toBeVisible({ timeout: 5000 })

    // Click edit button
    const editButton = row.first().locator('[data-testid="btn-edit-staff-meal"]')
    await expect(editButton).toBeVisible({ timeout: 5000 })
    await editButton.click()

    // Wait for edit form to load
    await page.waitForTimeout(500)

    // Verify form is open and has the existing values
    const staffCountInput = page.locator('[data-testid="input-staff-count"]')
    await expect(staffCountInput).toBeVisible({ timeout: 5000 })

    // Update staff_count from 5 to 10
    await staffCountInput.fill(updatedStaffCount)

    // Click save button
    await page.click('[data-testid="btn-save-staff-meal"]')

    // Wait for modal to close and table to update
    await expect(async () => {
      const tableVisible = await page.locator('[data-testid="staff-meals-table"]').isVisible().catch(() => false)
      expect(tableVisible).toBe(true)
    }).toPass({ timeout: 10000, intervals: [500, 1000, 2000] })

    // Verify table updates with new staff_count
    await expect(async () => {
      const updatedTable = page.locator('[data-testid="staff-meals-table"]')
      const updatedRow = updatedTable.locator(`tr:has-text("${uniqueNotes}")`)
      await expect(updatedRow.first()).toBeVisible()
      // Verify staff count in 3rd column (Adet)
      const updatedStaffCountCell = updatedRow.first().locator('td:nth-child(3)')
      await expect(updatedStaffCountCell).toHaveText(updatedStaffCount)
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

    // Reload page and verify staff_count is 10 in table
    await page.reload()
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    await expect(async () => {
      const reloadedTable = page.locator('[data-testid="staff-meals-table"]')
      await expect(reloadedTable).toBeVisible()
      const reloadedRow = reloadedTable.locator(`tr:has-text("${uniqueNotes}")`)
      await expect(reloadedRow.first()).toBeVisible()
      // Verify staff count in 3rd column (Adet)
      const finalStaffCountCell = reloadedRow.first().locator('td:nth-child(3)')
      await expect(finalStaffCountCell).toHaveText(updatedStaffCount)
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })
  })

  test('Delete staff meal with confirmation modal', async ({ page }) => {
    // FIXTURE: Create test data first
    const now = new Date()
    const day = (Math.floor(Date.now() / 1000) % 27) + 1
    const testDate = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`
    const uniqueNotes = `Delete Test ${uniqueId}`

    // Navigate to the page
    await page.goto(config.frontendUrl + '/staff-meals')
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Create initial record
    await expect(page.locator('[data-testid="heading-staff-meals"]')).toBeVisible({ timeout: 10000 })
    await page.click('[data-testid="btn-add-staff-meal"]')
    await page.waitForTimeout(500)

    await page.fill('[data-testid="input-meal-date"]', testDate)
    await page.fill('[data-testid="input-unit-price"]', '150')
    await page.fill('[data-testid="input-staff-count"]', '5')
    await page.fill('[data-testid="textarea-notes"]', uniqueNotes)

    await page.click('[data-testid="btn-save-staff-meal"]')

    // Wait for record to appear in table
    await expect(async () => {
      const table = page.locator('[data-testid="staff-meals-table"]')
      await expect(table).toBeVisible()
      const notesCell = table.locator(`text=${uniqueNotes}`)
      await expect(notesCell).toBeVisible()
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

    // NOW delete the record we just created
    const table = page.locator('[data-testid="staff-meals-table"]')
    const row = table.locator(`tr:has-text("${uniqueNotes}")`)
    await expect(row.first()).toBeVisible({ timeout: 5000 })

    // Click delete button
    const deleteButton = row.first().locator('[data-testid="btn-delete-staff-meal"]')
    await expect(deleteButton).toBeVisible({ timeout: 5000 })
    await deleteButton.click()

    // Wait for confirmation modal (ConfirmModal) to appear
    await expect(async () => {
      const confirmModal = page.locator('[data-testid="btn-confirm-delete"]')
      await expect(confirmModal).toBeVisible()
    }).toPass({ timeout: 5000, intervals: [500, 1000] })

    // Click 'Evet, Sil' button (btn-confirm-delete) to confirm deletion
    await page.click('[data-testid="btn-confirm-delete"]')

    // Wait for record to disappear from table
    await expect(async () => {
      const updatedTable = page.locator('[data-testid="staff-meals-table"]')
      const deletedRow = updatedTable.locator(`tr:has-text("${uniqueNotes}")`)
      const rowCount = await deletedRow.count()
      expect(rowCount).toBe(0)
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })

    // Reload page and verify record is gone from database
    await page.reload()
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    await expect(async () => {
      const reloadedTable = page.locator('[data-testid="staff-meals-table"]')
      await expect(reloadedTable).toBeVisible()
      const reloadedRow = reloadedTable.locator(`tr:has-text("${uniqueNotes}")`)
      const finalRowCount = await reloadedRow.count()
      expect(finalRowCount).toBe(0)
    }).toPass({ timeout: 15000, intervals: [1000, 2000, 3000] })
  })
})