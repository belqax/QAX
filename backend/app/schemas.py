from __future__ import annotations

import datetime as dt
from pydantic import BaseModel, Field, HttpUrl


class SourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    feed_url: HttpUrl
    category: str = Field(default="general", min_length=1, max_length=64)
    is_active: bool = True


class SourceOut(BaseModel):
    id: int
    name: str
    feed_url: str
    category: str
    is_active: bool
    created_at: dt.datetime

    class Config:
        from_attributes = True


class NewsOut(BaseModel):
    id: int
    source_id: int
    category: str
    title: str
    url: str
    summary: str | None
    published_at: dt.datetime
    created_at: dt.datetime

    source_name: str | None = None

    class Config:
        from_attributes = True
