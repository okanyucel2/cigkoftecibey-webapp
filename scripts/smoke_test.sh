#!/bin/bash
# Smoke Test for cigkoftecibey-webapp
# Usage: ./scripts/smoke_test.sh
#
# Prerequisites:
# - Docker running (cigkofte-db container)
# - Backend running on port 9049

BASE_URL="${BASE_URL:-http://localhost:9049/api}"

echo "=== CIGKOFTECIBEY-WEBAPP SMOKE TEST ==="
echo "Base URL: $BASE_URL"
echo ""

FAILED=0

# 1. Health check
echo -n "1. Health Check: "
HEALTH=$(curl -s $BASE_URL/health | jq -r '.status' 2>/dev/null)
if [ "$HEALTH" = "healthy" ]; then
  echo "✅ OK ($HEALTH)"
else
  echo "❌ FAILED ($HEALTH)"
  FAILED=1
fi

# 2. Login
echo -n "2. Login (admin@cigkofte.com): "
LOGIN_RESP=$(curl -s -X POST $BASE_URL/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@cigkofte.com", "password": "admin123"}')
TOKEN=$(echo "$LOGIN_RESP" | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
  echo "✅ OK (token received)"
else
  echo "❌ FAILED"
  echo "Response: $LOGIN_RESP"
  exit 1
fi

# 3. Get current user (/auth/me)
echo -n "3. Current User (/auth/me): "
ME_RESP=$(curl -s $BASE_URL/auth/me -H "Authorization: Bearer $TOKEN")
USER_EMAIL=$(echo "$ME_RESP" | jq -r '.email' 2>/dev/null)
if [ "$USER_EMAIL" = "admin@cigkofte.com" ]; then
  echo "✅ OK ($USER_EMAIL)"
else
  echo "❌ FAILED"
  FAILED=1
fi

# 4. Branches
echo -n "4. Branches: "
BRANCHES_RESP=$(curl -s $BASE_URL/branches -H "Authorization: Bearer $TOKEN")
BRANCH_COUNT=$(echo "$BRANCHES_RESP" | jq 'length' 2>/dev/null)
if [ "$BRANCH_COUNT" -gt 0 ] 2>/dev/null; then
  echo "✅ OK ($BRANCH_COUNT branches)"
else
  echo "⚠️ Warning - No branches or error"
fi

# 5. Organizations
echo -n "5. Organizations: "
ORG_RESP=$(curl -s $BASE_URL/organizations -H "Authorization: Bearer $TOKEN")
ORG_COUNT=$(echo "$ORG_RESP" | jq 'length' 2>/dev/null)
if [ "$ORG_COUNT" -gt 0 ] 2>/dev/null; then
  echo "✅ OK ($ORG_COUNT organizations)"
else
  echo "⚠️ Warning - No organizations or error"
fi

# 6. Cash Difference
echo -n "6. Cash Difference: "
CD_RESP=$(curl -s "$BASE_URL/cash-difference?month=1&year=2026" -H "Authorization: Bearer $TOKEN")
CD_STATUS=$(echo "$CD_RESP" | jq -r 'if type=="array" then "array" else .detail // "error" end' 2>/dev/null)
if [ "$CD_STATUS" = "array" ]; then
  CD_COUNT=$(echo "$CD_RESP" | jq 'length')
  echo "✅ OK ($CD_COUNT records)"
else
  echo "❌ FAILED ($CD_STATUS)"
  FAILED=1
fi

# 7. Expenses
echo -n "7. Expenses: "
EXP_RESP=$(curl -s "$BASE_URL/expenses" -H "Authorization: Bearer $TOKEN")
EXP_STATUS=$(echo "$EXP_RESP" | jq -r 'if type=="array" then "array" else .detail // "error" end' 2>/dev/null)
if [ "$EXP_STATUS" = "array" ]; then
  echo "✅ OK"
else
  echo "❌ FAILED ($EXP_STATUS)"
  FAILED=1
fi

# 8. Purchases
echo -n "8. Purchases: "
PURCH_RESP=$(curl -s "$BASE_URL/purchases" -H "Authorization: Bearer $TOKEN")
PURCH_STATUS=$(echo "$PURCH_RESP" | jq -r 'if type=="array" then "array" else .detail // "error" end' 2>/dev/null)
if [ "$PURCH_STATUS" = "array" ]; then
  echo "✅ OK"
else
  echo "❌ FAILED ($PURCH_STATUS)"
  FAILED=1
fi

# 9. Online Sales
echo -n "9. Online Sales: "
OS_RESP=$(curl -s "$BASE_URL/online-sales" -H "Authorization: Bearer $TOKEN")
OS_STATUS=$(echo "$OS_RESP" | jq -r 'if type=="array" then "array" else .detail // "error" end' 2>/dev/null)
if [ "$OS_STATUS" = "array" ]; then
  echo "✅ OK"
else
  echo "❌ FAILED ($OS_STATUS)"
  FAILED=1
fi

# 10. Employees
echo -n "10. Employees: "
EMP_RESP=$(curl -s "$BASE_URL/personnel/employees" -H "Authorization: Bearer $TOKEN")
EMP_STATUS=$(echo "$EMP_RESP" | jq -r 'if type=="array" then "array" else .detail // "error" end' 2>/dev/null)
if [ "$EMP_STATUS" = "array" ]; then
  echo "✅ OK"
else
  echo "❌ FAILED ($EMP_STATUS)"
  FAILED=1
fi

echo ""
echo "=== SMOKE TEST COMPLETE ==="

if [ $FAILED -eq 1 ]; then
  echo "⚠️ Some tests failed!"
  exit 1
else
  echo "✅ All tests passed!"
  exit 0
fi
