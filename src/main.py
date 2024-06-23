from fastapi import FastAPI

from src.routers import funds, health

app = FastAPI()

app.include_router(health.router, tags=["healthcheck"])
app.include_router(funds.router, tags=["funds"])
