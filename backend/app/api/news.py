from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import News, Source
from ..schemas import NewsOut

router = APIRouter(tags=["news"])


@router.get("/news", response_model=list[NewsOut])
async def list_news(
    category: str | None = None,
    q: str | None = Query(default=None, min_length=1, max_length=200),
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=100000),
    db: AsyncSession = Depends(get_session),
) -> list[NewsOut]:
    stmt = (
        select(News, Source.name)
        .join(Source, Source.id == News.source_id)
        .where(News.is_active.is_(True))
    )

    if category:
        stmt = stmt.where(News.category == category)

    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(News.title.ilike(like))

    stmt = stmt.order_by(desc(News.published_at)).limit(limit).offset(offset)

    res = await db.execute(stmt)
    rows = res.all()

    out: list[NewsOut] = []
    for news, source_name in rows:
        item = NewsOut.model_validate(news)
        item.source_name = source_name
        out.append(item)
    return out
