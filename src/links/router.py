from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import uuid4
from src.database import get_async_session
from src.links.schemas import LinkCreate, LinkResponse, StatsResponse, LinkAlias, ListLinkResponse, LinkPackCreate, LinkPackResponse
from typing import Optional, List
from src.models import User, Link
from src.auth.auth import fastapi_users, current_user
from datetime import datetime, timezone

router = APIRouter(
    prefix="/links",
    tags=["Links"]
)


def generate_short_link() -> str:
    return str(uuid4())[:6]


@router.post("/shorten", response_model=LinkResponse)
async def shorten_link(link: LinkCreate, db: AsyncSession = Depends(get_async_session),
                       user: Optional[User] = Depends(current_user)):
    short_link = generate_short_link()
    creator_id = user.id if user else None
    new_link = Link(
        original_url=link.original_url,
        short_link=short_link,
        creator_id=creator_id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    return new_link


@router.get("/search", response_model=LinkResponse)
async def search_links_by_original_url(original_url: str, db: AsyncSession = Depends(get_async_session)):
    res = await db.execute(select(Link).where(Link.original_url == original_url))
    link = res.scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="No link")
    return link


@router.get("/{short_code}", response_class=RedirectResponse)
async def redirect_link(short_code: str, db: AsyncSession = Depends(get_async_session)):
    res = await db.execute(select(Link).where(Link.short_link == short_code))
    link = res.scalars().first()
    if link is None:
        raise HTTPException(status_code=404, detail="No link")
    url = link.original_url
    link.clicks += 1
    link.last_used_at = datetime.now(timezone.utc)
    await db.commit()
    return RedirectResponse(url=url)


@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(short_code: str, db: AsyncSession = Depends(get_async_session),
    user: User = Depends(fastapi_users.current_user(active=True))):
    res = await db.execute(select(Link).where(Link.short_link == short_code))
    link = res.scalars().first()
    if link is None:
        raise HTTPException(status_code=404, detail="No link")
    if link.creator_id != user.id:
        raise HTTPException(status_code=403, detail="You can't delete this link")
    await db.delete(link)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{short_code}", response_model=LinkResponse)
async def update_link(short_code: str, link_update: LinkCreate, db: AsyncSession = Depends(get_async_session),
        user: User = Depends(fastapi_users.current_user(active=True))):
    res = await db.execute(select(Link).where(Link.short_link == short_code))
    link = res.scalars().first()
    if link is None:
        raise HTTPException(status_code=404, detail="No link")
    if link.creator_id != user.id:
        raise HTTPException(status_code=403, detail="You can't update this link")
    link.original_url = link_update.original_url
    await db.commit()
    await db.refresh(link)
    return link


@router.get("/{short_code}/stats", response_model=StatsResponse)
async def stats_link(short_code: str, db: AsyncSession = Depends(get_async_session)):
    res = await db.execute(select(Link).where(Link.short_link == short_code))
    link = res.scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="No link")
    return link


@router.post("/shorten/custom_alias", response_model=LinkResponse)
async def shorten_link_with_alias(link: LinkAlias, db: AsyncSession = Depends(get_async_session),
        user: Optional[User] = Depends(current_user)):
    res = await db.execute(select(Link).where(Link.short_link == link.custom_alias))
    if res.scalars().first():
        raise HTTPException(status_code=409, detail="Short link exists, create another")
    creator_id = user.id if user else None
    alias = Link(
        original_url=link.original_url,
        short_link=link.custom_alias,
        creator_id=creator_id,
        created_at=datetime.now(timezone.utc))
    db.add(alias)
    await db.commit()
    await db.refresh(alias)
    return alias


@router.get("/list/links", response_model=List[ListLinkResponse])
async def user_links(db: AsyncSession = Depends(get_async_session), user: Optional[User] = Depends(current_user)):
    if user is None:
        raise HTTPException(status_code=401, detail="You are not authorized")
    res = await db.execute(select(Link).where(Link.creator_id == user.id))
    links = res.scalars().all()
    return [ListLinkResponse(short_link=link.short_link, original_url=link.original_url) for link in links]


@router.post("/pack", response_model=List[LinkPackResponse])
async def pack_create_links(pack: LinkPackCreate, db: AsyncSession = Depends(get_async_session),
                            user: Optional[User] = Depends(current_user)):
    pack_links = []
    for url in pack.original_urls:
        for i in range(5):
            short_code = generate_short_link()
            res = await db.execute(select(Link).where(Link.short_link==short_code))
            link_in_db = res.scalars().first()
            if not link_in_db:
                break
        else:
            raise HTTPException(status_code=409, detail="Failed to create all new short links, try again")
        link = Link(
            original_url=url,
            short_link=short_code,
            creator_id=user.id if user else None,
            created_at=datetime.now(timezone.utc)
        )
        db.add(link)
        pack_links.append(link)
    await db.commit()
    return [LinkPackResponse(original_url=link.original_url, short_link=link.short_link) for link in pack_links]
