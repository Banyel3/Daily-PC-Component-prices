"""
Celery task for scheduled product scraping.
Runs daily at 11:59 PM to scrape all active URLs.
"""

from datetime import datetime, date
from typing import Optional
import logging

from celery import shared_task
from sqlmodel import Session, select

from backend.celery_app import celery_app
from backend.database import engine
from backend.models.product import Product
from backend.models.store import Store
from backend.models.price_history import PriceHistory
from backend.models.scrape_url import ScrapeURL
from backend.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


def calculate_price_change(current_price: float, product_id: str, session: Session) -> float:
    """
    Calculate percentage price change from the previous day's price.
    Returns 0 if no previous price exists.
    """
    # Get the most recent price history entry (excluding today)
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
    
    # Calculate percentage change
    change = ((current_price - previous_price.price) / previous_price.price) * 100
    return round(change, 2)


@celery_app.task(bind=True, max_retries=3)
def scrape_single_url(self, scrape_url_id: str) -> dict:
    """
    Scrape a single URL and update the database.
    
    This task is called for each URL during the daily scrape.
    """
    with Session(engine) as session:
        scrape_url = session.get(ScrapeURL, scrape_url_id)
        if not scrape_url:
            return {"status": "error", "message": "URL not found"}
        
        # Get store info
        store = session.get(Store, scrape_url.store_id)
        if not store:
            return {"status": "error", "message": "Store not found"}
        
        # Prepare custom selectors if any
        custom_selectors = {}
        if scrape_url.name_selector:
            custom_selectors["name"] = scrape_url.name_selector
        if scrape_url.price_selector:
            custom_selectors["price"] = scrape_url.price_selector
        if scrape_url.image_selector:
            custom_selectors["image"] = scrape_url.image_selector
        if scrape_url.availability_selector:
            custom_selectors["availability"] = scrape_url.availability_selector
        
        # Scrape the product
        scraper = BaseScraper()
        result = scraper.scrape_with_delay(
            scrape_url.url,
            custom_selectors if custom_selectors else None
        )
        
        if result.error:
            # Update error tracking
            scrape_url.last_error = result.error
            scrape_url.error_count += 1
            if scrape_url.error_count >= 5:
                scrape_url.is_active = False
            session.add(scrape_url)
            session.commit()
            
            return {"status": "error", "message": result.error, "url": scrape_url.url}
        
        # Check if product already exists (by URL)
        existing_product = session.exec(
            select(Product).where(Product.url == scrape_url.url)
        ).first()
        
        today = date.today()
        now = datetime.utcnow()
        
        # Validate required scraped data
        if result.name is None or result.price is None:
            raise ValueError("Scrape result missing required name or price")
        
        if existing_product:
            # Calculate price change
            price_change = calculate_price_change(result.price, existing_product.id, session)
            
            # Update existing product
            existing_product.name = result.name
            existing_product.current_price = result.price
            existing_product.image = result.image
            existing_product.price_change = price_change if price_change else 0.0
            existing_product.last_scraped = now
            existing_product.scrape_date = today
            existing_product.updated_at = now
            session.add(existing_product)
            
            product_id = existing_product.id
        else:
            # Create new product
            new_product = Product(
                name=result.name,
                current_price=result.price,
                currency=result.currency,
                image=result.image,
                category=scrape_url.category,
                brand=scrape_url.brand,
                url=scrape_url.url,
                store_id=scrape_url.store_id,
                price_change=0.0,  # No previous price
                last_scraped=now,
                scrape_date=today,
            )
            session.add(new_product)
            session.flush()  # Get the ID
            product_id = new_product.id
        
        # Add price history entry
        price_history = PriceHistory(
            product_id=product_id,
            price=result.price,
            currency=result.currency,
            recorded_date=today,
            was_available=result.is_available,
            scrape_source=scrape_url.url,
        )
        session.add(price_history)
        
        # Update scrape URL success status
        scrape_url.last_scraped = now
        scrape_url.last_error = None
        scrape_url.error_count = 0
        session.add(scrape_url)
        
        session.commit()
        
        return {
            "status": "success",
            "product_id": product_id,
            "name": result.name,
            "price": result.price,
            "url": scrape_url.url
        }


@celery_app.task
def scrape_all_products() -> dict:
    """
    Main scheduled task: Scrape all active URLs.
    
    This task runs daily at 11:59 PM (configured in celery_app.py).
    It queues individual scrape tasks for each active URL.
    """
    logger.info("Starting daily scrape task")
    
    with Session(engine) as session:
        # Get all active scrape URLs
        active_urls = session.exec(
            select(ScrapeURL).where(ScrapeURL.is_active == True)
        ).all()
        
        total_urls = len(active_urls)
        logger.info(f"Found {total_urls} active URLs to scrape")
        
        if total_urls == 0:
            return {
                "status": "completed",
                "message": "No active URLs to scrape",
                "total": 0
            }
        
        # Queue individual scrape tasks
        for scrape_url in active_urls:
            scrape_single_url.delay(scrape_url.id)
        
        return {
            "status": "queued",
            "message": f"Queued {total_urls} URLs for scraping",
            "total": total_urls,
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task
def manual_scrape_trigger() -> dict:
    """
    Manual trigger for scraping (for testing purposes).
    Note: In production, scraping should only run at scheduled time.
    """
    return scrape_all_products()
