"""AstroFlow — FastAPI application entry point."""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.config import settings
from app.database import init_db
from app.graphql.schema import schema
from app.api.health import router as health_router
from app.api.websocket import router as ws_router
from app.etl.scheduler import start_scheduler, stop_scheduler
from app.services.broadcaster import start_broadcast, stop_broadcast

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)

app = FastAPI(
    title="AstroFlow API",
    version="1.0.0",
    description="Space Science Intelligence Platform — GraphQL + WebSocket",
    redirect_slashes=False,   # prevent 301 /health → /health/ that bypasses the Vite proxy
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL — Strawberry + FastAPI integration
graphql_app = GraphQLRouter(schema, graphiql=True)
app.include_router(graphql_app, prefix="/graphql")

# REST health endpoints
app.include_router(health_router, prefix="/health")

# WebSocket
app.include_router(ws_router)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()
    await start_scheduler()
    await start_broadcast()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await stop_scheduler()
    await stop_broadcast()


@app.get("/", tags=["root"])
async def root():
    return {
        "service": "AstroFlow API",
        "version": "1.0.0",
        "graphql": "/graphql",
        "health": "/health",
        "etl_health": "/health/etl",
        "websocket": "ws://<host>/ws",
    }
