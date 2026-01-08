from __future__ import annotations

from fastapi import FastAPI

from .api.news import router as news_router
from .api.sources import router as sources_router

app = FastAPI(title="QAX")

app.include_router(news_router)
app.include_router(sources_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
