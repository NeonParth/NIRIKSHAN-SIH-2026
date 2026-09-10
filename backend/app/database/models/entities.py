from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.database.models.enums import (
    AnalysisType,
    CompletionStatus,
    DataSource,
    EvidenceType,
    RiskLevel,
    VerificationStatus,
)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    allocated_amount: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    benchmark_amount: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    sanctioned_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completion_status: Mapped[CompletionStatus] = mapped_column(
        Enum(CompletionStatus, name="completion_status"), default=CompletionStatus.PROPOSED
    )
    data_source: Mapped[DataSource] = mapped_column(Enum(DataSource, name="data_source"), default=DataSource.SYNTHETIC)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    evidence: Mapped[list[ProjectEvidence]] = relationship(back_populates="project")
    tenders: Mapped[list[Tender]] = relationship(back_populates="project")
    risk_assessments: Mapped[list[RiskAssessment]] = relationship(back_populates="project")

    __table_args__ = (
        Index("ix_projects_location", "location", postgresql_using="gist"),
        Index("ix_projects_created_at", "created_at"),
        Index("ix_projects_data_source", "data_source"),
        Index("ix_projects_completion_status", "completion_status"),
    )


class ProjectEvidence(Base):
    __tablename__ = "project_evidence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), index=True)
    evidence_type: Mapped[EvidenceType] = mapped_column(Enum(EvidenceType, name="evidence_type"))
    storage_uri: Mapped[str] = mapped_column(String(1024))
    captured_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    data_source: Mapped[DataSource] = mapped_column(Enum(DataSource, name="data_source"), default=DataSource.SYNTHETIC)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status"), default=VerificationStatus.UNVERIFIED
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped[Project] = relationship(back_populates="evidence")
    risk_links: Mapped[list[RiskEvidence]] = relationship(back_populates="evidence")


class Contractor(Base):
    __tablename__ = "contractors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), index=True)
    registration_no: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, unique=True)
    pan_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    gstin: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    address_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    parent_company_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("contractors.id"), nullable=True)
    location_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    data_source: Mapped[DataSource] = mapped_column(Enum(DataSource, name="data_source"), default=DataSource.SYNTHETIC)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    awards: Mapped[list[ContractAward]] = relationship(back_populates="contractor")


class Tender(Base):
    __tablename__ = "tenders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), index=True)
    official_tender_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    bidder_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    winning_amount: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    data_source: Mapped[DataSource] = mapped_column(Enum(DataSource, name="data_source"), default=DataSource.SYNTHETIC)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped[Project] = relationship(back_populates="tenders")
    awards: Mapped[list[ContractAward]] = relationship(back_populates="tender")


class ContractAward(Base):
    __tablename__ = "contract_awards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenders.id"), index=True)
    contractor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("contractors.id"), index=True)
    award_amount: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    award_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    rank: Mapped[Optional[int]] = mapped_column(nullable=True)
    data_source: Mapped[DataSource] = mapped_column(Enum(DataSource, name="data_source"), default=DataSource.SYNTHETIC)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tender: Mapped[Tender] = relationship(back_populates="awards")
    contractor: Mapped[Contractor] = relationship(back_populates="awards")

    __table_args__ = (UniqueConstraint("tender_id", "contractor_id", "rank", name="uq_award_tender_contractor_rank"),)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), index=True)
    risk_score: Mapped[int] = mapped_column(index=True)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel, name="risk_level"), index=True)
    reason_text: Mapped[str] = mapped_column(Text)
    source_module: Mapped[str] = mapped_column(String(128), default="rule_based_risk_engine")
    analysis_type: Mapped[AnalysisType] = mapped_column(
        Enum(AnalysisType, name="analysis_type"), default=AnalysisType.RULE_BASED
    )
    data_source: Mapped[DataSource] = mapped_column(Enum(DataSource, name="data_source"), default=DataSource.SYNTHETIC)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status"), default=VerificationStatus.UNVERIFIED, index=True
    )
    reviewer_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped[Project] = relationship(back_populates="risk_assessments")
    signals: Mapped[list[RiskSignal]] = relationship(back_populates="assessment", cascade="all, delete-orphan")
    evidence_links: Mapped[list[RiskEvidence]] = relationship(back_populates="assessment", cascade="all, delete-orphan")


class RiskSignal(Base):
    __tablename__ = "risk_signals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("risk_assessments.id"), index=True
    )
    signal_code: Mapped[str] = mapped_column(String(64), index=True)
    signal_name: Mapped[str] = mapped_column(String(128))
    contribution: Mapped[float] = mapped_column(Numeric(6, 2))
    observed_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    threshold: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    explanation: Mapped[str] = mapped_column(Text)
    source_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_module: Mapped[str] = mapped_column(String(128))

    assessment: Mapped[RiskAssessment] = relationship(back_populates="signals")


class RiskEvidence(Base):
    __tablename__ = "risk_evidence"

    risk_assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("risk_assessments.id"), primary_key=True
    )
    evidence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project_evidence.id"), primary_key=True
    )
    relevance: Mapped[str] = mapped_column(String(64), default="supporting")
    explanation: Mapped[str] = mapped_column(Text)

    assessment: Mapped[RiskAssessment] = relationship(back_populates="evidence_links")
    evidence: Mapped[ProjectEvidence] = relationship(back_populates="risk_links")
