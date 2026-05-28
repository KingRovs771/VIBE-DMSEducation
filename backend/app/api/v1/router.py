"""
API v1 main router — menggabungkan semua sub-router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, documents, categories

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
