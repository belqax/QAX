from fastapi import FastAPI

from .api.news import router as news_router

app = FastAPI(title="News Aggregator")

app.include_router(news_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
