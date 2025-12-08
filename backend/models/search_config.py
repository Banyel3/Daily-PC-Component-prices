"""
SearchConfig model for automatic search-based scraping.
Stores configuration for searching PC components on Lazada and Shopee.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, ClassVar, TYPE_CHECKING
from datetime import datetime
from enum import Enum
import uuid

if TYPE_CHECKING:
    from .store import Store


class ComponentCategory(str, Enum):
    """PC component categories for search."""
    GPU = "gpu"
    CPU = "cpu"
    RAM = "ram"
    MOTHERBOARD = "motherboard"
    PSU = "psu"
    SSD = "ssd"
    HDD = "hdd"
    CASE = "case"
    COOLER = "cooler"
    MONITOR = "monitor"
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    CUSTOM = "custom"


# Search term mappings for each category
CATEGORY_SEARCH_TERMS = {
    ComponentCategory.GPU: ["graphics card", "GPU", "video card", "RTX", "RX"],
    ComponentCategory.CPU: ["processor", "CPU", "Ryzen", "Intel Core"],
    ComponentCategory.RAM: ["RAM", "memory DDR4", "memory DDR5"],
    ComponentCategory.MOTHERBOARD: ["motherboard", "mainboard"],
    ComponentCategory.PSU: ["power supply", "PSU"],
    ComponentCategory.SSD: ["SSD", "solid state drive", "NVMe"],
    ComponentCategory.HDD: ["hard drive", "HDD"],
    ComponentCategory.CASE: ["PC case", "computer case", "ATX case"],
    ComponentCategory.COOLER: ["CPU cooler", "AIO cooler", "air cooler"],
    ComponentCategory.MONITOR: ["gaming monitor", "computer monitor"],
    ComponentCategory.KEYBOARD: ["mechanical keyboard", "gaming keyboard"],
    ComponentCategory.MOUSE: ["gaming mouse", "wireless mouse"],
}


class SearchConfig(SQLModel, table=True):
    """
    Search configuration for automatic product discovery.
    
    Defines what to search for on each store (Lazada/Shopee) with
    pagination tracking and scheduling options.
    """
    
    __tablename__: ClassVar[str] = "search_configs"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    store_id: str = Field(foreign_key="stores.id", index=True)
    
    # Search configuration
    category: str = Field(index=True)  # ComponentCategory value
    search_term: str  # Actual search query to use
    
    # Pagination settings
    max_pages: int = Field(default=10)  # Maximum pages to scrape (0 = unlimited)
    products_per_page: int = Field(default=40)  # Expected products per page
    
    # State tracking
    last_page_scraped: int = Field(default=0)  # Last successfully scraped page
    total_pages_found: Optional[int] = None  # Total pages discovered during scrape
    total_products_found: int = Field(default=0)  # Total products found so far
    
    # Status
    is_active: bool = Field(default=True)  # Enable/disable this search
    status: str = Field(default="pending")  # pending, running, completed, error
    last_error: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_scraped_at: Optional[datetime] = None
    
    # Relationships
    store: Optional["Store"] = Relationship()


class SearchConfigCreate(SQLModel):
    """Schema for creating a new search config."""
    store_id: str
    category: str
    search_term: str
    max_pages: int = 10
    is_active: bool = True


class SearchConfigRead(SQLModel):
    """Schema for reading search config data."""
    id: str
    store_id: str
    category: str
    search_term: str
    max_pages: int
    products_per_page: int
    last_page_scraped: int
    total_pages_found: Optional[int]
    total_products_found: int
    is_active: bool
    status: str
    last_error: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_scraped_at: Optional[datetime]


class SearchConfigUpdate(SQLModel):
    """Schema for updating a search config."""
    search_term: Optional[str] = None
    max_pages: Optional[int] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None
    last_page_scraped: Optional[int] = None
    total_pages_found: Optional[int] = None
    total_products_found: Optional[int] = None
    last_error: Optional[str] = None
