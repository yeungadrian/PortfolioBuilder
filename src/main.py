from fastapi import FastAPI

from src.routers import funds

app = FastAPI()


app.include_router(funds.router)
