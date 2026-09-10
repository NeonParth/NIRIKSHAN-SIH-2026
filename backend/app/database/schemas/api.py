from __future__ import annotations

from datetime import date, datetime
from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.database.models.enums import (
    AnalysisType,
    CompletionStatus,
    DataSource,
    EvidenceType,
    RiskLevel,
    VerificationStatus,
)


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


T = TypeVar("T")


class Paginated(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class GeoPoint(BaseModel):
    longitude: float
    latitude: float


class ProjectCreate(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    allocated_amount: Optional[float] = Field(default=None, ge=0)
    benchmark_amount: Optional[float] = Field(default=None, ge=0)
    sanctioned_date: Optional[date] = None
    completion_status: CompletionStatus = CompletionStatus.PROPOSED
    data_source: DataSource = DataSource.SYNTHETIC


class LatestRiskSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    risk_score: int
    risk_level: RiskLevel
    verification_status: VerificationStatus
    analysis_type: AnalysisType
    created_at: datetime


class ProjectSummary(BaseModel):
    id: UUID
    code: str
    name: str
    description: Optional[str]
    location: Optional[GeoPoint]
    allocated_amount: Optional[float]
    benchmark_amount: Optional[float]
    sanctioned_date: Optional[date]
    completion_status: CompletionStatus
    data_source: DataSource
    created_at: datetime
    updated_at: datetime
    latest_risk: Optional[LatestRiskSummary] = None


class EvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    evidence_type: EvidenceType
    storage_uri: str
    captured_at: Optional[datetime]
    extra_metadata: Optional[dict[str, Any]]
    data_source: DataSource
    verification_status: VerificationStatus
    created_at: datetime
    updated_at: datetime


class RiskSignalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    signal_code: str
    signal_name: str
    contribution: float
    observed_value: Optional[str]
    threshold: Optional[str]
    explanation: str
    source_reference: Optional[str]
    source_module: str


class RiskEvidenceRead(BaseModel):
    evidence_id: UUID
    relevance: str
    explanation: str
    evidence: Optional[EvidenceRead] = None


class RiskAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    risk_score: int
    risk_level: RiskLevel
    reason_text: str
    source_module: str
    analysis_type: AnalysisType
    data_source: DataSource
    verification_status: VerificationStatus
    reviewer_remarks: Optional[str]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    contributing_signals: list[RiskSignalRead] = Field(default_factory=list)
    evidence_references: list[RiskEvidenceRead] = Field(default_factory=list)


class ProjectDetail(ProjectSummary):
    evidence: list[EvidenceRead] = Field(default_factory=list)
    latest_assessment: Optional[RiskAssessmentRead] = None


class TenderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    official_tender_id: str
    bidder_count: Optional[int]
    winning_amount: Optional[float]
    data_source: DataSource
    created_at: datetime
    updated_at: datetime


class ContractorRead(BaseModel):
    id: UUID
    name: str
    registration_no: Optional[str]
    location_text: Optional[str]
    data_source: DataSource
    award_count: int
    created_at: datetime
    updated_at: datetime


class ReviewUpdate(BaseModel):
    verification_status: VerificationStatus
    remarks: Optional[str] = None
    reviewed_by: Optional[str] = Field(default="phase1-reviewer", max_length=128)


class NexusConnectionRead(BaseModel):
    entity_a: UUID
    entity_b: UUID
    connection_type: str
    confidence: float
    evidence: str


class HealthResponse(BaseModel):
    status: str
    database: str
