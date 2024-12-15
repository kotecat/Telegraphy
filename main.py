import logging
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from sqlalchemy import select

from src.api.routes import api, frontend
from src.config import app_config
from src.repository.database import async_db
from src.models.entities import Base, Account
from src.repository import crud


logging.basicConfig(level=app_config.LOGGING_LEVEL)
logger = logging.getLogger(__name__)


async def lifespan(app: FastAPI) -> AsyncGenerator:
    async with async_db.async_session() as db:
        logger.info("Getting admin token...")
        r = await db.execute(
            select(Account)
            .where(Account.is_admin == True)
            .limit(1)
        )
        
        acc = r.scalars().one_or_none()
        if not acc:
            logger.info("Creating new Admin")
            acc = await crud.create_account(db, "Admin", "Admin", "...")
            acc.is_admin = True
            await db.commit()
            await db.refresh(acc)
            
        logger.info("\n")
        logger.info("=-=-=-=-=-=-=")
        logger.info(f"ADMIN TOKEN: {acc.token}")
        logger.info("=-=-=-=-=-=-=\n")
    yield
    logger.info("Stopping...")


def init_application() -> FastAPI:
    app = FastAPI(
        debug=app_config.APP_DEBUG,
        title=app_config.TITLE,
        description=app_config.TITLE,
        docs_url='/docs' if app_config.API_DOCS else None,
        redoc_url='/redoc' if app_config.API_DOCS else None,
        lifespan=lifespan
    )
    
    app.include_router(api.router)
    
    if (app_config.FRONTEND_ENABLED):
        app.include_router(frontend.router)
        app.mount("/static", frontend.static_router)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.ALLOWED_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            content={
                "detail": f"Too Many Requests. Please try again later.",
                "limit": str(exc.detail)
            },
            status_code=429,
        )
    
    return app


telegraphy_app: FastAPI = init_application()


if __name__ == "__main__": 
    uvicorn.run(
        "main:telegraphy_app",
        host=app_config.SERVER_HOST,
        port=app_config.SERVER_PORT,
        reload=app_config.APP_DEBUG,
        workers=app_config.SERVER_WORKERS,
        log_level=app_config.LOGGING_LEVEL
    )
