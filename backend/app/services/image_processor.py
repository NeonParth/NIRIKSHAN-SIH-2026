from __future__ import annotations

from typing import Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.database.models import Project, ProjectEvidence

def perceptual_hash_from_metadata(metadata: Optional[dict[str, Any]]) -> Optional[str]:
    if not metadata:
        return None
    value = metadata.get("perceptual_hash")
    if value is None:
        return None
    return str(value)


def hashes_equal(left: Optional[str], right: Optional[str]) -> bool:
    if not left or not right:
        return False
    return left == right

def get_image_similarity_signal(db: Session, project: Project) -> Optional[dict[str, Any]]:
    # For Phase 1, we look for any evidence hash that matches evidence in other projects
    for evidence in project.evidence:
        hash_val = perceptual_hash_from_metadata(evidence.extra_metadata)
        if not hash_val:
            continue

        # Find other evidence with the same hash
        matches = db.query(ProjectEvidence).filter(
            ProjectEvidence.extra_metadata["perceptual_hash"].astext == hash_val,
            ProjectEvidence.project_id != project.id
        ).first()

        if matches:
            return {
                "signal_code": "image_similarity",
                "observed_value": "Hash Match",
                "threshold": "Exact Match",
                "explanation": f"Image evidence matches evidence from another project (Evidence ID: {matches.id})",
                "source_reference": f"Evidence {matches.id}",
                "source_module": "image_processor"
            }
    return None
