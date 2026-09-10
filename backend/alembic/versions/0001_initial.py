"""Initial NIRIKSHAN schema with PostGIS geometry.

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-03
"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    data_source = postgresql.ENUM(
        "REAL", "PUBLIC", "SYNTHETIC", name="data_source", create_type=False
    )
    analysis_type = postgresql.ENUM(
        "RAW_DATA", "RULE_BASED", "MODEL_PREDICTION", name="analysis_type", create_type=False
    )
    verification_status = postgresql.ENUM(
        "UNVERIFIED",
        "UNDER_REVIEW",
        "HUMAN_VERIFIED",
        "HUMAN_REJECTED",
        name="verification_status",
        create_type=False,
    )
    risk_level = postgresql.ENUM(
        "LOW", "MEDIUM", "HIGH", "CRITICAL", name="risk_level", create_type=False
    )
    completion_status = postgresql.ENUM(
        "PROPOSED",
        "SANCTIONED",
        "IN_PROGRESS",
        "COMPLETED",
        "DELAYED",
        name="completion_status",
        create_type=False,
    )
    evidence_type = postgresql.ENUM(
        "PHOTO",
        "DOCUMENT",
        "LOCATION_COMPARISON",
        "IMAGE_COMPARISON",
        "COST_COMPARISON",
        "TENDER_HISTORY",
        name="evidence_type",
        create_type=False,
    )

    data_source.create(op.get_bind(), checkfirst=True)
    analysis_type.create(op.get_bind(), checkfirst=True)
    verification_status.create(op.get_bind(), checkfirst=True)
    risk_level.create(op.get_bind(), checkfirst=True)
    completion_status.create(op.get_bind(), checkfirst=True)
    evidence_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", Geometry(geometry_type="POINT", srid=4326), nullable=True),
        sa.Column("allocated_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("benchmark_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("sanctioned_date", sa.Date(), nullable=True),
        sa.Column("completion_status", completion_status, nullable=False),
        sa.Column("data_source", data_source, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_projects_code", "projects", ["code"])
    op.create_index("ix_projects_name", "projects", ["name"])
    op.create_index("ix_projects_created_at", "projects", ["created_at"])
    op.create_index("ix_projects_data_source", "projects", ["data_source"])
    op.create_index("ix_projects_completion_status", "projects", ["completion_status"])
    op.create_index("ix_projects_location", "projects", ["location"], postgresql_using="gist")

    op.create_table(
        "project_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("evidence_type", evidence_type, nullable=False),
        sa.Column("storage_uri", sa.String(1024), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("extra_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("data_source", data_source, nullable=False),
        sa.Column("verification_status", verification_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_project_evidence_project_id", "project_evidence", ["project_id"])

    op.create_table(
        "contractors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("registration_no", sa.String(128), nullable=True),
        sa.Column("location_text", sa.String(255), nullable=True),
        sa.Column("data_source", data_source, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("registration_no"),
    )
    op.create_index("ix_contractors_name", "contractors", ["name"])

    op.create_table(
        "tenders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("official_tender_id", sa.String(128), nullable=False),
        sa.Column("bidder_count", sa.Integer(), nullable=True),
        sa.Column("winning_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("data_source", data_source, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("official_tender_id"),
    )
    op.create_index("ix_tenders_project_id", "tenders", ["project_id"])
    op.create_index("ix_tenders_official_tender_id", "tenders", ["official_tender_id"])

    op.create_table(
        "contract_awards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tender_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenders.id"), nullable=False),
        sa.Column("contractor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contractors.id"), nullable=False),
        sa.Column("award_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("award_date", sa.Date(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("data_source", data_source, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("tender_id", "contractor_id", "rank", name="uq_award_tender_contractor_rank"),
    )
    op.create_index("ix_contract_awards_tender_id", "contract_awards", ["tender_id"])
    op.create_index("ix_contract_awards_contractor_id", "contract_awards", ["contractor_id"])

    op.create_table(
        "risk_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("risk_level", risk_level, nullable=False),
        sa.Column("reason_text", sa.Text(), nullable=False),
        sa.Column("source_module", sa.String(128), nullable=False),
        sa.Column("analysis_type", analysis_type, nullable=False),
        sa.Column("data_source", data_source, nullable=False),
        sa.Column("verification_status", verification_status, nullable=False),
        sa.Column("reviewer_remarks", sa.Text(), nullable=True),
        sa.Column("reviewed_by", sa.String(128), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_risk_assessments_project_id", "risk_assessments", ["project_id"])
    op.create_index("ix_risk_assessments_risk_score", "risk_assessments", ["risk_score"])
    op.create_index("ix_risk_assessments_risk_level", "risk_assessments", ["risk_level"])
    op.create_index("ix_risk_assessments_created_at", "risk_assessments", ["created_at"])
    op.create_index("ix_risk_assessments_verification_status", "risk_assessments", ["verification_status"])

    op.create_table(
        "risk_signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "risk_assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("risk_assessments.id"),
            nullable=False,
        ),
        sa.Column("signal_code", sa.String(64), nullable=False),
        sa.Column("signal_name", sa.String(128), nullable=False),
        sa.Column("contribution", sa.Numeric(6, 2), nullable=False),
        sa.Column("observed_value", sa.String(255), nullable=True),
        sa.Column("threshold", sa.String(255), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("source_reference", sa.String(255), nullable=True),
        sa.Column("source_module", sa.String(128), nullable=False),
    )
    op.create_index("ix_risk_signals_assessment_id", "risk_signals", ["risk_assessment_id"])
    op.create_index("ix_risk_signals_signal_code", "risk_signals", ["signal_code"])

    op.create_table(
        "risk_evidence",
        sa.Column(
            "risk_assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("risk_assessments.id"),
            primary_key=True,
        ),
        sa.Column(
            "evidence_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("project_evidence.id"),
            primary_key=True,
        ),
        sa.Column("relevance", sa.String(64), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("risk_evidence")
    op.drop_table("risk_signals")
    op.drop_table("risk_assessments")
    op.drop_table("contract_awards")
    op.drop_table("tenders")
    op.drop_table("contractors")
    op.drop_table("project_evidence")
    op.drop_table("projects")
    op.execute("DROP TYPE IF EXISTS evidence_type")
    op.execute("DROP TYPE IF EXISTS completion_status")
    op.execute("DROP TYPE IF EXISTS risk_level")
    op.execute("DROP TYPE IF EXISTS verification_status")
    op.execute("DROP TYPE IF EXISTS analysis_type")
    op.execute("DROP TYPE IF EXISTS data_source")
