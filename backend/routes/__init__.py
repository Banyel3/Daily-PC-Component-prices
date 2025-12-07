from .products import router as products_router
from .stores import router as stores_router
from .stats import router as stats_router
from .scrape_urls import router as scrape_urls_router

__all__ = ["products_router", "stores_router", "stats_router", "scrape_urls_router"]
