from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import date, datetime

from backend.database import get_session
from backend.models.product import Product, ProductRead
from backend.models.store import Store
from backend.models.price_history import PriceHistory

router = APIRouter(prefix="/api/products", tags=["products"])


def product_to_read(product: Product, store_name: str) -> ProductRead:
    """Convert Product model to ProductRead schema."""
    return ProductRead(
        id=product.id,
        name=product.name,
        price=product.current_price,
        currency=product.currency,
        image=product.image,
        category=product.category,
        store=store_name,
        brand=product.brand,
        url=product.url,
        lastUpdated=product.last_scraped.isoformat() if product.last_scraped else datetime.utcnow().isoformat(),
        priceChange=product.price_change
    )


@router.get("/", response_model=List[ProductRead])
def get_products(
    session: Session = Depends(get_session),
    date_filter: Optional[date] = Query(None, alias="date", description="Filter by scrape date (defaults to today)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    store: Optional[str] = Query(None, description="Filter by store name"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    search: Optional[str] = Query(None, alias="q", description="Search in product name"),
):
    """
    Get all products scraped for a specific date.
    Defaults to today's date - only returns current day's scraped data.
    Search functionality operates only on the already scraped data.
    """
    # Default to today's date
    if date_filter is None:
        date_filter = date.today()
    
    # Build query
    query = select(Product, Store).join(Store).where(Product.scrape_date == date_filter)
    
    # Apply filters
    if category:
        query = query.where(Product.category == category)
    if store:
        query = query.where(Store.name == store)
    if brand:
        query = query.where(Product.brand == brand)
    if min_price is not None:
        query = query.where(Product.current_price >= min_price)
    if max_price is not None:
        query = query.where(Product.current_price <= max_price)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))  # type: ignore[union-attr]
    
    # Execute query
    results = session.exec(query).all()
    
    # Convert to response format
    return [product_to_read(product, store.name) for product, store in results]


@router.get("/categories", response_model=List[str])
def get_categories(session: Session = Depends(get_session)):
    """Get all unique product categories."""
    query = select(Product.category).distinct()
    results = session.exec(query).all()
    return [cat for cat in results if cat]


@router.get("/brands", response_model=List[str])
def get_brands(session: Session = Depends(get_session)):
    """Get all unique product brands."""
    query = select(Product.brand).distinct()
    results = session.exec(query).all()
    return [brand for brand in results if brand]


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: str, session: Session = Depends(get_session)):
    """Get a specific product by ID."""
    query = select(Product, Store).join(Store).where(Product.id == product_id)
    result = session.exec(query).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product, store = result
    return product_to_read(product, store.name)


@router.get("/{product_id}/history")
def get_product_history(
    product_id: str,
    session: Session = Depends(get_session),
    days: int = Query(30, description="Number of days of history to return")
):
    """Get price history for a specific product."""
    # Verify product exists
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get price history
    query = (
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.recorded_date.desc())  # type: ignore[union-attr]
        .limit(days)
    )
    history = session.exec(query).all()
    
    return {
        "product_id": product_id,
        "product_name": product.name,
        "history": [
            {
                "date": h.recorded_date.isoformat(),
                "price": h.price,
                "currency": h.currency,
                "was_available": h.was_available
            }
            for h in history
        ]
    }
