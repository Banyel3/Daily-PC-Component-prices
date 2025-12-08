"""
Base Playwright scraper for JavaScript-heavy sites like Lazada and Shopee.
Provides async browser automation with anti-detection measures.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import random

from backend.config import USER_AGENT

logger = logging.getLogger(__name__)

# Default delay between requests (5 seconds as requested)
DEFAULT_DELAY_SECONDS = 5.0


@dataclass
class SearchResult:
    """Data structure for a single product from search results."""
    title: str
    price: float
    currency: str = "PHP"
    original_price: Optional[float] = None
    discount_percent: Optional[int] = None
    product_url: str = ""
    image_url: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    sold_count: Optional[str] = None  # "1.2k sold" format
    location: Optional[str] = None
    store_name: Optional[str] = None
    is_official: bool = False
    is_preferred: bool = False


@dataclass
class SearchPageResult:
    """Data structure for a search results page."""
    page_number: int
    products: List[SearchResult] = field(default_factory=list)
    total_pages: Optional[int] = None
    has_next_page: bool = False
    error: Optional[str] = None


class PlaywrightBaseScraper:
    """
    Base scraper using Playwright for browser automation.
    
    Handles JavaScript-rendered content, anti-bot measures,
    and provides async pagination support.
    """
    
    def __init__(self, delay: float = DEFAULT_DELAY_SECONDS, headless: bool = True):
        self.delay = delay
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_browser()
    
    async def start_browser(self):
        """Start Playwright browser with anti-detection settings."""
        playwright = await async_playwright().start()
        
        # Use Chromium with stealth settings
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )
        
        # Create context with realistic viewport and user agent
        self.context = await self.browser.new_context(  # type: ignore[union-attr]
            viewport={'width': 1920, 'height': 1080},
            user_agent=USER_AGENT,
            locale='en-PH',
            timezone_id='Asia/Manila',
            geolocation={'latitude': 14.5995, 'longitude': 120.9842},  # Manila
            permissions=['geolocation'],
        )
        
        # Add stealth scripts to avoid detection
        await self.context.add_init_script("""  # type: ignore[union-attr]
            // Override webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en', 'fil']
        });
        """)
        
        self.page = await self.context.new_page()  # type: ignore[union-attr]
        logger.info("Playwright browser started successfully")
    
    async def close_browser(self):
        """Close browser and cleanup."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Playwright browser closed")
    
    async def wait_with_jitter(self, base_delay: Optional[float] = None):
        """Wait with random jitter to appear more human-like."""
        delay = base_delay or self.delay
        # Add 0-50% random jitter
        jitter = delay * random.uniform(0, 0.5)
        total_delay = delay + jitter
        logger.debug(f"Waiting {total_delay:.2f} seconds")
        await asyncio.sleep(total_delay)
    
    async def scroll_page(self, scroll_count: int = 3):
        """Scroll down the page to trigger lazy loading."""
        if not self.page:
            return
        
        for i in range(scroll_count):
            await self.page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {(i+1)/scroll_count})")
            await asyncio.sleep(0.5)
        
        # Scroll back to top
        await self.page.evaluate("window.scrollTo(0, 0)")
    
    async def navigate_to(self, url: str, wait_selector: Optional[str] = None) -> bool:
        """Navigate to URL and optionally wait for a selector."""
        if not self.page:
            logger.error("Browser page not initialized")
            return False
        
        try:
            response = await self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            if response and response.status >= 400:
                logger.error(f"HTTP {response.status} for {url}")
                return False
            
            if wait_selector:
                await self.page.wait_for_selector(wait_selector, timeout=15000)
            
            # Scroll to load lazy content
            await self.scroll_page()
            
            return True
        except Exception as e:
            logger.error(f"Navigation error for {url}: {e}")
            return False
    
    def parse_price(self, price_text: str) -> Optional[float]:
        """Parse price string to float, handling Philippine Peso format."""
        if not price_text:
            return None
        
        # Remove currency symbols and spaces
        cleaned = price_text.replace('₱', '').replace('PHP', '').replace(',', '').strip()
        
        # Handle price ranges (take the lower price)
        if '-' in cleaned:
            cleaned = cleaned.split('-')[0].strip()
        
        try:
            return float(cleaned)
        except ValueError:
            logger.warning(f"Could not parse price: {price_text}")
            return None
    
    async def search_products(self, search_term: str, page: int = 1) -> SearchPageResult:
        """
        Search for products. Override in subclass.
        
        Args:
            search_term: The search query
            page: Page number (1-indexed)
            
        Returns:
            SearchPageResult with products and pagination info
        """
        raise NotImplementedError("Subclasses must implement search_products")
    
    async def scrape_all_pages(
        self, 
        search_term: str, 
        max_pages: int = 10,
        start_page: int = 1,
        callback=None
    ) -> List[SearchResult]:
        """
        Scrape all pages of search results.
        
        Args:
            search_term: The search query
            max_pages: Maximum pages to scrape (0 = unlimited)
            start_page: Page to start from
            callback: Optional async callback(page_num, results) for progress updates
            
        Returns:
            List of all SearchResult objects
        """
        all_results = []
        current_page = start_page
        
        while True:
            logger.info(f"Scraping page {current_page} for '{search_term}'")
            
            result = await self.search_products(search_term, current_page)
            
            if result.error:
                logger.error(f"Error on page {current_page}: {result.error}")
                break
            
            all_results.extend(result.products)
            logger.info(f"Found {len(result.products)} products on page {current_page}")
            
            if callback:
                await callback(current_page, result)
            
            # Check if we should continue
            if not result.has_next_page:
                logger.info("No more pages available")
                break
            
            if max_pages > 0 and current_page >= max_pages:
                logger.info(f"Reached max pages limit ({max_pages})")
                break
            
            # Wait before next request
            await self.wait_with_jitter()
            current_page += 1
        
        logger.info(f"Total products scraped: {len(all_results)}")
        return all_results
