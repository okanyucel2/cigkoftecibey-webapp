"""
Multi-tenant mixins for SQLAlchemy models.

Phase 1: Adds tenant_id column (nullable for gradual migration)
Phase 2: Will make tenant_id NOT NULL after backfill
"""
from sqlalchemy import ForeignKey, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, declared_attr


class TenantMixin:
    """
    Mixin that adds tenant_id column for multi-tenant tables.

    Usage:
        class MyModel(TenantMixin, Base):
            __tablename__ = "my_table"
            ...

    The tenant_id column:
    - References organizations.id
    - Is indexed for query performance
    - Is nullable in Phase 1 (for gradual migration)
    - Will become NOT NULL in Phase 2 (after backfill)
    """

    @declared_attr
    def tenant_id(cls) -> Mapped[int]:
        return mapped_column(
            Integer,
            ForeignKey("organizations.id", ondelete="RESTRICT"),
            nullable=True,  # Phase 1: nullable for gradual migration
            index=True,  # Index for query performance
        )
