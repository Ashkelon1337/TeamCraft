from fastapi import FastAPI
from src.routers import auth_router, teams_router, players_router

app = FastAPI()
app.include_router(auth_router.router)
app.include_router(teams_router.router)
app.include_router(players_router.router)

