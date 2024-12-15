from pydantic import Field

from . import TelegraphyObj


class AccountResponse(TelegraphyObj):
    """
    This object represents a Telegraph account.
    """
    short_name: str = Field(max_length=32)
    author_name: str = Field(max_length=128)
    author_url: str = Field(max_length=512)
    access_token: str = Field(max_length=128)
    page_count: int = Field(default=0)
    views: int = Field(default=0)


class AccountEditedResponse(TelegraphyObj):
    """
    This object represents a Telegraph account.
    After edit.
    """
    short_name: str = Field(max_length=32)
    author_name: str = Field(max_length=128)
    author_url: str = Field(max_length=512)
