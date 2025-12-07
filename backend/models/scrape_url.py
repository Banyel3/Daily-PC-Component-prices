from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, ClassVar
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .store import Store


class ScrapeURL(SQLModel, table=True):
    """URLs to scrape for product data."""
    
    __tablename__: ClassVar[str] = "scrape_urls"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    url: str = Field(unique=True, index=True)
    store_id: str = Field(foreign_key="stores.id", index=True)
    
    # Scraping metadata
    category: str  # GPU, CPU, RAM, Storage, Motherboard, Case
    brand: Optional[str] = None
    
    # CSS Selectors for scraping (store-specific overrides)
    name_selector: Optional[str] = None
    price_selector: Optional[str] = None
    image_selector: Optional[str] = None
    availability_selector: Optional[str] = None
    
    # Status tracking
    is_active: bool = Field(default=True)
    last_scraped: Optional[datetime] = None
    last_error: Optional[str] = None
    error_count: int = Field(default=0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    store: Optional["Store"] = Relationship(back_populates="scrape_urls")


class ScrapeURLCreate(SQLModel):
    """Schema for creating a scrape URL."""
    url: str
    store_id: str
    category: str
    brand: Optional[str] = None
    name_selector: Optional[str] = None
    price_selector: Optional[str] = None
    image_selector: Optional[str] = None
    availability_selector: Optional[str] = None


class ScrapeURLRead(SQLModel):
    """Schema for reading scrape URL data."""
    id: str
    url: str
    store_id: str
    category: str
    brand: Optional[str]
    is_active: bool
    last_scraped: Optional[datetime]
    last_error: Optional[str]
    error_count: int
    created_at: datetime


class ScrapeURLBulkImport(SQLModel):
    """Schema for bulk importing URLs."""
    store_name: str  # Will be resolved to store_id
    category: str
    brand: Optional[str] = None
    urls: list[str]
