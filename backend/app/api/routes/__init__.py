from fastapi import APIRouter

from app.api.routes import auth, health, leads, portal

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(leads.router)
api_router.include_router(portal.router)

__all__ = ["api_router"]
