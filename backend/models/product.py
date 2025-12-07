from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING, ClassVar
from datetime import datetime, date
from decimal import Decimal
import uuid

if TYPE_CHECKING:
    from .store import Store
    from .price_history import PriceHistory


class Product(SQLModel, table=True):
    """Product model representing a PC component being tracked."""
    
    __tablename__: ClassVar[str] = "products"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(index=True)
    current_price: float
    currency: str = Field(default="USD")
    image: Optional[str] = None
    category: str = Field(index=True)  # GPU, CPU, RAM, Storage, Motherboard, Case
    brand: Optional[str] = Field(default=None, index=True)
    url: str = Field(unique=True)  # Product URL is unique identifier
    
    # Store relationship
    store_id: str = Field(foreign_key="stores.id", index=True)
    store: Optional["Store"] = Relationship(back_populates="products")
    
    # Price tracking
    price_change: float = Field(default=0.0)  # Percentage change from previous day
    last_scraped: Optional[datetime] = None
    scrape_date: Optional[date] = Field(default=None, index=True)  # Date of last scrape
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    # Relationships
    price_history: List["PriceHistory"] = Relationship(back_populates="product")


class ProductCreate(SQLModel):
    """Schema for creating a new product."""
    name: str
    current_price: float
    currency: str = "USD"
    image: Optional[str] = None
    category: str
    brand: Optional[str] = None
    url: str
    store_id: str


class ProductRead(SQLModel):
    """Schema for reading product data (matches frontend interface)."""
    id: str
    name: str
    price: float  # Alias for current_price to match frontend
    currency: str
    image: Optional[str]
    category: str
    store: str  # Store name instead of ID for frontend
    brand: Optional[str]
    url: str
    lastUpdated: str  # ISO format string for frontend
    priceChange: float  # Percentage change


class ProductWithHistory(ProductRead):
    """Product with price history for detailed views."""
    price_history: List["PriceHistoryRead"] = []


# Import here to avoid circular imports
from .price_history import PriceHistoryRead
