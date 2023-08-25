from fastapi import FastAPI

from src.api import health
from src.api.handlers import register_error_handling
from src.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(**settings.fastapi_kwargs)
    app.include_router(health.router)
    register_error_handling(app)
    return app
