from datetime import datetime, UTC
from os import path

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.routing import Router
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository import crud
from src.api.dependencies import get_async_session
from src.exceptions import PageNotFoundException
from src.models.schemas import (
    PageResponse
)
from src.utils.html import (
    node_to_html,
    parse_nodes_from_str,
    get_preview_from_nodes
)


front_path = path.join("src", "frontend")

router = APIRouter(tags=["frontend"])
static_router = Router()

static_router.mount("/", StaticFiles(directory=path.join(front_path, "static")), name="static")
templates = Jinja2Templates(directory=path.join(front_path, "templates"))


@router.get("/")
async def get_new_page_front(request: Request):
    page_response = PageResponse(
        path="",
        author_name="author",
        author_url="",
        title="Title...",
        image_url="",
        can_edit=False,
        created=datetime.now(tz=UTC),
        html_content=""
    ).model_dump(mode="python", exclude_defaults=True)
    
    return templates.TemplateResponse(
        request=request, name="view_page.html", context=page_response
    )
    

@router.get("/auth")
async def get_auth_page_front(request: Request):
    return templates.TemplateResponse(
        request=request, name="auth_page.html", context={}
    )


@router.get("/account")
async def get_account_page_front(request: Request):
    return templates.TemplateResponse(
        request=request, name="account_page.html", context={}
    )


@router.get("/{page_uri}", response_class=HTMLResponse)
async def get_page_front(
    request: Request,
    page_uri: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        page = await crud.get_page(db, page_uri)
    except PageNotFoundException:
        return templates.TemplateResponse(
            request=request, name="error_page.html", context={
                "title": f"404 - Not Found",
                "err_description": "",
                "button_text": "Create New"
            },
            status_code=404
        )
        
    nodes = parse_nodes_from_str(page.content)
    
    page_response = PageResponse(
        path=page.page_uri,
        author_name=page.author_name,
        author_url=page.author_url,
        title=page.title,
        image_url=get_preview_from_nodes(nodes) or "",
        can_edit=False,
        created=page.created,
        html_content=node_to_html(nodes)
    ).model_dump(mode="python", exclude_defaults=True)
    
    return templates.TemplateResponse(
        request=request, name="view_page.html", context=page_response
    )
