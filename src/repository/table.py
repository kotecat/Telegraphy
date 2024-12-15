import typing

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class DBTable(DeclarativeBase):
    metadata: MetaData = MetaData()
    

Base: typing.Type[DeclarativeBase] = DBTable
