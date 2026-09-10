# Data Model: NIRIKSHAN

## Entity Relationship Diagram (Conceptual)
`Project` $\rightarrow$ (1:N) $\rightarrow$ `ProjectEvidence`
`Project` $\rightarrow$ (1:N) $\rightarrow$ `Tender`
`Tender` $\rightarrow$ (1:N) $\rightarrow$ `ContractAward`
`Contractor` $\rightarrow$ (1:N) $\rightarrow$ `ContractAward`
`Project` $\rightarrow$ (1:N) $\rightarrow$ `RiskAssessment`
`RiskAssessment` $\rightarrow$ (1:N) $\rightarrow$ `RiskSignal`
`RiskAssessment` $\rightarrow$ (M:N) $\rightarrow$ `ProjectEvidence` (via `RiskEvidence`)

## Core Tables

### 1. projects
- `id` (UUID, PK)
- `code` (String, Unique) - Unique project identifier.
- `name` (String)
- `location` (Geometry Point) - PostGIS geometry for spatial analysis.
- `allocated_amount` (Numeric)
- `benchmark_amount` (Numeric) - Used for cost deviation analysis.
- `data_source` (Enum: REAL, PUBLIC, SYNTHETIC)
- `completion_status` (Enum)

### 2. project_evidence
- `id` (UUID, PK)
- `project_id` (FK $\rightarrow$ projects)
- `evidence_type` (Enum: PHOTO, GPS, DOCUMENT, etc.)
- `storage_uri` (String)
- `extra_metadata` (JSONB) - Stores perceptual hashes and EXIF data.
- `verification_status` (Enum: UNVERIFIED, UNDER_REVIEW, HUMAN_VERIFIED, HUMAN_REJECTED)

### 3. tenders
- `id` (UUID, PK)
- `project_id` (FK $\rightarrow$ projects)
- `official_tender_id` (String, Unique)
- `bidder_count` (Integer)
- `winning_amount` (Numeric)

### 4. contractors
- `id` (UUID, PK)
- `name` (String)
- `registration_no` (String)

### 5. contract_awards
- `id` (UUID, PK)
- `tender_id` (FK $\rightarrow$ tenders)
- `contractor_id` (FK $\rightarrow$ contractors)
- `award_amount` (Numeric)

### 6. risk_assessments
- `id` (UUID, PK)
- `project_id` (FK $\rightarrow$ projects)
- `risk_score` (Integer)
- `risk_level` (Enum)
- `reason_text` (Text)
- `verification_status` (Enum)

### 7. risk_signals
- `id` (UUID, PK)
- `risk_assessment_id` (FK $\rightarrow$ risk_assessments)
- `signal_code` (String) - e.g., `cost_deviation`.
- `contribution` (Float) - Weight added to total score.
- `observed_value` (String)
- `threshold` (String)
- `explanation` (Text)

## Data Provenance
The `data_source` field is present on all primary entities to ensure that synthetic data used for demonstration is never confused with real government data.
