from __future__ import annotations

import asyncio
import logging

from app.config import settings
from app.db import SessionFactory
from app.services.rss_fetcher import fetch_all

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fetch_loop")


async def main() -> None:
    interval = int(settings.fetch_interval_seconds)
    max_items = int(settings.fetch_max_items_per_feed)

    logger.info("Fetcher started interval_seconds=%s max_items_per_feed=%s", interval, max_items)

    while True:
        try:
            async with SessionFactory() as db:
                added = await fetch_all(db=db, max_items_per_feed=max_items)
            logger.info("Fetcher cycle complete added=%s", added)
        except Exception:
            logger.exception("Fetcher cycle failed")

        await asyncio.sleep(interval)


if __name__ == "__main__":
    asyncio.run(main())
