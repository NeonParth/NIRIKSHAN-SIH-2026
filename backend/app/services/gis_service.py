from __future__ import annotations

from typing import Optional, Any
from uuid import UUID

from geoalchemy2.shape import to_shape
from geoalchemy2.types import Geography
from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session

from app.database.models import Project
from app.database.schemas.api import GeoPoint

def point_wkt(longitude: float, latitude: float) -> str:
    return f"POINT({longitude} {latitude})"


def geometry_to_point(location) -> Optional[GeoPoint]:
    if location is None:
        return None
    shape = to_shape(location)
    return GeoPoint(longitude=float(shape.x), latitude=float(shape.y))


def find_nearby_projects(
    db: Session,
    project_id: UUID,
    location,
    meters: float,
) -> list[tuple[Project, float]]:
    if location is None:
        return []
    shape = to_shape(location)
    project_geog = cast(Project.location, Geography())
    origin_geog = cast(func.ST_SetSRID(func.ST_MakePoint(shape.x, shape.y), 4326), Geography())
    stmt = (
        select(Project, func.ST_Distance(project_geog, origin_geog))
        .where(Project.id != project_id)
        .where(Project.location.is_not(None))
        .where(func.ST_DWithin(project_geog, origin_geog, meters))
    )
    return [(row[0], float(row[1])) for row in db.execute(stmt).all()]

def get_proximity_signal(db: Session, project: Project, threshold_meters: float = 500.0) -> Optional[dict[str, Any]]:
    if project.location is None:
        return None

    nearby = find_nearby_projects(db, project.id, project.location, threshold_meters)
    if not nearby:
        return None

    closest_project, distance = nearby[0]
    return {
        "signal_code": "duplicate_proximity",
        "observed_value": f"{distance:.1f}m",
        "threshold": f"<{threshold_meters}m",
        "explanation": f"Project is within {threshold_meters}m of another project ({closest_project.name})",
        "source_reference": f"Project {closest_project.code}",
        "source_module": "gis_service"
    }
