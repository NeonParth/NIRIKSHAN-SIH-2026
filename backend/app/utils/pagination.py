from __future__ import annotations

from fastapi import Query


def pagination_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> tuple[int, int]:
    return page, page_size


def page_offset(page: int, page_size: int) -> int:
    return (page - 1) * page_size
