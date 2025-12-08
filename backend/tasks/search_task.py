"""
Celery task for search-based product scraping.
Scrapes Lazada and Shopee search results with pagination support.
"""

import asyncio
from datetime import datetime, date
from typing import Optional, List
from dataclasses import dataclass
import logging

from celery import shared_task
from sqlmodel import Session, select

from backend.celery_app import celery_app
from backend.database import engine
from backend.models.product import Product
from backend.models.store import Store
from backend.models.price_history import PriceHistory
from backend.models.search_config import SearchConfig, ComponentCategory, CATEGORY_SEARCH_TERMS
from backend.scrapers.playwright_base import SearchResult
from backend.scrapers.lazada_scraper import LazadaScraper
from backend.scrapers.shopee_scraper import ShopeeScraper

logger = logging.getLogger(__name__)


@dataclass
class SearchConfigData:
    """Simple data class to pass search config data outside session."""
    id: str
    store_id: str
    search_term: str
    category: str
    max_pages: int
    last_page_scraped: int


@dataclass
class StoreData:
    """Simple data class to pass store data outside session."""
    id: str
    name: str
    url: str


def run_async(coro):
    """Helper to run async code in sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def calculate_price_change(current_price: float, product_id: str, session: Session) -> float:
    """
    Calculate percentage price change from the previous day's price.
    Returns 0 if no previous price exists.
    """
    today = date.today()
    previous_price = session.exec(
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id)
        .where(PriceHistory.recorded_date < today)
        .order_by(PriceHistory.recorded_date.desc())  # type: ignore[union-attr]
        .limit(1)
    ).first()
    
    if not previous_price or previous_price.price == 0:
        return 0.0
    
    change = ((current_price - previous_price.price) / previous_price.price) * 100
    return round(change, 2)


def save_search_result(result: SearchResult, store_id: str, category: str, session: Session) -> Optional[str]:
    """
    Save a search result to the database.
    Creates or updates Product and adds PriceHistory entry.
    
    Returns the product ID if successful, None otherwise.
    """
    if not result.title or not result.price or not result.product_url:
        return None
    
    today = date.today()
    now = datetime.utcnow()
    
    # Check if product already exists (by URL)
    existing_product = session.exec(
        select(Product).where(Product.url == result.product_url)
    ).first()
    
    if existing_product:
        # Update existing product
        existing_product.name = result.title
        existing_product.current_price = result.price
        existing_product.image = result.image_url
        existing_product.is_active = True
        existing_product.updated_at = now
        existing_product.last_scraped = now
        existing_product.scrape_date = today
        existing_product.currency = "PHP"
        
        # Calculate price change
        price_change = calculate_price_change(result.price, existing_product.id, session)
        existing_product.price_change = price_change
        
        session.add(existing_product)
        product_id = existing_product.id
    else:
        # Create new product
        new_product = Product(
            name=result.title,
            url=result.product_url,
            store_id=store_id,
            category=category,
            current_price=result.price,
            currency="PHP",
            image=result.image_url,
            is_active=True,
            last_scraped=now,
            scrape_date=today,
            created_at=now,
            updated_at=now,
        )
        session.add(new_product)
        session.flush()  # Get the ID
        product_id = new_product.id
    
    # Check if we already have a price entry for today
    existing_history = session.exec(
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id)
        .where(PriceHistory.recorded_date == today)
    ).first()
    
    if not existing_history:
        # Add price history entry
        price_history = PriceHistory(
            product_id=product_id,
            price=result.price,
            recorded_date=today,
            recorded_at=now,
        )
        session.add(price_history)
    else:
        # Update existing price entry
        existing_history.price = result.price
        existing_history.recorded_at = now
        session.add(existing_history)
    
    return product_id


async def scrape_search_config_async(config: SearchConfigData, store: StoreData) -> dict:
    """
    Async function to scrape a search configuration.
    
    Returns dict with results summary.
    """
    store_name = store.name.lower()
    results = {
        "config_id": config.id,
        "store": store_name,
        "search_term": config.search_term,
        "products_found": 0,
        "pages_scraped": 0,
        "errors": [],
    }
    
    # Choose the right scraper
    if "lazada" in store_name:
        scraper_class = LazadaScraper
    elif "shopee" in store_name:
        scraper_class = ShopeeScraper
    else:
        results["errors"].append(f"Unknown store type: {store_name}")
        return results
    
    try:
        async with scraper_class(delay=5.0, headless=True) as scraper:
            # Progress callback to track pages
            async def on_page_complete(page_num: int, page_result):
                results["pages_scraped"] = page_num
                logger.info(f"Completed page {page_num} for {config.search_term}")
            
            # Scrape all pages
            products = await scraper.scrape_all_pages(
                search_term=config.search_term,
                max_pages=config.max_pages,
                start_page=config.last_page_scraped + 1 if config.last_page_scraped > 0 else 1,
                callback=on_page_complete,
            )
            
            results["products_found"] = len(products)
            
            # Save products to database
            with Session(engine) as session:
                saved_count = 0
                for product in products:
                    try:
                        product_id = save_search_result(
                            result=product,
                            store_id=config.store_id,
                            category=config.category,
                            session=session
                        )
                        if product_id:
                            saved_count += 1
                    except Exception as e:
                        logger.warning(f"Error saving product: {e}")
                        results["errors"].append(str(e))
                
                # Update search config status
                config_update = session.get(SearchConfig, config.id)
                if config_update:
                    config_update.status = "completed"
                    config_update.last_scraped_at = datetime.utcnow()
                    config_update.total_products_found = saved_count
                    config_update.last_page_scraped = results["pages_scraped"]
                    config_update.last_error = None
                    session.add(config_update)
                
                session.commit()
                
                results["products_saved"] = saved_count
                logger.info(f"Saved {saved_count} products for {config.search_term}")
                
    except Exception as e:
        logger.error(f"Search scrape error: {e}")
        results["errors"].append(str(e))
        
        # Update config with error
        with Session(engine) as session:
            config_update = session.get(SearchConfig, config.id)
            if config_update:
                config_update.status = "error"
                config_update.last_error = str(e)
                session.add(config_update)
                session.commit()
    
    return results


@celery_app.task(bind=True, max_retries=2)
def scrape_search_config(self, config_id: str) -> dict:
    """
    Celery task to scrape a single search configuration.
    
    Args:
        config_id: ID of the SearchConfig to scrape
        
    Returns:
        Dict with scraping results
    """
    with Session(engine) as session:
        config = session.get(SearchConfig, config_id)
        if not config:
            return {"status": "error", "message": "Config not found"}
        
        if not config.is_active:
            return {"status": "skipped", "message": "Config is inactive"}
        
        store = session.get(Store, config.store_id)
        if not store:
            return {"status": "error", "message": "Store not found"}
        
        # Mark as running
        config.status = "running"
        session.add(config)
        session.commit()
        
        # Refresh to get clean objects outside the session
        config_data = SearchConfigData(
            id=config.id,
            store_id=config.store_id,
            search_term=config.search_term,
            category=config.category,
            max_pages=config.max_pages,
            last_page_scraped=config.last_page_scraped,
        )
        store_data = StoreData(id=store.id, name=store.name, url=store.url)
    
    # Run the async scraper
    result = run_async(scrape_search_config_async(config_data, store_data))
    
    return result


@celery_app.task
def scrape_all_search_configs() -> dict:
    """
    Celery task to scrape all active search configurations.
    Called on schedule to update all product prices.
    """
    results = {
        "total_configs": 0,
        "successful": 0,
        "failed": 0,
        "skipped": 0,
        "details": [],
    }
    
    with Session(engine) as session:
        # Get all active search configs
        configs = session.exec(
            select(SearchConfig).where(SearchConfig.is_active == True)
        ).all()
        
        results["total_configs"] = len(configs)
        
        for config in configs:
            # Queue each config as a separate task
            task = scrape_search_config.delay(config.id)
            results["details"].append({
                "config_id": config.id,
                "search_term": config.search_term,
                "task_id": task.id,
            })
    
    logger.info(f"Queued {results['total_configs']} search configs for scraping")
    return results


@celery_app.task
def create_default_search_configs() -> dict:
    """
    Create default search configurations for Lazada and Shopee.
    This sets up the basic PC component searches.
    """
    results = {"created": [], "skipped": []}
    
    # Default search terms for PC components
    default_searches = [
        {"category": ComponentCategory.GPU.value, "search_term": "graphics card"},
        {"category": ComponentCategory.GPU.value, "search_term": "RTX 4090"},
        {"category": ComponentCategory.GPU.value, "search_term": "RTX 4080"},
        {"category": ComponentCategory.GPU.value, "search_term": "RTX 4070"},
        {"category": ComponentCategory.GPU.value, "search_term": "RX 7900"},
        {"category": ComponentCategory.CPU.value, "search_term": "processor"},
        {"category": ComponentCategory.CPU.value, "search_term": "Ryzen 7"},
        {"category": ComponentCategory.CPU.value, "search_term": "Intel Core i7"},
        {"category": ComponentCategory.RAM.value, "search_term": "DDR5 RAM"},
        {"category": ComponentCategory.RAM.value, "search_term": "DDR4 32GB"},
        {"category": ComponentCategory.MOTHERBOARD.value, "search_term": "gaming motherboard"},
        {"category": ComponentCategory.SSD.value, "search_term": "NVMe SSD 1TB"},
        {"category": ComponentCategory.PSU.value, "search_term": "modular PSU"},
        {"category": ComponentCategory.COOLER.value, "search_term": "AIO cooler 360mm"},
        {"category": ComponentCategory.MONITOR.value, "search_term": "gaming monitor 144hz"},
    ]
    
    with Session(engine) as session:
        # Get Lazada and Shopee stores
        lazada = session.exec(
            select(Store).where(Store.name.ilike("%lazada%"))  # type: ignore[union-attr]
        ).first()
        shopee = session.exec(
            select(Store).where(Store.name.ilike("%shopee%"))  # type: ignore[union-attr]
        ).first()
        
        stores = []
        if lazada:
            stores.append(lazada)
        if shopee:
            stores.append(shopee)
        
        if not stores:
            return {"error": "No Lazada or Shopee stores found. Please seed them first."}
        
        for store in stores:
            for search in default_searches:
                # Check if config already exists
                existing = session.exec(
                    select(SearchConfig)
                    .where(SearchConfig.store_id == store.id)
                    .where(SearchConfig.search_term == search["search_term"])
                ).first()
                
                if existing:
                    results["skipped"].append({
                        "store": store.name,
                        "search_term": search["search_term"],
                    })
                    continue
                
                # Create new config
                config = SearchConfig(
                    store_id=store.id,
                    category=search["category"],
                    search_term=search["search_term"],
                    max_pages=5,  # Start with 5 pages per search
                    is_active=True,
                )
                session.add(config)
                results["created"].append({
                    "store": store.name,
                    "search_term": search["search_term"],
                    "category": search["category"],
                })
        
        session.commit()
    
    logger.info(f"Created {len(results['created'])} search configs, skipped {len(results['skipped'])}")
    return results
