from fastapi import FastAPI

from app.api.api_router import api_router
from app.config import settings

app = FastAPI(title=settings.title, version=settings.version)

app.include_router(api_router)
