from fastapi import APIRouter
from src.api.v1 import users, searches, opportunities, vehicles

api_router = APIRouter()

# Include all route modules
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(searches.router, prefix="/searches", tags=["searches"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"]) 