from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class LinkCreate(BaseModel):
    original_url: str


class LinkResponse(BaseModel):
    id: int
    original_url: str
    short_link: str
    created_at: datetime
    clicks: int
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    creator_id: Optional[int] = None


class StatsResponse(BaseModel):
    original_url: str
    created_at: datetime
    clicks: int
    last_used_at: Optional[datetime] = None


class LinkAlias(LinkCreate):
    custom_alias: str


class ListLinkResponse(BaseModel):
    short_link: str
    original_url: str

class LinkPackCreate(BaseModel):
    original_urls: List[str]

class LinkPackResponse(BaseModel):
    original_url: str
    short_link: str
