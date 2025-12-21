# E2E Test Suite Upgrade Design

**Date:** 2025-12-21
**Status:** Approved
**Approach:** Quality First → Quick Wins → Full Coverage

---

## 1. Genesis E2E Test Standard

All tests must include these 5 components:

### 1.1 API Login Bypass
```typescript
// Skip UI login - inject token directly
const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', {
  data: { email: config.auth.email, password: config.auth.password }
})
const token = (await loginRes.json()).access_token
await page.evaluate((t) => localStorage.setItem('token', t), token)
```

### 1.2 data-testid Selectors
- Format: `[data-testid="component-action-element"]`
- Examples: `btn-save-expense`, `input-email`, `table-users`
- NO CSS class or text selectors (fragile)

### 1.3 Test Fixtures
- Create test data at start of each test
- Use unique IDs to prevent collisions
- Never skip test if data missing - create it

### 1.4 Persistence Verification
```typescript
// After CRUD operation
await page.reload()
await page.waitForLoadState('networkidle')
// Verify data survives reload
await expect(page.locator('[data-testid="table"]')).toContainText(uniqueValue)
```

### 1.5 Unique Test Data
- Timestamp-based: `Test_${Date.now()}`
- File-specific prefixes (see table below)

---

## 2. Unique Test Data Prefixes

Prevents collision between test files:

| Prefix Range | Test File | Example Values |
|--------------|-----------|----------------|
| 100-199 | courier-expenses.spec.ts | 1011, 1022, 1033 |
| 200-299 | staff-meals.spec.ts | 2011, 2022, 2033 |
| 300-399 | suppliers.spec.ts | 3011, 3022, 3033 |
| 400-499 | settings.spec.ts | 4011, 4022, 4033 |
| 500-599 | sgk.spec.ts | 5011, 5022, 5033 |
| 600-699 | invitation-codes.spec.ts | 6011, 6022, 6033 |
| 700-799 | unified-sales.spec.ts | 7011, 7022, 7033 |
| 800-899 | login.spec.ts | 8011, 8022, 8033 |

**Suffix Convention:**
- `xx1` = Create tests
- `xx2` = Edit tests
- `xx3` = Delete tests

**Full Format:** `{prefix}{suffix}_${Date.now().toString().slice(-4)}`

---

## 3. Implementation Phases

### Phase 1: Quick Wins (3 files)

| Order | File | Current State | Work Needed |
|-------|------|---------------|-------------|
| 1.1 | login.spec.ts | Good structure | Add edge cases, fixtures |
| 1.2 | staff-meals.spec.ts | Good quality | Minor tweaks only |
| 1.3 | suppliers.spec.ts | Incomplete CRUD | Complete Edit + Delete |

### Phase 2: Medium Effort (3 files)

| Order | File | Current State | Work Needed |
|-------|------|---------------|-------------|
| 2.1 | invitation-codes.spec.ts | Basic flow | Full CRUD + edge cases |
| 2.2 | sgk.spec.ts | Single test | Full CRUD coverage |
| 2.3 | settings.spec.ts | Very incomplete | Full rewrite needed |

---

## 4. Deliverables Per File

Each upgraded test file will have:

### Tests
- [ ] Page Load verification
- [ ] Create (Happy Path)
- [ ] Edit (with fixture)
- [ ] Delete (with confirmation modal)
- [ ] Validation errors (where applicable)

### Vue Components
- [ ] data-testid attributes added (documented in test header)

### Smoke Test
- [ ] At least 1 test marked `@smoke` for pre-deploy checks

---

## 5. Progress Tracking

### Phase 1 Progress

| File | API Login | data-testid | Fixtures | Persistence | Unique Data | Smoke Tag |
|------|-----------|-------------|----------|-------------|-------------|-----------|
| login.spec.ts | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| staff-meals.spec.ts | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| suppliers.spec.ts | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### Phase 2 Progress

| File | API Login | data-testid | Fixtures | Persistence | Unique Data | Smoke Tag |
|------|-----------|-------------|----------|-------------|-------------|-----------|
| invitation-codes.spec.ts | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| sgk.spec.ts | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| settings.spec.ts | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

---

## 6. Reference: Best Example

`courier-expenses.spec.ts` is the gold standard. Key patterns to copy:

```typescript
test.describe.configure({ mode: 'serial' })

test.beforeEach(async ({ page, request }) => {
  // API Login Bypass
  const loginRes = await request.post(config.backendUrl + '/api/auth/login-json', { ... })
  const token = (await loginRes.json()).access_token
  await page.evaluate((t) => localStorage.setItem('token', t), token)

  // Navigate to page
  await page.goto(config.frontendUrl + '/target-page')
  await page.waitForLoadState('networkidle')
})

test('Create Happy Path', async ({ page }) => {
  // Unique test data
  const uniqueAmount = '2011'
  const uniqueNote = `Test_201_${Date.now().toString().slice(-4)}`

  // Create
  await page.click('[data-testid="btn-add"]')
  await page.fill('[data-testid="input-amount"]', uniqueAmount)
  await page.click('[data-testid="btn-save"]')

  // Wait for save
  await page.waitForResponse(r => r.url().includes('/api/') && r.request().method() === 'POST')

  // Persistence verification
  await page.reload()
  await expect(page.locator('[data-testid="table"]')).toContainText(uniqueAmount)
})
```

---

## 7. Notes

- **Ports:** cigkoftecibey-webapp runs on backend:8000, frontend:5174
- **Config:** All tests use `../\_config/test_config.ts` for URLs
- **Serial Mode:** CRUD tests should run in serial to avoid data conflicts
