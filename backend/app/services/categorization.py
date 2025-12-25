"""
AI-Powered Expense Categorization Service

Uses Claude API to categorize expenses based on description.
Uses pattern matching for common Turkish restaurant expenses.
"""
from dataclasses import dataclass
from decimal import Decimal
import os


@dataclass
class CategorySuggestion:
    """A suggested category with confidence score"""
    category: str
    category_id: int | None
    confidence: float
    reasoning: str | None = None


class ExpenseCategorizer:
    """
    AI-powered expense categorization.

    Uses pattern matching first for common expenses,
    falls back to Claude API for unknown descriptions.
    """

    # Common patterns for fast categorization (no API call needed)
    KNOWN_PATTERNS = {
        "elektrik": ("Utilities", "Elektrik faturası"),
        "su fatura": ("Utilities", "Su faturası"),
        "doğalgaz": ("Utilities", "Doğalgaz faturası"),
        "internet": ("Utilities", "İnternet faturası"),
        "kira": ("Rent", "Kira ödemesi"),
        "avans": ("Personnel", "Personel avansı"),
        "maaş": ("Personnel", "Maaş ödemesi"),
        "sgk": ("Personnel", "SGK ödemesi"),
        "market": ("Supplies", "Market alışverişi"),
        "metro": ("Supplies", "Metro market"),
        "bim": ("Supplies", "BİM market"),
        "a101": ("Supplies", "A101 market"),
        "temizlik": ("Cleaning", "Temizlik malzemesi"),
        "kurye": ("Delivery", "Kurye ödemesi"),
        "getir": ("Delivery", "Getir komisyonu"),
        "trendyol": ("Delivery", "Trendyol komisyonu"),
    }

    def __init__(self):
        self._api_key = os.getenv("ANTHROPIC_API_KEY")

    def categorize(
        self,
        description: str,
        amount: Decimal | None = None,
        available_categories: list[dict] | None = None
    ) -> list[CategorySuggestion]:
        """
        Categorize a single expense description.

        Returns list of suggestions sorted by confidence.
        """
        # Check known patterns first (fast path)
        desc_lower = description.lower()
        for pattern, (category, _) in self.KNOWN_PATTERNS.items():
            if pattern in desc_lower:
                return [CategorySuggestion(
                    category=category,
                    category_id=None,  # Caller maps to actual ID
                    confidence=0.95,
                    reasoning=f"Matched known pattern: {pattern}"
                )]

        # Fall back to AI categorization
        return self._call_ai(description, amount, available_categories)

    def categorize_batch(
        self,
        expenses: list[dict],
        available_categories: list[dict] | None = None
    ) -> list[dict]:
        """
        Categorize multiple expenses in one API call.

        Each expense should have 'description' and optionally 'amount'.
        Returns list with added 'suggested_category' and 'confidence'.
        """
        if not expenses:
            return []

        # First, check known patterns
        results = []
        needs_ai = []

        for i, exp in enumerate(expenses):
            desc_lower = exp.get("description", "").lower()
            matched = False

            for pattern, (category, _) in self.KNOWN_PATTERNS.items():
                if pattern in desc_lower:
                    results.append({
                        **exp,
                        "index": i,
                        "suggested_category": category,
                        "confidence": 0.95,
                        "reasoning": f"Pattern: {pattern}"
                    })
                    matched = True
                    break

            if not matched:
                needs_ai.append({"index": i, **exp})

        # Call AI for remaining
        if needs_ai:
            ai_results = self._call_ai_batch(needs_ai, available_categories)
            results.extend(ai_results)

        # Sort by original index
        results.sort(key=lambda x: x.get("index", 0))
        return results

    def _call_ai(
        self,
        description: str,
        amount: Decimal | None,
        available_categories: list[dict] | None
    ) -> list[CategorySuggestion]:
        """Call Claude API for categorization"""
        if not self._api_key:
            # No API key - return fallback
            return [CategorySuggestion(
                category="Other",
                category_id=None,
                confidence=0.5,
                reasoning="No API key configured"
            )]

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self._api_key)

            categories_str = """
- Utilities (elektrik, su, doğalgaz, internet)
- Rent (kira)
- Personnel (maaş, avans, SGK)
- Supplies (market, malzeme)
- Cleaning (temizlik)
- Delivery (kurye, komisyon)
- Maintenance (tamirat, bakım)
- Marketing (reklam)
- Other (diğer)
"""
            if available_categories:
                categories_str = "\n".join([f"- {c['name']}" for c in available_categories])

            prompt = f"""Kategorize this Turkish restaurant expense:

Description: {description}
Amount: {amount if amount else 'Not specified'} TL

Available categories:
{categories_str}

Return JSON array with top 2 suggestions:
[{{"category": "CategoryName", "confidence": 0.0-1.0, "reasoning": "brief reason"}}]

Only return the JSON, no other text."""

            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            result = json.loads(response.content[0].text)

            return [
                CategorySuggestion(
                    category=r["category"],
                    category_id=None,
                    confidence=r["confidence"],
                    reasoning=r.get("reasoning")
                )
                for r in result
            ]
        except Exception as e:
            # Fallback to "Other" on any error
            return [CategorySuggestion(
                category="Other",
                category_id=None,
                confidence=0.5,
                reasoning=f"AI error: {str(e)}"
            )]

    def _call_ai_batch(
        self,
        expenses: list[dict],
        available_categories: list[dict] | None
    ) -> list[dict]:
        """Call Claude API for batch categorization"""
        if not expenses:
            return []

        if not self._api_key:
            # No API key - return all as Other
            return [
                {**e, "suggested_category": "Other", "confidence": 0.5}
                for e in expenses
            ]

        try:
            import anthropic
            import json

            client = anthropic.Anthropic(api_key=self._api_key)

            expenses_str = "\n".join([
                f"{i+1}. {e['description']} - {e.get('amount', 'N/A')} TL"
                for i, e in enumerate(expenses)
            ])

            prompt = f"""Kategorize these Turkish restaurant expenses:

{expenses_str}

Return JSON array:
[{{"index": 0, "category": "CategoryName", "confidence": 0.0-1.0}}]

Categories: Utilities, Rent, Personnel, Supplies, Cleaning, Delivery, Maintenance, Marketing, Other

Only return the JSON."""

            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            result = json.loads(response.content[0].text)

            # Merge with original expenses
            return [
                {
                    **expenses[r["index"]],
                    "suggested_category": r["category"],
                    "confidence": r["confidence"]
                }
                for r in result
                if r["index"] < len(expenses)
            ]
        except Exception:
            # Return all as "Other" on error
            return [
                {**e, "suggested_category": "Other", "confidence": 0.5}
                for e in expenses
            ]


# Singleton instance
_categorizer = None


def get_categorizer() -> ExpenseCategorizer:
    """Get the global categorizer instance"""
    global _categorizer
    if _categorizer is None:
        _categorizer = ExpenseCategorizer()
    return _categorizer
