from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func, col
from datetime import date

from backend.database import get_session
from backend.models.product import Product
from backend.models.store import Store

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/")
def get_stats(session: Session = Depends(get_session)):
    """
    Get dashboard statistics for today's scraped data.
    All stats are based on the current day's scrape results.
    """
    today = date.today()
    
    # Total products tracked (scraped today)
    total_products = session.exec(
        select(func.count(col(Product.id))).where(Product.scrape_date == today)
    ).one()
    
    # Unique stores with products scraped today
    unique_stores = session.exec(
        select(func.count(func.distinct(col(Product.store_id))))
        .where(Product.scrape_date == today)
    ).one()
    
    # Products with price drops today
    price_drops = session.exec(
        select(func.count(col(Product.id)))
        .where(Product.scrape_date == today)
        .where(Product.price_change < 0)
    ).one()
    
    # Biggest price drop percentage today
    biggest_drop_result = session.exec(
        select(func.min(Product.price_change))
        .where(Product.scrape_date == today)
        .where(Product.price_change < 0)
    ).one()
    biggest_drop = biggest_drop_result if biggest_drop_result else 0
    
    # Categories count
    categories_count = session.exec(
        select(func.count(func.distinct(Product.category)))
        .where(Product.scrape_date == today)
    ).one()
    
    # Average price drop for products with drops
    avg_drop_result = session.exec(
        select(func.avg(Product.price_change))
        .where(Product.scrape_date == today)
        .where(Product.price_change < 0)
    ).one()
    avg_drop = round(avg_drop_result, 2) if avg_drop_result else 0
    
    return {
        "date": today.isoformat(),
        "total_products": total_products or 0,
        "unique_stores": unique_stores or 0,
        "price_drops": price_drops or 0,
        "biggest_drop": round(abs(biggest_drop), 2),
        "categories_count": categories_count or 0,
        "avg_price_drop": abs(avg_drop),
    }


@router.get("/top-deals")
def get_top_deals(
    session: Session = Depends(get_session),
    limit: int = 10
):
    """
    Get top deals (biggest price drops) for today.
    """
    today = date.today()
    
    query = (
        select(Product, Store)
        .join(Store)
        .where(Product.scrape_date == today)
        .where(Product.price_change < 0)
        .order_by(Product.price_change.asc())  # type: ignore[union-attr]
        .limit(limit)
    )
    
    results = session.exec(query).all()
    
    return [
        {
            "id": product.id,
            "name": product.name,
            "price": product.current_price,
            "currency": product.currency,
            "image": product.image,
            "category": product.category,
            "store": store.name,
            "brand": product.brand,
            "url": product.url,
            "lastUpdated": product.last_scraped.isoformat() if product.last_scraped else None,
            "priceChange": product.price_change
        }
        for product, store in results
    ]


@router.get("/by-category")
def get_stats_by_category(session: Session = Depends(get_session)):
    """Get product counts and average prices by category for today."""
    today = date.today()
    
    query = (
        select(  # type: ignore[call-overload]
            col(Product.category),
            func.count(col(Product.id)).label("count"),
            func.avg(col(Product.current_price)).label("avg_price"),
            func.min(col(Product.current_price)).label("min_price"),
            func.max(col(Product.current_price)).label("max_price")
        )
        .where(Product.scrape_date == today)
        .group_by(col(Product.category))
    )
    
    results = session.exec(query).all()
    
    return [
        {
            "category": row[0],
            "count": row[1],
            "avg_price": round(row[2], 2) if row[2] else 0,
            "min_price": row[3] or 0,
            "max_price": row[4] or 0
        }
        for row in results
    ]
