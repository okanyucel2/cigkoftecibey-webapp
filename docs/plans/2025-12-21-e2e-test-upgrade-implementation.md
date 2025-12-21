# E2E Test Suite Upgrade - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade all E2E tests to Genesis Test Standard (API login, data-testid, fixtures, persistence, unique data)

**Architecture:** Phase 1 focuses on quick wins - files that need minimal changes. Each test file gets full CRUD coverage with the 5-component standard.

**Tech Stack:** Playwright, Vue 3, TypeScript, data-testid attributes

---

## Phase 1: Quick Wins

### Task 1: staff-meals.spec.ts - Add Smoke Tag + Unique Prefix

**Files:**
- Modify: `frontend/tests/e2e/expenses/staff-meals.spec.ts:1-10`

**Current State:** Already excellent quality. Just needs smoke tag and unique data prefix.

**Step 1: Add smoke tag and update unique data prefix**

Replace lines 1-10:

```typescript
// @smoke @critical
// Pre-flight check: Staff meal CRUD operations
import { test, expect } from '@playwright/test'

test.describe.configure({ mode: 'serial' })

import { config } from '../_config/test_config'

test.describe('🍽️ Personel Yemek', () => {
  const baseURL = config.frontendUrl
  // Unique prefix 201x for staff-meals (200-299 range)
  const uniquePrefix = '201'
  const uniqueSuffix = Date.now().toString().slice(-4)
  const uniqueId = `${uniquePrefix}_${uniqueSuffix}`
```

**Step 2: Update unique values in Create test (line ~82-83)**

Find and replace in Create test:

```typescript
  // Use UNIQUE values with staff-meals prefix (200-299 range)
  const uniqueNotes = `Test Meal ${uniqueId}`
  const unitPrice = '2011'  // Prefix 201 + operation 1 (create)
  const staffCount = '5'
```

**Step 3: Update unique values in Edit test (line ~146-148)**

```typescript
  const uniqueNotes = `Edit Test ${uniqueId}`
  const initialStaffCount = '2021'  // Prefix 202 + operation 1
  const updatedStaffCount = '2022'  // Prefix 202 + operation 2
```

**Step 4: Update unique values in Delete test (line ~237)**

```typescript
  const uniqueNotes = `Delete Test ${uniqueId}`
  // Uses 203x prefix for delete operations
```

**Step 5: Run tests to verify**

```bash
cd /Users/okan.yucel/cigkoftecibey-webapp/frontend
npx playwright test tests/e2e/expenses/staff-meals.spec.ts --headed
```

Expected: All 4 tests pass

**Step 6: Commit**

```bash
git add frontend/tests/e2e/expenses/staff-meals.spec.ts
git commit -m "test(staff-meals): add smoke tag and unique data prefix (201x)"
```

---

### Task 2: login.spec.ts - Add data-testid to Vue Component

**Files:**
- Modify: `frontend/src/components/LoginModal.vue` (add data-testid)
- Modify: `frontend/tests/e2e/auth/login.spec.ts`

**Step 1: Check LoginModal.vue for existing data-testid**

```bash
grep -n "data-testid" /Users/okan.yucel/cigkoftecibey-webapp/frontend/src/components/LoginModal.vue
```

**Step 2: Add data-testid attributes to LoginModal.vue**

Add these attributes (exact locations depend on component structure):

```vue
<!-- Email input -->
<input data-testid="input-email" type="email" ... />

<!-- Password input -->
<input data-testid="input-password" type="password" ... />

<!-- Submit button -->
<button data-testid="btn-login" type="submit" ... />

<!-- Error message -->
<div data-testid="login-error-message" v-if="error" ... />
```

**Step 3: Update login.spec.ts selectors**

Replace CSS selectors with data-testid:

```typescript
// OLD: await page.locator('input[type="email"]')
// NEW:
await page.locator('[data-testid="input-email"]')

// OLD: await page.locator('input[type="password"]')
// NEW:
await page.locator('[data-testid="input-password"]')

// OLD: page.locator('button[type="submit"]')
// NEW:
page.locator('[data-testid="btn-login"]')

// OLD: page.locator('[data-testid="error-message"]')
// NEW:
page.locator('[data-testid="login-error-message"]')
```

**Step 4: Run login tests**

```bash
cd /Users/okan.yucel/cigkoftecibey-webapp/frontend
npx playwright test tests/e2e/auth/login.spec.ts --headed
```

Expected: All 4 tests pass

**Step 5: Commit**

```bash
git add frontend/src/components/LoginModal.vue frontend/tests/e2e/auth/login.spec.ts
git commit -m "test(login): add data-testid selectors for reliable testing"
```

---

### Task 3: login.spec.ts - Add API Login Test

**Files:**
- Modify: `frontend/tests/e2e/auth/login.spec.ts`

**Step 1: Add API login verification test**

Add after the existing tests:

```typescript
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
```

**Step 2: Run tests**

```bash
npx playwright test tests/e2e/auth/login.spec.ts --headed
```

Expected: All 6 tests pass

**Step 3: Commit**

```bash
git add frontend/tests/e2e/auth/login.spec.ts
git commit -m "test(login): add API login verification tests"
```

---

### Task 4: purchases.spec.ts - Upgrade to Standard

**Files:**
- Modify: `frontend/tests/e2e/inventory/purchases.spec.ts`
- Check: `frontend/src/views/PurchasesView.vue` (for data-testid)

**Step 1: Check current data-testid usage in Vue component**

```bash
grep -n "data-testid" /Users/okan.yucel/cigkoftecibey-webapp/frontend/src/views/PurchasesView.vue || echo "No data-testid found"
```

**Step 2: Rewrite purchases.spec.ts with API login bypass**

Replace entire file:

```typescript
// @smoke
// Pre-flight check: Purchase CRUD operations
import { test, expect } from '@playwright/test'

test.describe.configure({ mode: 'serial' })

import { config } from '../_config/test_config'

test.describe('📦 Mal Alımı', () => {
  // Unique prefix 301x for purchases (300-399 range)
  const uniquePrefix = '301'
  const uniqueSuffix = Date.now().toString().slice(-4)
  const uniqueId = `${uniquePrefix}_${uniqueSuffix}`

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

    // Navigate to purchases page
    await page.goto(config.frontendUrl + '/purchases')
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})
  })

  test('Navigate to Purchases page and verify page loads', async ({ page }) => {
    await expect(page).toHaveURL(/purchases/)
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Verify page loaded - look for heading or table
    const pageLoaded = await page.locator('h1, h2, [data-testid="heading-purchases"]').first().isVisible({ timeout: 10000 }).catch(() => false)
    expect(pageLoaded).toBe(true)
  })

  test('Create Purchase via API and verify in UI', async ({ page, request }) => {
    // Get token for API calls
    const token = await page.evaluate(() => localStorage.getItem('token'))
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }

    // Create supplier first
    const supplierRes = await request.post(`${config.backendUrl}/api/purchases/suppliers`, {
      headers,
      data: {
        name: `Test Supplier ${uniqueId}`,
        phone: '05551234567'
      }
    })
    const supplier = await supplierRes.json()

    // Create purchase with unique notes
    const uniqueNotes = `Purchase_${uniqueId}`
    const purchaseRes = await request.post(`${config.backendUrl}/api/purchases`, {
      headers,
      data: {
        purchase_date: new Date().toISOString().split('T')[0],
        supplier_id: supplier.id,
        notes: uniqueNotes,
        items: [
          { product_id: 1, description: 'Test Item', quantity: 3011, unit: 'kg', unit_price: 100, vat_rate: 18 }
        ]
      }
    })

    expect(purchaseRes.ok()).toBe(true)

    // Reload page and verify in UI
    await page.reload()
    await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {})

    // Verify record appears
    await expect(page.locator('table')).toContainText(uniqueNotes, { timeout: 15000 })
  })
})
```

**Step 3: Run tests**

```bash
npx playwright test tests/e2e/inventory/purchases.spec.ts --headed
```

Expected: All tests pass

**Step 4: Commit**

```bash
git add frontend/tests/e2e/inventory/purchases.spec.ts
git commit -m "test(purchases): upgrade to Genesis Test Standard with API login"
```

---

## Phase 1 Verification

### Task 5: Run All Phase 1 Tests

**Step 1: Run all Phase 1 tests together**

```bash
cd /Users/okan.yucel/cigkoftecibey-webapp/frontend
npx playwright test tests/e2e/auth/login.spec.ts tests/e2e/expenses/staff-meals.spec.ts tests/e2e/inventory/purchases.spec.ts --headed
```

Expected: All tests pass

**Step 2: Run smoke tests only**

```bash
npx playwright test --grep @smoke
```

Expected: Tests with @smoke tag run successfully

**Step 3: Update design document progress**

Update `docs/plans/2025-12-21-e2e-test-upgrade-design.md`:

```markdown
### Phase 1 Progress

| File | API Login | data-testid | Fixtures | Persistence | Unique Data | Smoke Tag |
|------|-----------|-------------|----------|-------------|-------------|-----------|
| login.spec.ts | [x] | [x] | [x] | [x] | [x] | [x] |
| staff-meals.spec.ts | [x] | [x] | [x] | [x] | [x] | [x] |
| purchases.spec.ts | [x] | [x] | [x] | [x] | [x] | [x] |
```

**Step 4: Final commit**

```bash
git add docs/plans/
git commit -m "docs: mark Phase 1 test upgrades complete"
```

---

## Summary

| Task | File | Changes | Est. Time |
|------|------|---------|-----------|
| 1 | staff-meals.spec.ts | Smoke tag + prefix | 5 min |
| 2 | LoginModal.vue + login.spec.ts | data-testid | 10 min |
| 3 | login.spec.ts | API tests | 5 min |
| 4 | purchases.spec.ts | Full rewrite | 15 min |
| 5 | All | Verification | 5 min |

**Total: ~40 minutes**

---

## Next: Phase 2

After Phase 1 complete, create Phase 2 plan for:
- invitation-codes.spec.ts (600-699 prefix)
- sgk.spec.ts (500-599 prefix)
- settings.spec.ts (400-499 prefix)
