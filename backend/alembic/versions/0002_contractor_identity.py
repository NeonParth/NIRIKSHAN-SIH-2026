"""Add contractor identity columns used by the ORM.

Revision ID: 0002_contractor_identity
Revises: 0001_initial
Create Date: 2026-09-03
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_contractor_identity"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("contractors", sa.Column("pan_number", sa.String(64), nullable=True))
    op.add_column("contractors", sa.Column("gstin", sa.String(64), nullable=True))
    op.add_column("contractors", sa.Column("email", sa.String(255), nullable=True))
    op.add_column("contractors", sa.Column("phone", sa.String(64), nullable=True))
    op.add_column("contractors", sa.Column("address_hash", sa.String(128), nullable=True))
    op.add_column(
        "contractors",
        sa.Column("parent_company_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_contractors_parent_company_id",
        "contractors",
        "contractors",
        ["parent_company_id"],
        ["id"],
    )
    op.create_index("ix_contractors_pan_number", "contractors", ["pan_number"])
    op.create_index("ix_contractors_gstin", "contractors", ["gstin"])
    op.create_index("ix_contractors_email", "contractors", ["email"])
    op.create_index("ix_contractors_phone", "contractors", ["phone"])
    op.create_index("ix_contractors_address_hash", "contractors", ["address_hash"])


def downgrade() -> None:
    op.drop_index("ix_contractors_address_hash", table_name="contractors")
    op.drop_index("ix_contractors_phone", table_name="contractors")
    op.drop_index("ix_contractors_email", table_name="contractors")
    op.drop_index("ix_contractors_gstin", table_name="contractors")
    op.drop_index("ix_contractors_pan_number", table_name="contractors")
    op.drop_constraint("fk_contractors_parent_company_id", "contractors", type_="foreignkey")
    op.drop_column("contractors", "parent_company_id")
    op.drop_column("contractors", "address_hash")
    op.drop_column("contractors", "phone")
    op.drop_column("contractors", "email")
    op.drop_column("contractors", "gstin")
    op.drop_column("contractors", "pan_number")
