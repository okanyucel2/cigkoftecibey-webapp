"""Tests for AI expense categorization"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.categorization import ExpenseCategorizer, CategorySuggestion


def test_categorize_returns_suggestions():
    """Should return category suggestions for expense description"""
    categorizer = ExpenseCategorizer()

    # Mock the AI call
    with patch.object(categorizer, '_call_ai') as mock_ai:
        mock_ai.return_value = [
            CategorySuggestion(category="Utilities", category_id=None, confidence=0.95),
            CategorySuggestion(category="Operations", category_id=None, confidence=0.3)
        ]

        result = categorizer.categorize("Elektrik faturası Aralık")

        assert len(result) >= 1
        assert result[0].category == "Utilities"
        assert result[0].confidence >= 0.9


def test_categorize_uses_pattern_matching():
    """Should use pattern matching for common expenses"""
    categorizer = ExpenseCategorizer()

    # These should match patterns without calling AI
    result = categorizer.categorize("Elektrik faturası")
    assert result[0].category == "Utilities"
    assert "pattern" in result[0].reasoning.lower()

    result = categorizer.categorize("Metro market alışveriş")
    assert result[0].category == "Supplies"


def test_categorize_batch():
    """Should categorize multiple expenses at once"""
    categorizer = ExpenseCategorizer()

    with patch.object(categorizer, '_call_ai_batch') as mock_ai:
        mock_ai.return_value = [
            {"index": 0, "description": "Custom expense", "suggested_category": "Other", "confidence": 0.6}
        ]

        expenses = [
            {"description": "Elektrik faturası", "amount": 1500},  # Pattern match
            {"description": "Custom expense", "amount": 500}  # Needs AI
        ]

        result = categorizer.categorize_batch(expenses)

        assert len(result) == 2
        # First should be pattern-matched
        assert result[0]["suggested_category"] == "Utilities"
