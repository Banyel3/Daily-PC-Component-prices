from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, ClassVar
from datetime import datetime, date
import uuid

if TYPE_CHECKING:
    from .product import Product


class PriceHistory(SQLModel, table=True):
    """Price history model for tracking product prices over time."""
    
    __tablename__: ClassVar[str] = "price_history"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    product_id: str = Field(foreign_key="products.id", index=True)
    price: float
    currency: str = Field(default="USD")
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    recorded_date: date = Field(index=True)  # For easy date-based queries
    
    # Optional metadata from scrape
    was_available: bool = Field(default=True)
    scrape_source: Optional[str] = None  # URL that was scraped
    
    # Relationship
    product: Optional["Product"] = Relationship(back_populates="price_history")


class PriceHistoryCreate(SQLModel):
    """Schema for creating a price history entry."""
    product_id: str
    price: float
    currency: str = "USD"
    recorded_date: date
    was_available: bool = True
    scrape_source: Optional[str] = None


class PriceHistoryRead(SQLModel):
    """Schema for reading price history data."""
    id: str
    product_id: str
    price: float
    currency: str
    recorded_at: datetime
    recorded_date: date
    was_available: bool
