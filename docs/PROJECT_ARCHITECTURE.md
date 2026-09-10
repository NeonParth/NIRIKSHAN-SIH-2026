# Project Architecture: NIRIKSHAN

## Overview
NIRIKSHAN is an evidence-driven risk analysis platform designed to identify anomalies, procurement irregularities, and cost deviations in the MPLADS Scheme. The system focuses on risk signals rather than definitive fraud detection, providing a foundation for human investigators.

## Phase 1 Architecture

The Phase 1 implementation establishes a modular foundation:

### 1. Data Ingestion & Storage
- **PostgreSQL + PostGIS**: Used for relational data and geospatial queries.
- **Geometry Types**: Project locations are stored as `POINT` geometry to enable proximity analysis.
- **Normalized Entities**: Projects, Evidence, Tenders, Contractors, and Risk Assessments are stored in a normalized relational schema.

### 2. Backend (FastAPI)
- **Modular Service Layer**:
    - `gis_service`: Handles geospatial queries (e.g., finding projects within X meters).
    - `cost_analyzer`: Computes cost deviations against benchmarks.
    - `image_processor`: Detects image similarity using perceptual hashing.
    - `tender_service`: Analyzes bidder competition and contractor patterns.
    - `assessment_service`: Orchestrates signal collection and triggers the Risk Engine.
- **API v1**: Versioned REST API providing endpoints for projects, risks, and contractors.

### 3. Risk Engine (Deterministic)
- **Weight-Based Scoring**: Uses a YAML-configured weight map.
- **Explainability**: Every risk score is decomposed into contributing signals with observed values and thresholds.
- **Risk Levels**: Maps numerical scores (0-100) to categories (LOW, MEDIUM, HIGH, CRITICAL).

### 4. Frontend (React + TS)
- **Government-Style Interface**: A clean, data-dense UI focusing on evidence traceability.
- **Provenance Tracking**: Explicitly labels synthetic data to prevent misinterpretation.

## Future Extensions (Phase 2+)
- **Production ML**: Moving from metadata hashes to deep-learning image similarity.
- **GIS Analytics**: Advanced spatial clustering of suspicious projects.
- **Relationship Graphs**: Using Graph databases (e.g., Neo4j) to uncover complex contractor webs.
- **Full Authentication**: Implementing RBAC for government officers.
