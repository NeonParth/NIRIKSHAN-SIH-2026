from __future__ import annotations

import enum


class DataSource(str, enum.Enum):
    REAL = "REAL"
    PUBLIC = "PUBLIC"
    SYNTHETIC = "SYNTHETIC"


class AnalysisType(str, enum.Enum):
    RAW_DATA = "RAW_DATA"
    RULE_BASED = "RULE_BASED"
    MODEL_PREDICTION = "MODEL_PREDICTION"


class VerificationStatus(str, enum.Enum):
    UNVERIFIED = "UNVERIFIED"
    UNDER_REVIEW = "UNDER_REVIEW"
    HUMAN_VERIFIED = "HUMAN_VERIFIED"
    HUMAN_REJECTED = "HUMAN_REJECTED"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CompletionStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    SANCTIONED = "SANCTIONED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DELAYED = "DELAYED"


class EvidenceType(str, enum.Enum):
    PHOTO = "PHOTO"
    DOCUMENT = "DOCUMENT"
    LOCATION_COMPARISON = "LOCATION_COMPARISON"
    IMAGE_COMPARISON = "IMAGE_COMPARISON"
    COST_COMPARISON = "COST_COMPARISON"
    TENDER_HISTORY = "TENDER_HISTORY"
