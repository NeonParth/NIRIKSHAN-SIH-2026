from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Set
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.database.models.entities import Contractor, ContractAward, Tender


@dataclass(frozen=True)
class NexusConnection:
    entity_a: UUID
    entity_b: UUID
    connection_type: str  # "SHARED_PAN", "SHARED_GSTIN", "SHARED_EMAIL", "SHARED_PHONE", "SHARED_ADDRESS", "CORPORATE_HIERARCHY"
    confidence: float
    evidence: str


class NexusService:
    """
    Service for detecting hidden relationships and collusion patterns
    between contractors (Vendor Nexus Analysis).
    """

    def __init__(self, db: Session):
        self.db = db

    def find_nexus_for_contractor(self, contractor_id: UUID) -> List[NexusConnection]:
        """
        Identify all other contractors linked to the given contractor through shared attributes.
        """
        contractor = self.db.get(Contractor, contractor_id)
        if not contractor:
            return []

        connections = []

        # 1. Check for shared attributes
        # We look for other contractors who share any of the identifying fields
        filters = []
        if contractor.pan_number:
            filters.append(Contractor.pan_number == contractor.pan_number)
        if contractor.gstin:
            filters.append(Contractor.gstin == contractor.gstin)
        if contractor.email:
            filters.append(Contractor.email == contractor.email)
        if contractor.phone:
            filters.append(Contractor.phone == contractor.phone)
        if contractor.address_hash:
            filters.append(Contractor.address_hash == contractor.address_hash)

        if filters:
            stmt = select(Contractor).where(
                or_(*filters),
                Contractor.id != contractor_id
            )
            matches = self.db.execute(stmt).scalars().all()

            for match in matches:
                connections.append(self._determine_connection_type(contractor, match))

        # 2. Check Corporate Hierarchy
        # Same parent company
        if contractor.parent_company_id:
            stmt = select(Contractor).where(
                Contractor.parent_company_id == contractor.parent_company_id,
                Contractor.id != contractor_id
            )
            siblings = self.db.execute(stmt).scalars().all()
            for sibling in siblings:
                connections.append(NexusConnection(
                    entity_a=contractor_id,
                    entity_b=sibling.id,
                    connection_type="CORPORATE_HIERARCHY",
                    confidence=1.0,
                    evidence=f"Both belong to parent company {contractor.parent_company_id}"
                ))

        # Is this contractor a parent of others?
        stmt = select(Contractor).where(
            Contractor.parent_company_id == contractor_id
        )
        children = self.db.execute(stmt).scalars().all()
        for child in children:
            connections.append(NexusConnection(
                entity_a=contractor_id,
                entity_b=child.id,
                connection_type="CORPORATE_HIERARCHY",
                confidence=1.0,
                evidence=f"Contractor {contractor.name} is the parent of {child.name}"
            ))

        return connections

    def detect_tender_collusion(self, tender_id: UUID) -> List[NexusConnection]:
        """
        Check if any winning bidders or participants in a specific tender share a nexus.
        """
        # Get all contractors awarded for this tender
        stmt = select(ContractAward).where(ContractAward.tender_id == tender_id)
        awards = self.db.execute(stmt).scalars().all()
        contractors = [award.contractor for award in awards]

        nexus_alerts = []
        for i in range(len(contractors)):
            for j in range(i + 1, len(contractors)):
                c1 = contractors[i]
                c2 = contractors[j]

                conn = self._determine_connection_type(c1, c2)
                if conn:
                    nexus_alerts.append(conn)

        return nexus_alerts

    def _determine_connection_type(self, c1: Contractor, c2: Contractor) -> NexusConnection | None:
        """
        Determine the strongest link between two contractors.
        """
        if c1.pan_number and c1.pan_number == c2.pan_number:
            return NexusConnection(c1.id, c2.id, "SHARED_PAN", 1.0, "Same PAN number")
        if c1.gstin and c1.gstin == c2.gstin:
            return NexusConnection(c1.id, c2.id, "SHARED_GSTIN", 1.0, "Same GSTIN")
        if c1.email and c1.email == c2.email:
            return NexusConnection(c1.id, c2.id, "SHARED_EMAIL", 0.8, "Same email address")
        if c1.phone and c1.phone == c2.phone:
            return NexusConnection(c1.id, c2.id, "SHARED_PHONE", 0.8, "Same phone number")
        if c1.address_hash and c1.address_hash == c2.address_hash:
            return NexusConnection(c1.id, c2.id, "SHARED_ADDRESS", 0.7, "Shared physical address hash")

        return None
