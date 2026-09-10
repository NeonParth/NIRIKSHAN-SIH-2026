from __future__ import annotations

from uuid import UUID, uuid5, NAMESPACE_DNS
from datetime import date, datetime, timezone

from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import (
    ContractAward,
    Contractor,
    Project,
    ProjectEvidence,
    Tender,
)
from app.database.models.enums import (
    CompletionStatus,
    DataSource,
    EvidenceType,
    VerificationStatus,
)
from app.services.assessment_service import assess_project
from app.services.gis_service import point_wkt

DEMO_NS = uuid5(NAMESPACE_DNS, "nirikshan.synthetic.demo")


def demo_uuid(name: str) -> UUID:
    return uuid5(DEMO_NS, name)


def seed_if_empty(db: Session) -> dict[str, str]:
    existing = db.scalar(select(Project).where(Project.code == "DEMO-001"))
    if existing:
        return {"status": "already_seeded", "demo_project": "DEMO-001"}

    now = datetime.now(timezone.utc)
    loc_a = WKTElement(point_wkt(79.0800, 21.1500), srid=4326)
    loc_b = WKTElement(point_wkt(79.0812, 21.1508), srid=4326)
    loc_c = WKTElement(point_wkt(78.5000, 20.5000), srid=4326)

    demo_001 = Project(
        id=demo_uuid("project-DEMO-001"),
        code="DEMO-001",
        name="Synthetic Community Hall — Demo Ward A",
        description=(
            "SYNTHETIC demonstration project used to exercise the explainable risk workflow. "
            "Not an official MPLADS record."
        ),
        location=loc_a,
        allocated_amount=2500000,
        benchmark_amount=1600000,
        sanctioned_date=date(2025, 4, 1),
        completion_status=CompletionStatus.IN_PROGRESS,
        data_source=DataSource.SYNTHETIC,
    )
    demo_002 = Project(
        id=demo_uuid("project-DEMO-002"),
        code="DEMO-002",
        name="Synthetic Community Hall — Demo Ward A Adjacent",
        description="SYNTHETIC nearby comparison project for proximity and image-hash demonstration.",
        location=loc_b,
        allocated_amount=1550000,
        benchmark_amount=1600000,
        sanctioned_date=date(2025, 3, 15),
        completion_status=CompletionStatus.COMPLETED,
        data_source=DataSource.SYNTHETIC,
    )
    demo_003 = Project(
        id=demo_uuid("project-DEMO-003"),
        code="DEMO-003",
        name="Synthetic Solar Lights — Demo Ward C",
        description="SYNTHETIC lower-signal comparison project.",
        location=loc_c,
        allocated_amount=400000,
        benchmark_amount=420000,
        sanctioned_date=date(2025, 1, 10),
        completion_status=CompletionStatus.COMPLETED,
        data_source=DataSource.SYNTHETIC,
    )
    demo_004 = Project(
        id=demo_uuid("project-DEMO-004"),
        code="DEMO-004",
        name="Synthetic Drain Repair — Demo Ward D",
        description="SYNTHETIC additional award used to demonstrate repeated contractor wins.",
        location=WKTElement(point_wkt(78.5100, 20.5100), srid=4326),
        allocated_amount=700000,
        benchmark_amount=690000,
        sanctioned_date=date(2025, 2, 20),
        completion_status=CompletionStatus.SANCTIONED,
        data_source=DataSource.SYNTHETIC,
    )
    db.add_all([demo_001, demo_002, demo_003, demo_004])

    contractor = Contractor(
        id=demo_uuid("contractor-alpha"),
        name="SYNTHETIC Contractor Alpha",
        registration_no="SYN-REG-0001",
        location_text="Demo District (synthetic)",
        data_source=DataSource.SYNTHETIC,
    )
    contractor_b = Contractor(
        id=demo_uuid("contractor-beta"),
        name="SYNTHETIC Contractor Beta",
        registration_no="SYN-REG-0002",
        location_text="Demo District (synthetic)",
        data_source=DataSource.SYNTHETIC,
    )
    db.add_all([contractor, contractor_b])

    t1 = Tender(
        id=demo_uuid("tender-001"),
        project_id=demo_001.id,
        official_tender_id="SYN-TENDER-001",
        bidder_count=1,
        winning_amount=2400000,
        data_source=DataSource.SYNTHETIC,
    )
    t2 = Tender(
        id=demo_uuid("tender-002"),
        project_id=demo_002.id,
        official_tender_id="SYN-TENDER-002",
        bidder_count=5,
        winning_amount=1500000,
        data_source=DataSource.SYNTHETIC,
    )
    t3 = Tender(
        id=demo_uuid("tender-003"),
        project_id=demo_003.id,
        official_tender_id="SYN-TENDER-003",
        bidder_count=6,
        winning_amount=390000,
        data_source=DataSource.SYNTHETIC,
    )
    t4 = Tender(
        id=demo_uuid("tender-004"),
        project_id=demo_004.id,
        official_tender_id="SYN-TENDER-004",
        bidder_count=4,
        winning_amount=680000,
        data_source=DataSource.SYNTHETIC,
    )
    db.add_all([t1, t2, t3, t4])

    db.add_all(
        [
            ContractAward(
                id=demo_uuid("award-001"),
                tender_id=t1.id,
                contractor_id=contractor.id,
                award_amount=2400000,
                award_date=date(2025, 5, 1),
                rank=1,
                data_source=DataSource.SYNTHETIC,
            ),
            ContractAward(
                id=demo_uuid("award-004"),
                tender_id=t4.id,
                contractor_id=contractor.id,
                award_amount=680000,
                award_date=date(2025, 3, 1),
                rank=1,
                data_source=DataSource.SYNTHETIC,
            ),
            ContractAward(
                id=demo_uuid("award-002"),
                tender_id=t2.id,
                contractor_id=contractor_b.id,
                award_amount=1500000,
                award_date=date(2025, 4, 10),
                rank=1,
                data_source=DataSource.SYNTHETIC,
            ),
            ContractAward(
                id=demo_uuid("award-003"),
                tender_id=t3.id,
                contractor_id=contractor_b.id,
                award_amount=390000,
                award_date=date(2025, 2, 1),
                rank=1,
                data_source=DataSource.SYNTHETIC,
            ),
        ]
    )

    db.add_all(
        [
            ProjectEvidence(
                id=demo_uuid("ev-001-photo"),
                project_id=demo_001.id,
                evidence_type=EvidenceType.PHOTO,
                storage_uri="data/synthetic/evidence/demo001_site.txt",
                captured_at=now,
                extra_metadata={"perceptual_hash": "SYNTH-HASH-A1", "note": "synthetic placeholder"},
                data_source=DataSource.SYNTHETIC,
                verification_status=VerificationStatus.UNVERIFIED,
            ),
            ProjectEvidence(
                id=demo_uuid("ev-001-image"),
                project_id=demo_001.id,
                evidence_type=EvidenceType.IMAGE_COMPARISON,
                storage_uri="data/synthetic/evidence/demo001_site.txt",
                captured_at=now,
                extra_metadata={"perceptual_hash": "SYNTH-HASH-A1"},
                data_source=DataSource.SYNTHETIC,
                verification_status=VerificationStatus.UNVERIFIED,
            ),
            ProjectEvidence(
                id=demo_uuid("ev-001-loc"),
                project_id=demo_001.id,
                evidence_type=EvidenceType.LOCATION_COMPARISON,
                storage_uri="data/synthetic/evidence/demo001_site.txt",
                captured_at=now,
                extra_metadata={"compared_with": "DEMO-002"},
                data_source=DataSource.SYNTHETIC,
                verification_status=VerificationStatus.UNVERIFIED,
            ),
            ProjectEvidence(
                id=demo_uuid("ev-001-cost"),
                project_id=demo_001.id,
                evidence_type=EvidenceType.COST_COMPARISON,
                storage_uri="data/synthetic/evidence/demo001_cost.txt",
                captured_at=now,
                extra_metadata={"allocated": 2500000, "benchmark": 1600000},
                data_source=DataSource.SYNTHETIC,
                verification_status=VerificationStatus.UNVERIFIED,
            ),
            ProjectEvidence(
                id=demo_uuid("ev-001-tender"),
                project_id=demo_001.id,
                evidence_type=EvidenceType.TENDER_HISTORY,
                storage_uri="data/synthetic/evidence/demo001_cost.txt",
                captured_at=now,
                extra_metadata={"official_tender_id": "SYN-TENDER-001", "bidder_count": 1},
                data_source=DataSource.SYNTHETIC,
                verification_status=VerificationStatus.UNVERIFIED,
            ),
            ProjectEvidence(
                id=demo_uuid("ev-002-photo"),
                project_id=demo_002.id,
                evidence_type=EvidenceType.PHOTO,
                storage_uri="data/synthetic/evidence/demo002_site.txt",
                captured_at=now,
                extra_metadata={"perceptual_hash": "SYNTH-HASH-A1", "note": "synthetic placeholder"},
                data_source=DataSource.SYNTHETIC,
                verification_status=VerificationStatus.UNVERIFIED,
            ),
        ]
    )
    db.commit()

    assess_project(db, demo_001.id)
    assess_project(db, demo_003.id)
    return {"status": "seeded", "demo_project": "DEMO-001"}


if __name__ == "__main__":
    from app.database.connection import SessionLocal

    session = SessionLocal()
    try:
        print(seed_if_empty(session))
    finally:
        session.close()
