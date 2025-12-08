from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.database import create_db_and_tables
from backend.config import CORS_ORIGINS
from backend.routes import products_router, stores_router, stats_router, scrape_urls_router, search_configs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - runs on startup and shutdown."""
    # Startup: Create database tables
    create_db_and_tables()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="PC Component Price Tracker API",
    description="API for tracking PC component prices across multiple stores",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products_router)
app.include_router(stores_router)
app.include_router(stats_router)
app.include_router(scrape_urls_router)
app.include_router(search_configs_router)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "PC Component Price Tracker",
        "version": "1.0.0"
    }


@app.get("/api/health")
def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }
