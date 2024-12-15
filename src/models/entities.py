import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Integer, DateTime,
    ForeignKey, PrimaryKeyConstraint, 
    func, Boolean
)

from src.repository.table import Base


class Account(Base):
    __tablename__ = "account"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    short_name: Mapped[str] = mapped_column(String(32), default="MrCat")
    author_name: Mapped[str] = mapped_column(String(128), default="MrAnonymous")
    author_url: Mapped[str] = mapped_column(String(512), default="")
    token: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, server_default="f", default=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Page(Base):
    __tablename__ = "page"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    page_uri: Mapped[str] = mapped_column(String(512), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    author_name: Mapped[str] = mapped_column(String(128), nullable=False)
    author_url: Mapped[str] = mapped_column(String(512), default="")
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"))
    content: Mapped[str] = mapped_column(String(1048576), default="")
    is_deleted: Mapped[bool] = mapped_column(Boolean, server_default="f", default=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    account: Mapped["Account"] = relationship(
        "Account",
        lazy="joined"
    )


class PageView(Base):
    __tablename__ = "page_view"

    ip: Mapped[str] = mapped_column(String(64), nullable=False)
    user_agent_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    page_id: Mapped[int] = mapped_column(ForeignKey("page.id", ondelete="CASCADE", onupdate="CASCADE"))
    time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        PrimaryKeyConstraint("ip", "user_agent_hash", "page_id", name="pr__ip__user_agent_hash__page_id"),
    )
    
    page: Mapped["Page"] = relationship(
        "Page",
        lazy="joined"
    )
