import pathlib
import logging
from typing import List

import decouple

ROOT_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.resolve()


class AppConfig:
    
    # meta info
    TITLE: str = "Telegraphy"
    DESCRIPTION: str = "An open-source alternative to Telegra.ph for simple and anonymous publishing."
    VERSION: str = "0.0.2"
    
    # startup
    APP_DEBUG: bool = decouple.config("APP_DEBUG", False, cast=bool)
    SQL_DEBUG: bool = decouple.config("SQL_DEBUG", False, cast=bool)
    API_DOCS: bool = decouple.config("API_DOCS", True, cast=bool)
    FRONTEND_ENABLED: bool = decouple.config("FRONTEND_ENABLED", True, cast=bool)
    ALLOWED_ORIGINS: str = decouple.config("ALLOWED_ORIGINS", "*", cast=str)
    
    # server options
    SERVER_HOST: str = decouple.config("SERVER_HOST", "0.0.0.0", cast=str)
    SERVER_PORT: int = decouple.config("SERVER_PORT", 8085, cast=int)
    SERVER_WORKERS: int = decouple.config("SERVER_WORKERS", 4, cast=int)
    
    # database
    DATABASE_URL: str = decouple.config("DB_URL", cast=str)
    DB_POOL_SIZE: int = decouple.config("DB_POOL_SIZE", 100, cast=int)
    DB_POOL_OVERFLOW: int = decouple.config("DB_POOL_OVERFLOW", 20, cast=int)
    DB_TIMEOUT: int = decouple.config("DB_TIMEOUT", 5, cast=int)
    
    # limits
    LIMIT_CREATE_ACCOUNT: str = decouple.config("LIMIT_CREATE_ACCOUNT", "3/second", cast=str)
    LIMIT_EDIT_ACCOUNT: str = decouple.config("LIMIT_EDIT_ACCOUNT", "100/second", cast=str)
    LIMIT_CREATE_PAGE: str = decouple.config("LIMIT_CREATE_PAGE", "5/second", cast=str)
    LIMIT_EDIT_PAGE: str = decouple.config("LIMIT_EDIT_PAGE", "10/second", cast=str)
    LIMIT_DELETE_PAGE: str = decouple.config("LIMIT_DELETE_PAGE", "50/second", cast=str)
    LIMIT_ADD_VIEW: str = decouple.config("LIMIT_ADD_VIEW", "1000/second", cast=str)
    LIMIT_RESET_TOKEN: str = decouple.config("LIMIT_RESET_TOKEN", "500/second", cast=str)
    LIMIT_GET_ACCOUNT: str = decouple.config("LIMIT_GET_ACCOUNT", "1000/second", cast=str)
    LIMIT_GET_PAGE: str = decouple.config("LIMIT_GET_PAGE", "2500/second", cast=str)
    LIMIT_GET_PAGES: str = decouple.config("LIMIT_GET_PAGES", "500/second", cast=str)
    
    # etc
    LOGGING_LEVEL: int = getattr(
        logging, 
        decouple.config("LOGGING_LEVEL", "INFO", cast=str).upper(), 
        logging.INFO
    )


app_config = AppConfig()
