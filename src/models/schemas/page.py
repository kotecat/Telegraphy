from typing import List
from datetime import datetime, UTC
from enum import Enum

from pydantic import Field

from . import TelegraphyObjExcludeNone, NodeElement


class PageResponse(TelegraphyObjExcludeNone):
    """
    This object represents a Telegraph account.
    """
    path: str = Field(max_length=1024)
    author_name: str = Field(max_length=128)
    author_url: str = Field(max_length=512, default="")
    title: str = Field(max_length=256)
    image_url: str | None = Field(default="")
    can_edit: bool = Field(default=False)
    views: int = Field(default=0)
    created: datetime = Field(default=datetime.now(UTC))
    content: List[NodeElement | str] = Field(default=[])
    html_content: str = Field(default="")


class PageOrderBy(Enum):
    TITLE: str = "title"
    VIEWS: str = "views"
    DATE: str = "date"
