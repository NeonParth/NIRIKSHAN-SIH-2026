from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import ContractAward, Project, Tender


def get_bidder_competition_signal(tender: Tender, threshold_count: int = 3) -> Optional[dict[str, Any]]:
    if tender.bidder_count is None:
        return None

    if tender.bidder_count < threshold_count:
        return {
            "signal_code": "low_bidder_competition",
            "observed_value": f"{tender.bidder_count} bidders",
            "threshold": f"<{threshold_count} bidders",
            "explanation": (
                f"Tender had only {tender.bidder_count} bidder(s), below the configured "
                f"threshold of {threshold_count}. This is a potential competition signal "
                "and requires verification."
            ),
            "source_reference": f"Tender {tender.official_tender_id}",
            "source_module": "tender_service",
        }
    return None


def get_contractor_concentration_signal(db: Session, project: Project) -> Optional[dict[str, Any]]:
    for tender in project.tenders:
        for award in tender.awards:
            contractor_id = award.contractor_id
            count = db.scalar(
                select(func.count()).select_from(ContractAward).where(ContractAward.contractor_id == contractor_id)
            ) or 0
            if count > 5:
                return {
                    "signal_code": "contractor_concentration",
                    "observed_value": f"{count} awards",
                    "threshold": "<= 5 awards",
                    "explanation": (
                        f"Contractor has a high concentration of awards ({count} projects). "
                        "This is a potential concentration signal and requires verification."
                    ),
                    "source_reference": f"Contractor {contractor_id}",
                    "source_module": "tender_service",
                }
    return None


def get_repeated_wins_signal(
    db: Session,
    project: Project,
    min_awards: int = 2,
) -> Optional[dict[str, Any]]:
    contractor_ids = db.scalars(
        select(ContractAward.contractor_id).join(Tender).where(Tender.project_id == project.id)
    ).all()
    seen: set[UUID] = set()
    for contractor_id in contractor_ids:
        if contractor_id in seen:
            continue
        seen.add(contractor_id)
        count = db.scalar(
            select(func.count()).select_from(ContractAward).where(ContractAward.contractor_id == contractor_id)
        ) or 0
        if count >= min_awards:
            return {
                "signal_code": "repeated_contractor_wins",
                "observed_value": f"{count} awards",
                "threshold": f">= {min_awards} awards",
                "explanation": (
                    f"The same contractor has {count} award(s) in this demonstration dataset, "
                    f"meeting the configured repeated-wins threshold of {min_awards}. "
                    "This is a potential repeated-award signal and requires verification."
                ),
                "source_reference": f"Contractor {contractor_id}",
                "source_module": "tender_service",
            }
    return None
