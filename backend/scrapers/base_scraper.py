"""
Base scraper class for PC component price scraping.
Uses BeautifulSoup for HTML parsing with store-specific selectors.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from dataclasses import dataclass
import time
import re
import logging

from backend.config import USER_AGENT, SCRAPE_DELAY_SECONDS, SCRAPE_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)


@dataclass
class ScrapedData:
    """Data structure for scraped product information."""
    name: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    image: Optional[str] = None
    is_available: bool = True
    error: Optional[str] = None


# Store-specific CSS selectors
# These are the default selectors - can be overridden per URL in the database
STORE_SELECTORS: Dict[str, Dict[str, str]] = {
    "newegg": {
        "name": "h1.product-title",
        "price": ".price-current",
        "image": ".product-view-img-original",
        "availability": ".product-inventory",
    },
    "amazon": {
        "name": "#productTitle",
        "price": ".a-price .a-offscreen",
        "image": "#landingImage",
        "availability": "#availability",
    },
    "bestbuy": {
        "name": ".sku-title h1",
        "price": ".priceView-customer-price span",
        "image": ".primary-image",
        "availability": ".fulfillment-add-to-cart-button",
    },
    "microcenter": {
        "name": "h1.ProductLink",
        "price": "#pricing",
        "image": "#productImage",
        "availability": ".inventory",
    },
}


class BaseScraper:
    """
    Base scraper class using BeautifulSoup for HTML parsing.
    
    Supports store-specific selectors with fallback to default patterns.
    Includes rate limiting and error handling.
    """
    
    def __init__(self, delay: float = SCRAPE_DELAY_SECONDS):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
    
    def detect_store(self, url: str) -> Optional[str]:
        """Detect store from URL."""
        url_lower = url.lower()
        if "newegg" in url_lower:
            return "newegg"
        elif "amazon" in url_lower:
            return "amazon"
        elif "bestbuy" in url_lower:
            return "bestbuy"
        elif "microcenter" in url_lower:
            return "microcenter"
        return None
    
    def get_selectors(self, store: str, custom_selectors: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get CSS selectors for a store, with custom overrides."""
        default = STORE_SELECTORS.get(store, {})
        if custom_selectors:
            return {**default, **{k: v for k, v in custom_selectors.items() if v}}
        return default
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage."""
        try:
            response = self.session.get(url, timeout=SCRAPE_TIMEOUT_SECONDS)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def extract_price(self, text: str) -> Optional[float]:
        """Extract numeric price from text."""
        if not text:
            return None
        
        # Remove currency symbols and commas, find number
        cleaned = re.sub(r"[^\d.,]", "", text)
        # Handle different decimal formats
        cleaned = cleaned.replace(",", "")
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def scrape_product(
        self,
        url: str,
        custom_selectors: Optional[Dict[str, str]] = None
    ) -> ScrapedData:
        """
        Scrape product data from a URL.
        
        Args:
            url: Product page URL
            custom_selectors: Optional custom CSS selectors to override defaults
            
        Returns:
            ScrapedData with product information or error
        """
        result = ScrapedData()
        
        # Detect store and get selectors
        store = self.detect_store(url)
        if not store:
            result.error = "Unknown store - cannot determine selectors"
            return result
        
        selectors = self.get_selectors(store, custom_selectors)
        
        # Fetch page
        soup = self.fetch_page(url)
        if not soup:
            result.error = "Failed to fetch page"
            return result
        
        # Extract name
        if selectors.get("name"):
            name_elem = soup.select_one(selectors["name"])
            if name_elem:
                result.name = name_elem.get_text(strip=True)
        
        # Extract price
        if selectors.get("price"):
            price_elem = soup.select_one(selectors["price"])
            if price_elem:
                result.price = self.extract_price(price_elem.get_text())
        
        # Extract image
        if selectors.get("image"):
            img_elem = soup.select_one(selectors["image"])
            if img_elem:
                img_src = img_elem.get("src") or img_elem.get("data-src")
                result.image = str(img_src) if img_src else None
        
        # Check availability
        if selectors.get("availability"):
            avail_elem = soup.select_one(selectors["availability"])
            if avail_elem:
                avail_text = avail_elem.get_text(strip=True).lower()
                result.is_available = "out of stock" not in avail_text and "unavailable" not in avail_text
        
        # Validate minimum required data
        if not result.name or result.price is None:
            result.error = "Could not extract required data (name and/or price)"
        
        return result
    
    def scrape_with_delay(
        self,
        url: str,
        custom_selectors: Optional[Dict[str, str]] = None
    ) -> ScrapedData:
        """Scrape with rate limiting delay."""
        result = self.scrape_product(url, custom_selectors)
        time.sleep(self.delay)
        return result
