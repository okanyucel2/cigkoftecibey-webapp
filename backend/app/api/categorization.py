"""
Expense Categorization API
"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.api.deps import DBSession, CurrentBranchContext
from app.services.categorization import get_categorizer
from app.models import ExpenseCategory

router = APIRouter(prefix="/categorization", tags=["categorization"])


class ExpenseInput(BaseModel):
    description: str
    amount: float | None = None


class CategorySuggestionResponse(BaseModel):
    category: str
    category_id: int | None
    confidence: float
    reasoning: str | None = None


class BatchExpenseInput(BaseModel):
    expenses: list[ExpenseInput]


@router.post("/suggest", response_model=list[CategorySuggestionResponse])
def suggest_category(
    expense: ExpenseInput,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Get category suggestions for a single expense"""
    # Get available categories for this branch
    categories = db.query(ExpenseCategory).filter(
        (ExpenseCategory.branch_id == None) |
        (ExpenseCategory.branch_id == ctx.current_branch_id)
    ).all()

    available = [{"id": c.id, "name": c.name} for c in categories]

    categorizer = get_categorizer()
    suggestions = categorizer.categorize(
        expense.description,
        expense.amount,
        available
    )

    # Map category names to IDs
    category_map = {c.name.lower(): c.id for c in categories}

    return [
        CategorySuggestionResponse(
            category=s.category,
            category_id=category_map.get(s.category.lower()),
            confidence=s.confidence,
            reasoning=s.reasoning
        )
        for s in suggestions
    ]


@router.post("/suggest-batch")
def suggest_categories_batch(
    batch: BatchExpenseInput,
    db: DBSession,
    ctx: CurrentBranchContext
):
    """Get category suggestions for multiple expenses"""
    categories = db.query(ExpenseCategory).filter(
        (ExpenseCategory.branch_id == None) |
        (ExpenseCategory.branch_id == ctx.current_branch_id)
    ).all()

    available = [{"id": c.id, "name": c.name} for c in categories]
    category_map = {c.name.lower(): c.id for c in categories}

    expenses = [{"description": e.description, "amount": e.amount} for e in batch.expenses]

    categorizer = get_categorizer()
    results = categorizer.categorize_batch(expenses, available)

    # Add category IDs
    for r in results:
        cat_name = r.get("suggested_category", "").lower()
        r["category_id"] = category_map.get(cat_name)

    return results
