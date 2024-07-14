import logging

from fastapi import FastAPI

from app.api.main import api_router
from app.middleware import LoggingMiddleware

uvicorn_error = logging.getLogger("uvicorn.error")
uvicorn_error.disabled = True
uvicorn_access = logging.getLogger("uvicorn.access")
uvicorn_access.disabled = True

app = FastAPI()

app.include_router(api_router)
app.add_middleware(LoggingMiddleware)
