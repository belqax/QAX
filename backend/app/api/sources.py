from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import Source
from ..schemas import SourceCreate, SourceOut

router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=list[SourceOut])
async def list_sources(
    db: AsyncSession = Depends(get_session),
) -> list[SourceOut]:
    stmt = select(Source).order_by(Source.id.asc())
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.post("/sources", response_model=SourceOut, status_code=status.HTTP_201_CREATED)
async def create_source(
    payload: SourceCreate,
    db: AsyncSession = Depends(get_session),
) -> SourceOut:
    # Уникальность по feed_url
    exists = await db.execute(select(Source).where(Source.feed_url == str(payload.feed_url)))
    if exists.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="source_with_same_feed_url_already_exists",
        )

    src = Source(
        name=payload.name,
        feed_url=str(payload.feed_url),
        category=payload.category,
        is_active=payload.is_active,
    )
    db.add(src)
    await db.commit()
    await db.refresh(src)
    return src


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: int,
    db: AsyncSession = Depends(get_session),
) -> None:
    res = await db.execute(select(Source).where(Source.id == source_id))
    src = res.scalar_one_or_none()
    if not src:
        raise HTTPException(status_code=404, detail="source_not_found")

    await db.delete(src)
    await db.commit()
