# Testing Guide - Cigkoftecibey Webapp

## Test Environment

### Unit Tests (pytest)
Unit tests use in-memory SQLite and mock authentication.

```bash
# Run all tests
PYTHONPATH=. pytest

# Run specific test file
PYTHONPATH=. pytest tests/test_dashboard_comparison.py -v

# Run with coverage
PYTHONPATH=. pytest --cov=app tests/
```

### Test Fixtures (conftest.py)
Tests use the following pre-configured fixtures:

| Fixture | Description |
|---------|-------------|
| `db` | In-memory SQLite session with pre-populated User/Branch |
| `client` | FastAPI TestClient with mocked auth |

### Mock User (Unit Tests)
```python
User(
    id=1,
    email="test@example.com",
    is_super_admin=True,
    name="Test User"
)
```

### Mock Branch (Unit Tests)
```python
Branch(
    id=1,
    name="Test Branch",
    code="TEST",
    city="Istanbul",
    is_active=True
)
```

## Integration Testing (Manual / E2E)

### Development Database
For manual API testing, you need valid credentials in the development database.

**Option 1: Create Test User via API**
```bash
# Register new user (requires invitation code)
curl -X POST http://localhost:9049/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test123", "name": "Test", "invitation_code": "XXX"}'
```

**Option 2: Direct Database Insert**
```bash
# Connect to database
sqlite3 cigkofte.db

# Insert test user (password: test123)
INSERT INTO users (email, password_hash, name, is_active, is_super_admin)
VALUES ('test@dev.local', '$2b$12$...hashed...', 'Dev Test', 1, 1);
```

### Getting Auth Token
```bash
# Login to get JWT token
TOKEN=$(curl -s -X POST http://localhost:9049/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=YOUR_EMAIL&password=YOUR_PASSWORD" | jq -r '.access_token')

# Use token in requests
curl -H "Authorization: Bearer $TOKEN" http://localhost:9049/api/reports/dashboard
```

## Test Data Setup

### Sales Data
All sales are stored in `online_sales` table with different channel types:
- `pos_visa` - Salon/Card sales
- `pos_nakit` - Cash sales
- `online` - Online platform sales (Trendyol, Getir, etc.)

### Expense Data
Expenses are distributed across multiple tables:
- `purchases` - Supplier purchases
- `expenses` - General expenses
- `courier_expenses` - Delivery costs (with VAT)
- `part_time_costs` - Part-time labor
- `staff_meals` - Staff meal costs

## Troubleshooting

### "Email veya sifre hatali" Error
- Check if user exists in database
- Verify password hash is correct
- Check if user's `is_active=True`

### Auth Token Issues
- Tokens expire after configured time
- Check `JWT_SECRET_KEY` in `.env`
- Verify token format: `Bearer <token>`

### Database Connection Issues
- Check `DATABASE_URL` in `.env`
- Ensure database file exists
- Run migrations: `alembic upgrade head`
