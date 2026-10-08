import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.entrypoints.rest_api.routes import (
    auth_router,
    space_router,
    user_router,
    product_router,
    file_router,
)
from src.infrastructure.databases.postgresql.setup import setup as pg_setup


def create_app() -> FastAPI:
    app = FastAPI(
        title="ProductControl API",
        version="1.0.0",
        description="Sistema de controle de produtos e ativos",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    env = os.environ.get("APP_ENV", "development")
    if env in ("development", "testing"):
        pg_setup()

    app.include_router(auth_router)
    app.include_router(space_router)
    app.include_router(user_router)
    app.include_router(product_router)
    app.include_router(file_router)

    return app
