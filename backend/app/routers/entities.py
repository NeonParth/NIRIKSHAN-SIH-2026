from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import ContractAward, Contractor, Tender
from app.database.schemas.api import ContractorRead, NexusConnectionRead, Paginated, TenderRead
from app.services.nexus_service import NexusService
from app.utils.pagination import page_offset, pagination_params

contractors_router = APIRouter(prefix="/contractors", tags=["contractors"])
tenders_router = APIRouter(prefix="/tenders", tags=["tenders"])


@contractors_router.get("", response_model=Paginated[ContractorRead])
def list_contractors(paging: tuple[int, int] = Depends(pagination_params), db: Session = Depends(get_db)):
    page, page_size = paging
    total = db.scalar(select(func.count()).select_from(Contractor)) or 0
    rows = db.scalars(
        select(Contractor).order_by(Contractor.name).offset(page_offset(page, page_size)).limit(page_size)
    ).all()
    items = []
    for contractor in rows:
        award_count = db.scalar(
            select(func.count()).select_from(ContractAward).where(ContractAward.contractor_id == contractor.id)
        ) or 0
        items.append(
            ContractorRead(
                id=contractor.id,
                name=contractor.name,
                registration_no=contractor.registration_no,
                location_text=contractor.location_text,
                data_source=contractor.data_source,
                award_count=award_count,
                created_at=contractor.created_at,
                updated_at=contractor.updated_at,
            )
        )
    return Paginated(items=items, total=total, page=page, page_size=page_size)


@contractors_router.get("/{contractor_id}/nexus", response_model=list[NexusConnectionRead])
def get_contractor_nexus(contractor_id: UUID, db: Session = Depends(get_db)):
    service = NexusService(db)
    return service.find_nexus_for_contractor(contractor_id)


@tenders_router.get("", response_model=Paginated[TenderRead])
def list_tenders(paging: tuple[int, int] = Depends(pagination_params), db: Session = Depends(get_db)):
    page, page_size = paging
    total = db.scalar(select(func.count()).select_from(Tender)) or 0
    rows = db.scalars(
        select(Tender).order_by(Tender.created_at.desc()).offset(page_offset(page, page_size)).limit(page_size)
    ).all()
    return Paginated(
        items=[TenderRead.model_validate(item) for item in rows],
        total=total,
        page=page,
        page_size=page_size,
    )
