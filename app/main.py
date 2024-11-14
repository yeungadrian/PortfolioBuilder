from fastapi import FastAPI

from app.api.api_router import api_router

app = FastAPI(title="Portfolio Builder", version="1.0.0")

app.include_router(api_router)
