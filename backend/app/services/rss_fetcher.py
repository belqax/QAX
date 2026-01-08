import feedparser
import datetime as dt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models import News


async def fetch_rss(
    *,
    db: AsyncSession,
    feed_url: str,
    source: str,
    category: str,
) -> int:
    parsed = feedparser.parse(feed_url)
    added = 0

    for entry in parsed.entries:
        url = entry.get("link")
        title = entry.get("title")

        if not url or not title:
            continue

        exists = await db.execute(
            select(News).where(News.url == url)
        )
        if exists.scalar_one_or_none():
            continue

        published = entry.get("published_parsed")
        published_at = (
            dt.datetime(*published[:6], tzinfo=dt.timezone.utc)
            if published else dt.datetime.now(dt.timezone.utc)
        )

        news = News(
            title=title,
            url=url,
            source=source,
            category=category,
            summary=entry.get("summary"),
            published_at=published_at,
        )
        db.add(news)
        added += 1

    await db.commit()
    return added
