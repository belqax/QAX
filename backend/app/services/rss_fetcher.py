from __future__ import annotations

import datetime as dt
import logging
from typing import Optional

import feedparser
from dateutil import tz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import News, Source

logger = logging.getLogger("rss_fetcher")


def _parse_published(entry: dict) -> dt.datetime:
    published = entry.get("published_parsed")
    if published:
        # published_parsed обычно в UTC
        return dt.datetime(*published[:6], tzinfo=dt.timezone.utc)

    # Иногда есть updated_parsed
    updated = entry.get("updated_parsed")
    if updated:
        return dt.datetime(*updated[:6], tzinfo=dt.timezone.utc)

    return dt.datetime.now(dt.timezone.utc)


async def fetch_one_source(
    *,
    db: AsyncSession,
    source: Source,
    max_items: int,
) -> int:
    parsed = feedparser.parse(source.feed_url)
    added = 0

    entries = list(parsed.entries)[:max_items]

    for e in entries:
        url: Optional[str] = e.get("link")
        title: Optional[str] = e.get("title")

        if not url or not title:
            continue

        exists = await db.execute(select(News.id).where(News.url == url))
        if exists.scalar_one_or_none() is not None:
            continue

        news = News(
            source_id=source.id,
            category=source.category,
            title=title.strip(),
            url=url.strip(),
            summary=(e.get("summary") or None),
            published_at=_parse_published(e),
            is_active=True,
        )
        db.add(news)
        added += 1

    if added > 0:
        await db.commit()

    return added


async def fetch_all(
    *,
    db: AsyncSession,
    max_items_per_feed: int,
) -> int:
    res = await db.execute(select(Source).where(Source.is_active.is_(True)).order_by(Source.id.asc()))
    sources = list(res.scalars().all())

    total_added = 0
    for src in sources:
        try:
            added = await fetch_one_source(db=db, source=src, max_items=max_items_per_feed)
            total_added += added
            logger.info("Fetched source=%s added=%s", src.feed_url, added)
        except Exception:
            logger.exception("Fetch failed for source=%s", src.feed_url)

    return total_added
