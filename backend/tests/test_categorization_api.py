"""Tests for Categorization API"""
import pytest


def test_suggest_category(client):
    """Should return category suggestions for expense"""
    response = client.post("/api/categorization/suggest", json={
        "description": "Elektrik faturası",
        "amount": 1500.0
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "category" in data[0]
    assert "confidence" in data[0]


def test_suggest_batch(client):
    """Should categorize multiple expenses"""
    response = client.post("/api/categorization/suggest-batch", json={
        "expenses": [
            {"description": "Elektrik", "amount": 1500},
            {"description": "Metro market", "amount": 2300}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
