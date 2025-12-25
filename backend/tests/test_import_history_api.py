"""Tests for ImportHistory API"""
import pytest


def test_get_import_history(client):
    """Should return import history for current branch"""
    response = client.get("/api/import-history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_import_history_by_type(client):
    """Should filter by import type"""
    response = client.get("/api/import-history?import_type=kasa_raporu")
    assert response.status_code == 200
