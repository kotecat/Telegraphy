from typing import List

from sqlalchemy import select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import (
    NoResultFound,
    IntegrityError
)

from src.utils import coders
from src.utils import html
from src.models.schemas import (
    PageOrderBy, OrderMode
)
from src.models.entities import (
    Account, Page, PageView
)
from src.exceptions import (
    AccountNotFoundException,
    PageNotFoundException
)


async def create_account(
    db: AsyncSession,
    short_name: str,
    author_name: str,
    author_url: str
) -> Account:
    account = Account(
        short_name=short_name,
        author_name=author_name,
        author_url=author_url,
        token=coders.generate_token()
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    
    return account


async def get_account(
    db: AsyncSession,
    token: str,
    raise_e: bool = True
) -> Account | None:
    result = await db.execute(
        select(Account)
        .where(Account.token == token)
    )
    try:
        account = result.scalars().one()
    except NoResultFound:
        account = None
    
    if raise_e and account is None:
        raise AccountNotFoundException()
    
    return account


async def get_page(
    db: AsyncSession,
    page_uri: str,
    raise_e: bool = True,
    raise_is_del: bool = True
) -> Page | None:
    result = await db.execute(
        select(Page)
        .where(Page.page_uri.ilike(page_uri))
    )
    try:
        page = result.scalars().one()
    except NoResultFound:
        page = None
    
    if raise_e and (
        (page is None) or (raise_is_del and page.is_deleted)
    ):
        raise PageNotFoundException()
    
    return page


async def edit_account_info(
    db: AsyncSession,
    token: str,
    short_name: str | None,
    author_name: str | None,
    author_url: str | None
) -> Account:
    account = await get_account(db, token)
    
    account.short_name = short_name or account.short_name
    account.author_name = author_name or account.author_name
    account.author_url = author_url or account.author_url
    
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        await db.refresh(account)
    
    return account


async def get_account_page_count(
    db: AsyncSession,
    token: str
) -> int:
    account = await get_account(db, token)

    result = await db.execute(
        select(func.count())
        .select_from(Page)
        .where(Page.account_id == account.id)
    )
    count = result.scalar_one_or_none() or 0
    
    return count


async def get_account_pages(
    db: AsyncSession,
    acc_id: int,
    query: str,
    limit: int = 10,
    offset: int = 0,
    order_by: PageOrderBy = PageOrderBy.DATE,
    order_mode: OrderMode = OrderMode.DESC,
    hide_is_del: bool = True
) -> List[Page]:
    stmt = (
        select(Page)
        .where(Page.account_id == acc_id)
        .where(Page.title.ilike(f"%{query.lower()}%"))
    )
    
    if hide_is_del:
        stmt = (
            stmt
            .where(Page.is_deleted == False)
        )
    
    order_func = desc if order_mode == OrderMode.DESC else asc
    
    if order_by == PageOrderBy.DATE:
        stmt = stmt.order_by(order_func(Page.created))
        
    elif order_by == PageOrderBy.TITLE:
        stmt = stmt.order_by(order_func(Page.title))
        
    elif order_by == PageOrderBy.VIEWS:
        stmt = (
            stmt.outerjoin(PageView, Page.id == PageView.page_id)
            .group_by(Page.id)
            .order_by(order_func(func.count(PageView.page_id)))
        )
    
    stmt = stmt.limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    pages = result.scalars().all()
    
    return pages


async def get_account_pages_views(
    db: AsyncSession,
    acc_id: int,
    hide_is_del: bool = True
) -> int:
    stmt = (
        select(func.count(PageView.page_id))
        .select_from(PageView)
        .join(Page, Page.id == PageView.page_id)
        .filter(Page.account_id == acc_id)
    )
    
    if hide_is_del:
        stmt = (
            stmt
            .filter(Page.is_deleted == False)
        )
    
    result = await db.execute(stmt)
    count = result.scalar_one_or_none() or 0
    
    return count


async def get_page_views_count(
    db: AsyncSession,
    page_uri: str
) -> int:
    page = await get_page(db, page_uri, raise_is_del=False)

    result = await db.execute(
        select(func.count())
        .select_from(PageView)
        .where(PageView.page_id == page.id)
    )
    count = result.scalar_one_or_none() or 0
    
    return count


async def create_page(
    db: AsyncSession,
    token: str,
    nodes: str,
    title: str,
    uri: str,
    author_name: str | None,
    author_url: str | None
) -> Page:
    account = await get_account(db, token)
    
    acc_id = account.id
    author_name = author_name or account.author_name
    author_url = author_url or account.author_url
    uri = uri.lower().strip()
    
    seq = 0
    while True:
        seq += 1
        slug = "-" + coders.create_slug(seq)
        
        page = Page(
            page_uri=f"{uri[:255 - len(slug)]}{slug}",
            title=title,
            author_name=author_name,
            author_url=author_url,
            account_id=acc_id,
            content=nodes
        )
        try:
            db.add(page)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            continue
        else:
            await db.refresh(page)
            return page


async def edit_page(
    db: AsyncSession,
    token: str,
    page_uri: str,
    nodes: str | None,
    title: str | None,
    author_name: str | None,
    author_url: str | None
) -> Page:
    page = await get_page(db, page_uri)
    
    page.author_name = author_name or page.author_name
    page.author_url = author_url or page.author_url
    page.title = title or page.title
    page.content = nodes or page.content
    
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
    finally:
        await db.refresh(page)
    
    return page


async def add_view(
    db: AsyncSession,
    ip: str,
    hashed_info: str,
    page_id: int
) -> PageView | None:
    page_view = PageView(
        ip=ip,
        user_agent_hash=hashed_info,
        page_id=page_id
    )
    try:
        db.add(page_view)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return

    await db.refresh(page_view)
    return page_view
