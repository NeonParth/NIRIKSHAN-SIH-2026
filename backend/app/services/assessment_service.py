from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database.models import (
    ContractAward,
    Contractor,
    Project,
    ProjectEvidence,
    RiskAssessment,
    RiskEvidence,
    RiskSignal,
    Tender,
)
from app.database.models.enums import (
    AnalysisType,
    DataSource,
    EvidenceType,
    VerificationStatus,
)
from app.database.schemas.api import (
    EvidenceRead,
    GeoPoint,
    LatestRiskSummary,
    ProjectDetail,
    ProjectSummary,
    RiskAssessmentRead,
    RiskEvidenceRead,
    RiskSignalRead,
)
from app.services import cost_analyzer, gis_service, image_processor, tender_service
from app.services.risk_engine import (
    SIGNAL_LABELS,
    SignalContribution,
    calculate_assessment,
    contribution_from_weight,
    load_weight_config,
)


def _latest_assessment(project: Project) -> RiskAssessment | None:
    if not project.risk_assessments:
        return None
    return sorted(project.risk_assessments, key=lambda item: item.created_at, reverse=True)[0]


def to_project_summary(project: Project) -> ProjectSummary:
    latest = _latest_assessment(project)
    latest_summary = None
    if latest:
        latest_summary = LatestRiskSummary.model_validate(latest)
    return ProjectSummary(
        id=project.id,
        code=project.code,
        name=project.name,
        description=project.description,
        location=gis_service.geometry_to_point(project.location),
        allocated_amount=float(project.allocated_amount) if project.allocated_amount is not None else None,
        benchmark_amount=float(project.benchmark_amount) if project.benchmark_amount is not None else None,
        sanctioned_date=project.sanctioned_date,
        completion_status=project.completion_status,
        data_source=project.data_source,
        created_at=project.created_at,
        updated_at=project.updated_at,
        latest_risk=latest_summary,
    )


def to_evidence(item: ProjectEvidence) -> EvidenceRead:
    return EvidenceRead.model_validate(item)


def to_assessment(item: RiskAssessment) -> RiskAssessmentRead:
    signals = [RiskSignalRead.model_validate(signal) for signal in item.signals]
    links = [
        RiskEvidenceRead(
            evidence_id=link.evidence_id,
            relevance=link.relevance,
            explanation=link.explanation,
            evidence=to_evidence(link.evidence) if link.evidence is not None else None,
        )
        for link in item.evidence_links
    ]
    return RiskAssessmentRead(
        id=item.id,
        project_id=item.project_id,
        risk_score=item.risk_score,
        risk_level=item.risk_level,
        reason_text=item.reason_text,
        source_module=item.source_module,
        analysis_type=item.analysis_type,
        data_source=item.data_source,
        verification_status=item.verification_status,
        reviewer_remarks=item.reviewer_remarks,
        reviewed_by=item.reviewed_by,
        reviewed_at=item.reviewed_at,
        created_at=item.created_at,
        updated_at=item.updated_at,
        contributing_signals=signals,
        evidence_references=links,
    )


def to_project_detail(project: Project) -> ProjectDetail:
    summary = to_project_summary(project)
    latest = _latest_assessment(project)
    return ProjectDetail(
        **summary.model_dump(),
        evidence=[to_evidence(item) for item in project.evidence],
        latest_assessment=to_assessment(latest) if latest else None,
    )


def _photo_hash(evidence: ProjectEvidence) -> str | None:
    if evidence.evidence_type not in {EvidenceType.PHOTO, EvidenceType.IMAGE_COMPARISON}:
        return None
    return image_processor.perceptual_hash_from_metadata(evidence.extra_metadata)


def collect_signals(db: Session, project: Project) -> tuple[list[SignalContribution], list[tuple[UUID, str, str]]]:
    settings = get_settings()
    config = load_weight_config(settings.resolved_weights_path())
    weights = {key: float(value) for key, value in config["signals"].items()}
    thresholds = config.get("thresholds", {})
    signals: list[SignalContribution] = []
    evidence_links: list[tuple[UUID, str, str]] = []

    proximity_m = float(thresholds.get("proximity_meters", 500))
    nearby = gis_service.find_nearby_projects(db, project.id, project.location, proximity_m)
    if nearby:
        nearest, distance = min(nearby, key=lambda pair: pair[1])
        signals.append(
            contribution_from_weight(
                "duplicate_proximity",
                weights=weights,
                observed_value=f"{distance:.1f}m from {nearest.code}",
                threshold=f"{proximity_m}m",
                explanation=(
                    f"Another project ({nearest.code}) is within {proximity_m} m. "
                    "This is a potential proximity/duplication signal and requires verification."
                ),
                source_reference=str(nearest.id),
                source_module="gis_engine",
            )
        )
        for item in project.evidence:
            if item.evidence_type == EvidenceType.LOCATION_COMPARISON:
                evidence_links.append((item.id, "supporting", "Location comparison for nearby-project signal"))

    project_hashes = [_photo_hash(item) for item in project.evidence]
    project_hashes = [value for value in project_hashes if value]
    if project_hashes:
        other_evidence = db.scalars(
            select(ProjectEvidence).where(ProjectEvidence.project_id != project.id)
        ).all()
        matches = []
        for item in other_evidence:
            other_hash = _photo_hash(item)
            if other_hash and any(image_processor.hashes_equal(other_hash, value) for value in project_hashes):
                matches.append(item)
        if matches:
            other_ids = ", ".join(sorted({str(item.project_id) for item in matches}))
            signals.append(
                contribution_from_weight(
                    "image_similarity",
                    weights=weights,
                    observed_value=f"matching_hash_count={len(matches)}",
                    threshold="exact metadata hash match",
                    explanation=(
                        "Evidence metadata contains the same demonstration perceptual hash as another project. "
                        "This is a potential image-similarity signal, not proof of recycled photographs."
                    ),
                    source_reference=other_ids,
                    source_module="computer_vision_placeholder",
                )
            )
            for item in project.evidence:
                if item.evidence_type in {EvidenceType.PHOTO, EvidenceType.IMAGE_COMPARISON}:
                    evidence_links.append((item.id, "supporting", "Image comparison for similarity signal"))

    ratio = cost_analyzer.deviation_ratio(project.allocated_amount, project.benchmark_amount)
    cost_threshold = float(thresholds.get("cost_deviation_ratio", 1.25))
    if ratio is not None and ratio >= cost_threshold:
        signals.append(
            contribution_from_weight(
                "cost_deviation",
                weights=weights,
                observed_value=f"ratio={ratio:.2f}",
                threshold=str(cost_threshold),
                explanation=(
                    f"Allocated amount is {ratio:.2f} times the demonstration benchmark. "
                    "This is a potential cost-deviation signal and requires verification."
                ),
                source_reference="project.benchmark_amount",
                source_module="cost_engine",
            )
        )
        for item in project.evidence:
            if item.evidence_type == EvidenceType.COST_COMPARISON:
                evidence_links.append((item.id, "supporting", "Cost comparison for deviation signal"))

    # --- Tender and Contractor Signals ---
    low_bidder_count = int(thresholds.get("low_bidder_count", 3))
    tenders = db.scalars(select(Tender).where(Tender.project_id == project.id)).all()
    for tender in tenders:
        sig = tender_service.get_bidder_competition_signal(tender, threshold_count=low_bidder_count)
        if sig:
            signals.append(
                contribution_from_weight(
                    sig["signal_code"],
                    weights=weights,
                    observed_value=sig["observed_value"],
                    threshold=sig["threshold"],
                    explanation=sig["explanation"],
                    source_reference=sig["source_reference"],
                    source_module=sig["source_module"],
                )
            )
            for item in project.evidence:
                if item.evidence_type == EvidenceType.TENDER_HISTORY:
                    evidence_links.append((item.id, "supporting", "Tender history for competition signal"))

    conc_sig = tender_service.get_contractor_concentration_signal(db, project)
    if conc_sig:
        signals.append(
            contribution_from_weight(
                conc_sig["signal_code"],
                weights=weights,
                observed_value=conc_sig["observed_value"],
                threshold=conc_sig["threshold"],
                explanation=conc_sig["explanation"],
                source_reference=conc_sig["source_reference"],
                source_module=conc_sig["source_module"],
            )
        )

    repeated_wins_count = int(thresholds.get("repeated_wins_count", 2))
    win_sig = tender_service.get_repeated_wins_signal(db, project, min_awards=repeated_wins_count)
    if win_sig:
        signals.append(
            contribution_from_weight(
                win_sig["signal_code"],
                weights=weights,
                observed_value=win_sig["observed_value"],
                threshold=win_sig["threshold"],
                explanation=win_sig["explanation"],
                source_reference=win_sig["source_reference"],
                source_module=win_sig["source_module"],
            )
        )

    return signals, evidence_links


def assess_project(db: Session, project_id: UUID) -> RiskAssessment:
    project = db.get(Project, project_id)
    if project is None:
        raise KeyError(project_id)
    project = db.scalars(
        select(Project)
        .options(selectinload(Project.evidence), selectinload(Project.risk_assessments))
        .where(Project.id == project_id)
    ).one()

    settings = get_settings()
    config = load_weight_config(settings.resolved_weights_path())
    weights = {key: float(value) for key, value in config["signals"].items()}
    levels = config.get("risk_levels")
    signals, evidence_links = collect_signals(db, project)
    result = calculate_assessment(
        signals,
        weights,
        source_module=str(config.get("source_module", "rule_based_risk_engine")),
        levels=levels,
    )

    assessment = RiskAssessment(
        project_id=project.id,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        reason_text=result.explanation,
        source_module=result.source_module,
        analysis_type=AnalysisType.RULE_BASED,
        data_source=project.data_source,
        verification_status=VerificationStatus.UNDER_REVIEW
        if result.risk_score >= 61
        else VerificationStatus.UNVERIFIED,
    )
    db.add(assessment)
    db.flush()

    for item in result.contributing_signals:
        db.add(
            RiskSignal(
                risk_assessment_id=assessment.id,
                signal_code=item.signal_code,
                signal_name=SIGNAL_LABELS.get(item.signal_code, item.signal_code),
                contribution=item.contribution,
                observed_value=item.observed_value,
                threshold=item.threshold,
                explanation=item.explanation,
                source_reference=item.source_reference,
                source_module=item.source_module,
            )
        )

    seen: set[UUID] = set()
    for evidence_id, relevance, explanation in evidence_links:
        if evidence_id in seen:
            continue
        seen.add(evidence_id)
        db.add(
            RiskEvidence(
                risk_assessment_id=assessment.id,
                evidence_id=evidence_id,
                relevance=relevance,
                explanation=explanation,
            )
        )

    db.commit()
    loaded = db.scalars(
        select(RiskAssessment)
        .options(
            selectinload(RiskAssessment.signals),
            selectinload(RiskAssessment.evidence_links).selectinload(RiskEvidence.evidence),
        )
        .where(RiskAssessment.id == assessment.id)
    ).one()
    return loaded


def apply_review(
    db: Session,
    assessment_id: UUID,
    status: VerificationStatus,
    remarks: str | None,
    reviewed_by: str | None,
) -> RiskAssessment:
    assessment = db.get(RiskAssessment, assessment_id)
    if assessment is None:
        raise KeyError(assessment_id)
    assessment.verification_status = status
    assessment.reviewer_remarks = remarks
    assessment.reviewed_by = reviewed_by
    assessment.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(assessment)
    return assessment
