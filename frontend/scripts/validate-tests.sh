#!/bin/bash
# Genesis Test Validation Script
# Validates test files before commit to prevent common issues

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

echo "🔍 Genesis Test Validator"
echo "========================="

# Get test files (from args or staged files)
if [ "$#" -gt 0 ]; then
    FILES="$@"
else
    FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.spec\.ts$' || true)
fi

if [ -z "$FILES" ]; then
    echo "No test files to validate."
    exit 0
fi

for FILE in $FILES; do
    if [ ! -f "$FILE" ]; then
        continue
    fi

    echo ""
    echo "📄 Checking: $FILE"

    # Check 1: File completeness (not truncated)
    LAST_LINE=$(tail -1 "$FILE" | tr -d '[:space:]')
    if [[ "$LAST_LINE" != *"})" ]] && [[ "$LAST_LINE" != *"});" ]]; then
        echo -e "${RED}  ❌ TRUNCATED: File does not end with '})' or '});' (found: $LAST_LINE)${NC}"
        ERRORS=$((ERRORS + 1))
    fi

    # Check 2: Balanced braces
    OPEN_BRACES=$(grep -o '{' "$FILE" | wc -l | tr -d ' ')
    CLOSE_BRACES=$(grep -o '}' "$FILE" | wc -l | tr -d ' ')
    if [ "$OPEN_BRACES" -ne "$CLOSE_BRACES" ]; then
        echo -e "${RED}  ❌ UNBALANCED: $OPEN_BRACES '{' vs $CLOSE_BRACES '}'${NC}"
        ERRORS=$((ERRORS + 1))
    fi

    # Check 3: Has at least one test
    if ! grep -q 'test(' "$FILE" && ! grep -q 'it(' "$FILE"; then
        echo -e "${RED}  ❌ NO TESTS: No test() or it() blocks found${NC}"
        ERRORS=$((ERRORS + 1))
    fi

    # Check 4: Forbidden selectors
    if grep -qE "input\[type=['\"]email" "$FILE"; then
        echo -e "${RED}  ❌ FRAGILE SELECTOR: input[type='email'] - use data-testid${NC}"
        ERRORS=$((ERRORS + 1))
    fi

    if grep -qE "button\[type=['\"]submit" "$FILE"; then
        echo -e "${RED}  ❌ FRAGILE SELECTOR: button[type='submit'] - use data-testid${NC}"
        ERRORS=$((ERRORS + 1))
    fi

    if grep -qE "has-text\(['\"]" "$FILE"; then
        echo -e "${YELLOW}  ⚠️  WARNING: has-text() selector found - prefer data-testid${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi

    # Check 5: Naming convention (kebab-case)
    BASENAME=$(basename "$FILE")
    if echo "$BASENAME" | grep -qE '_'; then
        echo -e "${YELLOW}  ⚠️  WARNING: Underscore in filename - use kebab-case (hyphens)${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi

    # Check 6: Empty state after single delete (anti-pattern)
    if grep -qE "delete.*empty.*visible|sil.*empty.*visible" "$FILE"; then
        echo -e "${YELLOW}  ⚠️  WARNING: Expecting empty state after delete - other records may exist${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi

    # Check 7: Missing waitForResponse after form submit
    if grep -qE "click.*btn-save|click.*submit" "$FILE" | head -1; then
        if ! grep -qE "waitForResponse" "$FILE"; then
            echo -e "${YELLOW}  ⚠️  WARNING: Missing waitForResponse - add Promise.all pattern after form submit${NC}"
            WARNINGS=$((WARNINGS + 1))
        fi
    fi

    echo -e "${GREEN}  ✓ Validation complete${NC}"
done

echo ""
echo "========================="
echo "Summary: $ERRORS errors, $WARNINGS warnings"

if [ "$ERRORS" -gt 0 ]; then
    echo -e "${RED}❌ Validation FAILED - fix errors before committing${NC}"
    exit 1
fi

if [ "$WARNINGS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Validation passed with warnings${NC}"
fi

echo -e "${GREEN}✅ All tests validated successfully${NC}"
exit 0
