from typing import List

from fastapi import (
    APIRouter, Request,
    Depends, Query, Form
)
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import app_config
from src.api.dependencies import get_async_session
from src.repository import crud
from src.models.schemas import (
    AccountResponse, NodeElement,
    AccountEditedResponse, PageResponse,
    PageOrderBy, OrderMode
)
from src.utils.html import (
    node_to_html, parse_nodes_from_str,
    formatting_nodes, get_preview_from_nodes
)
from src.utils import coders
from src.utils.validation import is_can_edit
from src.exceptions import (
    AccountNotFoundException,
    PageEditForbiddenException,
    PageNotFoundException
)


limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api", tags=["api"])


@router.get("/createAccount", response_model=AccountResponse)
@limiter.limit(app_config.LIMIT_CREATE_ACCOUNT)
async def create_account(
    request: Request,
    short_name: str = Query(max_length=32),
    author_name: str = Query(max_length=128, default="Anonymous"),
    author_url: str = Query(max_length=512, default=""),
    db: AsyncSession = Depends(get_async_session)
):
    """ Create Account """
    account = await crud.create_account(db, coders.text_to_translit(short_name), author_name, author_url)
    return AccountResponse(
        short_name=account.short_name,
        author_name=account.author_name,
        author_url=account.author_url,
        access_token=account.token
    )


@router.get("/resetToken", response_model=AccountResponse)
@limiter.limit(app_config.LIMIT_RESET_TOKEN)
async def reset_token(
    request: Request,
    token: str,
    db: AsyncSession = Depends(get_async_session)
):
    """ Reset Token """
    try:
        account = await crud.get_account(db, token)
        pages = await crud.get_account_page_count(db, token)
        account.token = coders.generate_token()
        await db.commit()
        await db.refresh(account)
        
    except AccountNotFoundException:
        raise HTTPException(401, "Unauthorized")
    
    return AccountResponse(
        short_name=account.short_name,
        author_name=account.author_name,
        author_url=account.author_url,
        access_token=account.token,
        page_count=pages,
        views=(await crud.get_account_pages_views(db, account.id))
    )


@router.get("/editAccountInfo", response_model=AccountEditedResponse)
@limiter.limit(app_config.LIMIT_EDIT_ACCOUNT)
async def edit_account_info(
    request: Request,
    token: str,
    short_name: str | None = Query(None, max_length=32),
    author_name: str | None = Query(None, max_length=128),
    author_url: str | None = Query(None, max_length=512),
    db: AsyncSession = Depends(get_async_session)
):
    """ Edit Account Info """
    try:
        account = await crud.edit_account_info(
            db, token,
            coders.text_to_translit(short_name) if short_name else None,
            author_name, author_url
        )
        await db.refresh(account)
    except AccountNotFoundException:
        raise HTTPException(401, "Unauthorized")
    
    return AccountEditedResponse(
        short_name=account.short_name,
        author_name=account.author_name,
        author_url=account.author_url
    )
    

@router.get("/getAccountInfo", response_model=AccountResponse)
@limiter.limit(app_config.LIMIT_GET_ACCOUNT)
async def get_account_info(
    request: Request,
    token: str,
    db: AsyncSession = Depends(get_async_session)
):
    """ Get Account Info """
    try:
        account = await crud.get_account(db, token)
        pages = await crud.get_account_page_count(db, token)
    except AccountNotFoundException:
        raise HTTPException(401, "Unauthorized")
    
    return AccountResponse(
        short_name=account.short_name,
        author_name=account.author_name,
        author_url=account.author_url,
        access_token=account.token,
        page_count=pages,
        views=(await crud.get_account_pages_views(db, account.id))
    )
    

@router.post("/createPage", response_model=PageResponse)
@limiter.limit(app_config.LIMIT_CREATE_PAGE)
async def create_page(
    request: Request,
    token: str = Form(),
    content: str = Form(
        description="""This abstract object represents a DOM Node.
                    It can be a String which represents a DOM text node or a NodeElement object""",
        example='["Hello ", {"tag": "b", "children": ["World", {"tag": "i", "children": ["!"]} ]} ]',
        max_length=1048576
    ),
    title: str = Form(min_length=1, max_length=256),
    author_name: str | None = Form(None, max_length=128),
    author_url: str | None = Form(None, max_length=512),
    return_content: bool = Form(True),
    db: AsyncSession = Depends(get_async_session)
):
    """ Create Page """
    nodes = parse_nodes_from_str(content)
    content_list = formatting_nodes(nodes)
    uri = coders.text_to_translit(title).lower()
    
    try:
        account = await crud.get_account(db, token)
        page = await crud.create_page(
            db, token,
            nodes=coders.json_dumps(content_list),
            title=title,
            uri=uri,
            author_name=author_name,
            author_url=author_url
        )
    except AccountNotFoundException:
        raise HTTPException(401, "Unauthorized")
    
    page_response = PageResponse(
        path=page.page_uri,
        author_name=page.author_name,
        author_url=page.author_url,
        title=page.title,
        image_url=get_preview_from_nodes(nodes),
        can_edit=(account.id == page.account_id),
        created=page.created
    )
    if return_content:
        page_response.content = nodes

    return page_response


@router.post("/editPage/{page_uri}", response_model=PageResponse)
@limiter.limit(app_config.LIMIT_EDIT_PAGE)
async def edit_page(
    request: Request,
    page_uri: str,
    token: str = Form(),
    content: str | None = Form(
        None,
        description="""This abstract object represents a DOM Node.
                    It can be a String which represents a DOM text node or a NodeElement object""",
        example='["Hello ", {"tag": "b", "children": ["World", {"tag": "i", "children": ["!"]} ]} ]',
        max_length=1048576
    ),
    title: str | None = Form(None, min_length=1, max_length=256),
    author_name: str | None = Form(None, max_length=128),
    author_url: str | None = Form(None, max_length=512),
    return_content: bool = Form(True),
    db: AsyncSession = Depends(get_async_session)
):
    """ Edit Page """
    if content is not None:
        nodes = parse_nodes_from_str(content)
        content_list = formatting_nodes(nodes)
    else:
        nodes, content_list = None, None
    
    try:
        account = await crud.get_account(db, token)
        views = await crud.get_page_views_count(db, page_uri)
        page = await crud.get_page(db, page_uri)

        if not is_can_edit(account, page):
            raise PageEditForbiddenException()
        
        page = await crud.edit_page(
            db, token,
            page_uri,
            nodes=coders.json_dumps(content_list) if content_list else None,
            title=title,
            author_name=author_name,
            author_url=author_url
        )
        await db.refresh(account)

    except AccountNotFoundException:
        raise HTTPException(401, "Unauthorized")
    except PageNotFoundException:
        raise HTTPException(404, "Not Found")
    except PageEditForbiddenException:
        raise HTTPException(403, "Forbidden")
    
    page_response = PageResponse(
        path=page.page_uri,
        author_name=page.author_name,
        author_url=page.author_url,
        title=page.title,
        image_url=get_preview_from_nodes(nodes),
        views=views,
        can_edit=is_can_edit(account, page),
        created=page.created
    )
    if return_content:
        page_response.content = nodes

    return page_response


@router.get("/deletePage/{page_uri}")
@limiter.limit(app_config.LIMIT_DELETE_PAGE)
async def delete_page(
    request: Request,
    page_uri: str,
    token: str,
    db: AsyncSession = Depends(get_async_session)
):
    """ Delete Page """
    try:
        account = await crud.get_account(db, token)
        page = await crud.get_page(db, page_uri)
        
        if not is_can_edit(account, page):
            raise PageEditForbiddenException()
        
        if not account.is_admin:
            page.is_deleted = True
            await db.commit()
        else:
            await db.delete(page)
            await db.commit()
        
    except AccountNotFoundException:
        raise HTTPException(401, "Unauthorized")
    except PageNotFoundException:
        raise HTTPException(404, "Not Found")
    except PageEditForbiddenException:
        raise HTTPException(403, "Forbidden")
    
    return {
        "ok": True
    }


@router.get("/getPage/{page_uri}", response_model=PageResponse)
@limiter.limit(app_config.LIMIT_GET_PAGE)
async def get_page(
    request: Request,
    page_uri: str,
    token: str | None = Query(None, max_length=128),
    return_content: bool = Query(True),
    db: AsyncSession = Depends(get_async_session)
):
    """ Get Page """
    
    account = None
    try:
        if token is not None:
            account = await crud.get_account(db, token)
        views = await crud.get_page_views_count(db, page_uri)
        page = await crud.get_page(db, page_uri)
        
    except AccountNotFoundException:
        raise HTTPException(401, "Unauthorized")
    except PageNotFoundException:
        raise HTTPException(404, "Not Found")
    
    nodes = parse_nodes_from_str(page.content)
    
    page_response = PageResponse(
        path=page.page_uri,
        author_name=page.author_name,
        author_url=page.author_url,
        title=page.title,
        image_url=get_preview_from_nodes(nodes),
        views=views,
        can_edit=is_can_edit(account, page),
        created=page.created
    )
    if return_content:
        page_response.content = nodes

    return page_response


@router.get("/getPages", response_model=List[PageResponse])
@limiter.limit(app_config.LIMIT_GET_PAGES)
async def get_pages(
    request: Request,
    token: str = Query(max_length=128),
    query: str = Query("", max_length=256, description="Filer by Title"),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    order_by: PageOrderBy = Query(PageOrderBy.DATE),
    order_mode: OrderMode = Query(OrderMode.DESC),
    db: AsyncSession = Depends(get_async_session)
):
    """ Get Pages """
    
    account = None
    try:
        account = await crud.get_account(db, token)
    except AccountNotFoundException:
        raise HTTPException(401, "Unauthorized")
    
    pages_response: List[PageResponse] = []
    pages = await crud.get_account_pages(
        db, account.id,
        query=query,
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_mode=order_mode
    )
    
    for page in pages:
        views = await crud.get_page_views_count(db, page.page_uri)
        nodes = parse_nodes_from_str(page.content)
        
        page_response = PageResponse(
            path=page.page_uri,
            author_name=page.author_name,
            author_url=page.author_url,
            title=page.title,
            image_url=get_preview_from_nodes(nodes),
            views=views,
            can_edit=is_can_edit(account, page),
            created=page.created
        )
        pages_response.append(page_response)

    return pages_response


@router.get("/addView/{page_uri}")
@limiter.limit(app_config.LIMIT_ADD_VIEW)
async def add_view(
    request: Request,
    page_uri: str,
    db: AsyncSession = Depends(get_async_session)
):
    """ Add view """
    
    try:
        page = await crud.get_page(db, page_uri)
    except PageNotFoundException:
        raise HTTPException(404, "Not Found")
    else:
        ip = request.client.host or "0.0.0.0"
        user_agent = request.headers.get("User-Agent", None)
        
        if user_agent is None:
            return HTTPException(403, "Your User-Agent is Forbidden")
        
        hashed_info = coders.calc_sha256(
            ip, user_agent,
            b64=True
        )
        
        try:
            await crud.add_view(
                db,
                ip=ip,
                hashed_info=hashed_info,
                page_id=page.id
            )
        except Exception:
            ...

    return {
        "ok": True
    }
