# backend/tests/test_cash_difference_idempotency.py
"""
Test idempotency key support for cash difference import endpoint
"""
import pytest
from decimal import Decimal
from datetime import date
from app.models import CashDifference
from app.idempotency import get_idempotency_store


def test_import_with_idempotency_key_prevents_duplicate(client, db):
    """Same idempotency key should return cached response and prevent duplicate creation"""

    # Clear idempotency store before test
    get_idempotency_store()._store.clear()

    request_data = {
        "difference_date": "2024-01-15",
        "kasa_visa": 1000.0,
        "kasa_nakit": 500.0,
        "kasa_trendyol": 300.0,
        "kasa_getir": 200.0,
        "kasa_yemeksepeti": 150.0,
        "kasa_migros": 100.0,
        "kasa_total": 2250.0,
        "pos_visa": 1050.0,
        "pos_nakit": 500.0,
        "pos_trendyol": 300.0,
        "pos_getir": 200.0,
        "pos_yemeksepeti": 150.0,
        "pos_migros": 100.0,
        "pos_total": 2300.0
    }

    idempotency_key = "test-import-123"

    # First request with idempotency key
    response1 = client.post(
        "/api/cash-difference/import",
        json=request_data,
        headers={"X-Idempotency-Key": idempotency_key}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["id"] is not None
    assert data1["difference_date"] == "2024-01-15"
    assert data1["diff_total"] == "50.00"  # 2300 - 2250

    # Verify one record in database
    records = db.query(CashDifference).all()
    assert len(records) == 1

    # Second request with same idempotency key
    response2 = client.post(
        "/api/cash-difference/import",
        json=request_data,
        headers={"X-Idempotency-Key": idempotency_key}
    )

    assert response2.status_code == 200
    data2 = response2.json()

    # Should return the same response
    assert data2["id"] == data1["id"]
    assert data2["difference_date"] == data1["difference_date"]

    # Verify still only one record in database (no duplicate created)
    records = db.query(CashDifference).all()
    assert len(records) == 1


def test_import_without_idempotency_key_works_normally(client, db):
    """Request without idempotency key should work as before"""

    # Clear idempotency store before test
    get_idempotency_store()._store.clear()

    request_data = {
        "difference_date": "2024-01-16",
        "kasa_visa": 1000.0,
        "kasa_nakit": 500.0,
        "kasa_trendyol": 300.0,
        "kasa_getir": 200.0,
        "kasa_yemeksepeti": 150.0,
        "kasa_migros": 100.0,
        "kasa_total": 2250.0,
        "pos_visa": 1050.0,
        "pos_nakit": 500.0,
        "pos_trendyol": 300.0,
        "pos_getir": 200.0,
        "pos_yemeksepeti": 150.0,
        "pos_migros": 100.0,
        "pos_total": 2300.0
    }

    # Request without idempotency key header
    response = client.post(
        "/api/cash-difference/import",
        json=request_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["difference_date"] == "2024-01-16"

    # Verify record created
    records = db.query(CashDifference).all()
    assert len(records) == 1


def test_different_idempotency_keys_create_separate_records(client, db):
    """Different idempotency keys should create separate records"""

    # Clear idempotency store before test
    get_idempotency_store()._store.clear()

    request_data_1 = {
        "difference_date": "2024-01-17",
        "kasa_visa": 1000.0,
        "kasa_nakit": 500.0,
        "kasa_trendyol": 300.0,
        "kasa_getir": 200.0,
        "kasa_yemeksepeti": 150.0,
        "kasa_migros": 100.0,
        "kasa_total": 2250.0,
        "pos_visa": 1050.0,
        "pos_nakit": 500.0,
        "pos_trendyol": 300.0,
        "pos_getir": 200.0,
        "pos_yemeksepeti": 150.0,
        "pos_migros": 100.0,
        "pos_total": 2300.0
    }

    request_data_2 = {
        "difference_date": "2024-01-18",
        "kasa_visa": 2000.0,
        "kasa_nakit": 1000.0,
        "kasa_trendyol": 600.0,
        "kasa_getir": 400.0,
        "kasa_yemeksepeti": 300.0,
        "kasa_migros": 200.0,
        "kasa_total": 4500.0,
        "pos_visa": 2100.0,
        "pos_nakit": 1000.0,
        "pos_trendyol": 600.0,
        "pos_getir": 400.0,
        "pos_yemeksepeti": 300.0,
        "pos_migros": 200.0,
        "pos_total": 4600.0
    }

    # First request with key 1
    response1 = client.post(
        "/api/cash-difference/import",
        json=request_data_1,
        headers={"X-Idempotency-Key": "key-1"}
    )

    assert response1.status_code == 200

    # Second request with key 2
    response2 = client.post(
        "/api/cash-difference/import",
        json=request_data_2,
        headers={"X-Idempotency-Key": "key-2"}
    )

    assert response2.status_code == 200

    # Verify two separate records created
    records = db.query(CashDifference).all()
    assert len(records) == 2
    assert {r.difference_date for r in records} == {date(2024, 1, 17), date(2024, 1, 18)}
