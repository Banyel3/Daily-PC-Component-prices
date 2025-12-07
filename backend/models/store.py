from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING, ClassVar
from datetime import datetime, date
from decimal import Decimal
import uuid

if TYPE_CHECKING:
    from .product import Product
    from .scrape_url import ScrapeURL


class Store(SQLModel, table=True):
    """Store model representing a retailer that sells PC components."""
    
    __tablename__: ClassVar[str] = "stores"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(index=True, unique=True)
    url: str
    logo: Optional[str] = None
    description: Optional[str] = None
    status: str = Field(default="active")  # active, inactive, error
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    products: List["Product"] = Relationship(back_populates="store")
    scrape_urls: List["ScrapeURL"] = Relationship(back_populates="store")


class StoreCreate(SQLModel):
    """Schema for creating a new store."""
    name: str
    url: str
    logo: Optional[str] = None
    description: Optional[str] = None
    status: str = "active"


class StoreRead(SQLModel):
    """Schema for reading store data."""
    id: str
    name: str
    url: str
    logo: Optional[str]
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
