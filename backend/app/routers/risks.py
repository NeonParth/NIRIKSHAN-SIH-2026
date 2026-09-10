from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database.connection import get_db
from app.database.models import Project, ProjectEvidence, RiskAssessment, RiskEvidence
from app.database.models.enums import RiskLevel, VerificationStatus
from app.database.schemas.api import EvidenceRead, Paginated, ReviewUpdate, RiskAssessmentRead
from app.services.assessment_service import apply_review, assess_project, to_assessment, to_evidence
from app.utils.errors import http_error
from app.utils.pagination import page_offset, pagination_params

router = APIRouter(prefix="", tags=["risks"])


@router.get("/projects/{project_id}/evidence", response_model=list[EvidenceRead])
def list_project_evidence(project_id: UUID, db: Session = Depends(get_db)):
    if db.get(Project, project_id) is None:
        raise http_error(status.HTTP_404_NOT_FOUND, "NOT_FOUND", "Project not found")
    rows = db.scalars(select(ProjectEvidence).where(ProjectEvidence.project_id == project_id)).all()
    return [to_evidence(item) for item in rows]


@router.get("/projects/{project_id}/risks", response_model=list[RiskAssessmentRead])
def list_project_risks(project_id: UUID, db: Session = Depends(get_db)):
    if db.get(Project, project_id) is None:
        raise http_error(status.HTTP_404_NOT_FOUND, "NOT_FOUND", "Project not found")
    rows = db.scalars(
        select(RiskAssessment)
        .options(
            selectinload(RiskAssessment.signals),
            selectinload(RiskAssessment.evidence_links).selectinload(RiskEvidence.evidence),
        )
        .where(RiskAssessment.project_id == project_id)
        .order_by(RiskAssessment.created_at.desc())
    ).all()
    return [to_assessment(item) for item in rows]


@router.post("/risks/assess/{project_id}", response_model=RiskAssessmentRead)
def assess(project_id: UUID, db: Session = Depends(get_db)):
    if db.get(Project, project_id) is None:
        raise http_error(status.HTTP_404_NOT_FOUND, "NOT_FOUND", "Project not found")
    return to_assessment(assess_project(db, project_id))


@router.get("/risks", response_model=Paginated[RiskAssessmentRead])
def list_risks(
    project_id: UUID | None = None,
    risk_level: RiskLevel | None = None,
    verification_status: VerificationStatus | None = None,
    paging: tuple[int, int] = Depends(pagination_params),
    db: Session = Depends(get_db),
):
    page, page_size = paging
    stmt = select(RiskAssessment).options(
        selectinload(RiskAssessment.signals),
        selectinload(RiskAssessment.evidence_links).selectinload(RiskEvidence.evidence),
    )
    if project_id:
        stmt = stmt.where(RiskAssessment.project_id == project_id)
    if risk_level:
        stmt = stmt.where(RiskAssessment.risk_level == risk_level)
    if verification_status:
        stmt = stmt.where(RiskAssessment.verification_status == verification_status)
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    rows = db.scalars(
        stmt.order_by(RiskAssessment.created_at.desc()).offset(page_offset(page, page_size)).limit(page_size)
    ).all()
    return Paginated(items=[to_assessment(item) for item in rows], total=total, page=page, page_size=page_size)


@router.post("/risks/{assessment_id}/review", response_model=RiskAssessmentRead)
def review_assessment(assessment_id: UUID, payload: ReviewUpdate, db: Session = Depends(get_db)):
    try:
        updated = apply_review(
            db,
            assessment_id,
            payload.verification_status,
            payload.remarks,
            payload.reviewed_by,
        )
    except KeyError:
        raise http_error(status.HTTP_404_NOT_FOUND, "NOT_FOUND", "Risk assessment not found")
    loaded = db.scalars(
        select(RiskAssessment)
        .options(
            selectinload(RiskAssessment.signals),
            selectinload(RiskAssessment.evidence_links).selectinload(RiskEvidence.evidence),
        )
        .where(RiskAssessment.id == updated.id)
    ).one()
    return to_assessment(loaded)
