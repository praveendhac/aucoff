"""Cursor pagination shared by list endpoints (api-contract.md section 2: `limit`, `cursor`).

The cursor is opaque to clients. These helpers page over an in-memory sequence; the database-backed
implementations will keep the same request and response shape.
"""

import base64
import binascii
from typing import Annotated, Literal

from fastapi import HTTPException, Query
from pydantic import BaseModel, Field

DataSource = Literal["synthetic", "catalogue", "assessments"]


class Page[T](BaseModel):
    items: list[T]
    next_cursor: str | None = Field(
        description="Pass as `cursor` for the next page; null at the end."
    )
    data_source: DataSource = Field(
        description="`synthetic` marks demo rows that are not real results."
    )


Limit = Annotated[int, Query(ge=1, le=100, description="Page size (default 25, maximum 100).")]
Cursor = Annotated[str | None, Query(description="Opaque cursor from a previous page.")]


def _decode(cursor: str | None) -> int:
    if not cursor:
        return 0
    try:
        offset = int(base64.urlsafe_b64decode(cursor.encode()).decode())
    except (ValueError, binascii.Error) as exc:
        raise HTTPException(status_code=400, detail="invalid cursor") from exc
    if offset < 0:
        raise HTTPException(status_code=400, detail="invalid cursor")
    return offset


def paginate[T](rows: list[T], limit: int, cursor: str | None) -> tuple[list[T], str | None]:
    start = _decode(cursor)
    end = start + limit
    nxt = base64.urlsafe_b64encode(str(end).encode()).decode() if end < len(rows) else None
    return rows[start:end], nxt
