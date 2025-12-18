
from fastapi.testclient import TestClient
from datetime import date

def test_sgk_lifecycle(client: TestClient):
    """
    Test the full lifecycle of an SGK/Payroll entry:
    1. Create Employee
    2. Create Payroll (SGK)
    3. Update Payroll
    4. Delete Payroll
    """
    
    # 1. Create Employee
    employee_data = {
        "name": "Test Personel",
        "base_salary": 20000.0,
        "has_sgk": True,
        "sgk_amount": 5000.0,
        "daily_rate": 0,
        "hourly_rate": 0,
        "payment_type": "monthly",
        "is_part_time": False
    }
    response = client.post("/api/personnel/employees", json=employee_data)
    assert response.status_code == 200
    employee = response.json()
    assert employee["name"] == "Test Personel"
    employee_id = employee["id"]

    # 2. Create Payroll (SGK Entry)
    payroll_data = {
        "employee_id": employee_id,
        "year": 2024,
        "month": 12,
        "payment_date": str(date.today()),
        "record_type": "salary",
        "base_salary": 20000.0,
        "sgk_amount": 5000.0,
        "bonus": 1000.0,
        "premium": 500.0,
        "notes": "Test Odeme"
    }
    response = client.post("/api/personnel/payroll", json=payroll_data)
    if response.status_code != 200:
        print(response.json())
        
    assert response.status_code == 200
    payroll = response.json()
    assert float(payroll["sgk_amount"]) == 5000.0
    assert float(payroll["premium"]) == 500.0
    
    payroll_id = payroll["id"]

    # 3. Read Payroll
    response = client.get(f"/api/personnel/payroll/{payroll_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["notes"] == "Test Odeme"

    # 4. Update Payroll (Edit)
    update_data = {
        "sgk_amount": 5500.0,
        "notes": "Guncellenmis Odeme"
    }
    response = client.put(f"/api/personnel/payroll/{payroll_id}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert float(updated["sgk_amount"]) == 5500.0
    assert updated["notes"] == "Guncellenmis Odeme"

    # 5. Delete Payroll
    response = client.delete(f"/api/personnel/payroll/{payroll_id}")
    assert response.status_code == 200
    
    # Verify Deletion
    response = client.get(f"/api/personnel/payroll/{payroll_id}")
    assert response.status_code == 404
