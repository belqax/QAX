from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db import get_session
from ..models import News

router = APIRouter(prefix="/news", tags=["news"])


@router.get("")
async def list_news(
    category: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_session),
):
    stmt = select(News).where(News.is_active.is_(True))

    if category:
        stmt = stmt.where(News.category == category)

    stmt = stmt.order_by(News.published_at.desc()).limit(limit)

    result = await db.execute(stmt)
    return result.scalars().all()
