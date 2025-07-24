from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import uvicorn
import os
from pathlib import Path
from loguru import logger

from src.core.config import settings
from src.core.database import connect_to_mongo, close_mongo_connection
from src.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Car Finder application...")
    await connect_to_mongo()
    logger.info("Connected to MongoDB")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Car Finder application...")
    await close_mongo_connection()
    logger.info("Disconnected from MongoDB")


# Create FastAPI application
app = FastAPI(
    title="Car Finder API",
    description="Automated used car arbitrage opportunity finder",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_hosts_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Static files configuration - serve React build output
static_dir = Path("/app/static")
assets_dir = Path("/app/static/assets")

if static_dir.exists():
    # Mount assets directory directly at /assets (for React JS/CSS files)
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        logger.info(f"Mounted assets from {assets_dir} at /assets")
    
    # Add individual routes for favicon and icon files (avoids capturing all routes)
    from fastapi.responses import FileResponse
    
    @app.get("/car-icon.svg")
    async def car_icon():
        return FileResponse(str(static_dir / "car-icon.svg"))
    
    @app.get("/favicon-32x32.png")
    async def favicon_32():
        return FileResponse(str(static_dir / "favicon-32x32.png"))
    
    @app.get("/favicon-16x16.png")
    async def favicon_16():
        return FileResponse(str(static_dir / "favicon-16x16.png"))
    
    @app.get("/apple-touch-icon.png")
    async def apple_touch_icon():
        return FileResponse(str(static_dir / "apple-touch-icon.png"))
    
    logger.info(f"Added favicon and icon routes for static files")
else:
    logger.warning(f"Static directory {static_dir} not found")


@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy", "service": "car-finder"}


# Catch-all route for React SPA (must be last)
@app.get("/{path:path}")
async def serve_spa(request: Request, path: str = ""):
    """
    Serve React SPA for all non-API routes
    This handles client-side routing
    """
    # Don't serve SPA for API routes, docs, or favicon files
    if (path.startswith("api/") or path.startswith("docs") or path.startswith("redoc") or 
        path.startswith("assets/") or path.endswith(".svg") or path.endswith(".png") or 
        path.endswith(".ico") or path == "health"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve index.html for SPA routes
    index_file = Path("/app/static/index.html")
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        # Fallback response if no frontend built
        return {
            "message": "Car Finder API", 
            "version": "1.0.0",
            "status": "running",
            "frontend": "not built"
        }


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 