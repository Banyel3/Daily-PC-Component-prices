"""
Lazada PH scraper using Playwright.
Handles search-based product discovery with pagination.
"""

import logging
import re
from typing import Optional
from urllib.parse import urlencode, quote_plus

from .playwright_base import PlaywrightBaseScraper, SearchResult, SearchPageResult

logger = logging.getLogger(__name__)


class LazadaScraper(PlaywrightBaseScraper):
    """
    Scraper for Lazada Philippines (lazada.com.ph).
    
    Search URL format: https://www.lazada.com.ph/catalog/?q={query}&page={page}
    """
    
    BASE_URL = "https://www.lazada.com.ph"
    
    # CSS Selectors for Lazada search results
    SELECTORS = {
        # Product grid container
        "product_grid": "[data-qa-locator='general-products']",
        "product_item": "[data-qa-locator='product-item']",
        
        # Alternative selectors (Lazada changes these frequently)
        "product_item_alt": ".Bm3ON, [data-tracking='product-card']",
        "product_link": "a[href*='/products/']",
        
        # Product details within item
        "title": ".RfADt a, [data-qa-locator='product-item'] a",
        "price": ".ooOxS, .price-wrapper span",
        "original_price": ".WNoq3, .price--original-del",
        "discount": ".IcOsH, .price-discount",
        "image": "img[src*='lazada'], img[data-src*='lazada']",
        "rating": ".qzqFw, .rating-stars",
        "sold": ".mdmmT, .item-sold-and-location span",
        "location": "._6uN7R, .item-sold-and-location span:last-child",
        "store_name": "._1HVbe, .seller-name",
        
        # Pagination
        "pagination": ".ant-pagination",
        "next_page": ".ant-pagination-next:not(.ant-pagination-disabled)",
        "page_numbers": ".ant-pagination-item",
        "total_results": ".qGXE9D, .search-result-count",
    }
    
    def build_search_url(self, search_term: str, page: int = 1) -> str:
        """Build Lazada search URL."""
        params = {
            'q': search_term,
            'page': page,
        }
        return f"{self.BASE_URL}/catalog/?{urlencode(params)}"
    
    async def search_products(self, search_term: str, page: int = 1) -> SearchPageResult:
        """
        Search for products on Lazada PH.
        
        Args:
            search_term: The search query (e.g., "graphics card", "RTX 4090")
            page: Page number (1-indexed)
            
        Returns:
            SearchPageResult with products and pagination info
        """
        url = self.build_search_url(search_term, page)
        result = SearchPageResult(page_number=page)
        
        logger.info(f"Lazada search: {url}")
        
        try:
            # Navigate to search page
            success = await self.navigate_to(url)
            if not success:
                result.error = "Failed to load search page"
                return result
            
            # Wait for products to load
            assert self.page is not None  # For type checker
            await self.page.wait_for_timeout(2000)  # Give JS time to render
            
            # Extract products using JavaScript evaluation
            products_data = await self.page.evaluate("""
                () => {
                    const products = [];
                    
                    // Try multiple selector strategies
                    const selectors = [
                        '[data-qa-locator="product-item"]',
                        '.Bm3ON',
                        '[data-tracking="product-card"]',
                        '.qmXQo',
                    ];
                    
                    let items = [];
                    for (const selector of selectors) {
                        items = document.querySelectorAll(selector);
                        if (items.length > 0) break;
                    }
                    
                    items.forEach(item => {
                        try {
                            // Get link and title
                            const linkEl = item.querySelector('a[href*="/products/"]') || 
                                          item.querySelector('a[href*="lazada.com.ph"]');
                            const titleEl = item.querySelector('.RfADt a') || 
                                           item.querySelector('[data-qa-locator="product-item"] a') ||
                                           linkEl;
                            
                            // Get prices
                            const priceEl = item.querySelector('.ooOxS') || 
                                           item.querySelector('[data-price]') ||
                                           item.querySelector('.price-current');
                            const originalPriceEl = item.querySelector('.WNoq3') ||
                                                   item.querySelector('.price--original-del');
                            const discountEl = item.querySelector('.IcOsH') ||
                                              item.querySelector('.price-discount');
                            
                            // Get image
                            const imgEl = item.querySelector('img[src*="lazada"]') ||
                                         item.querySelector('img[data-src]') ||
                                         item.querySelector('img');
                            
                            // Get ratings and sold
                            const ratingEl = item.querySelector('.qzqFw') ||
                                            item.querySelector('.rating-stars');
                            const soldEl = item.querySelector('.mdmmT') ||
                                          item.querySelector('.item-sold-and-location');
                            const locationEl = item.querySelector('._6uN7R') ||
                                              item.querySelectorAll('.item-sold-and-location span')[1];
                            
                            // Get store info
                            const storeEl = item.querySelector('._1HVbe') ||
                                           item.querySelector('.seller-name');
                            const isOfficial = item.querySelector('.official-store-badge') !== null ||
                                              item.textContent.includes('Official');
                            const isPreferred = item.querySelector('.lazmall-badge') !== null ||
                                               item.textContent.includes('LazMall');
                            
                            const product = {
                                title: titleEl?.textContent?.trim() || '',
                                price: priceEl?.textContent?.trim() || '',
                                original_price: originalPriceEl?.textContent?.trim() || '',
                                discount: discountEl?.textContent?.trim() || '',
                                url: linkEl?.href || '',
                                image: imgEl?.src || imgEl?.dataset?.src || '',
                                rating: ratingEl?.textContent?.trim() || '',
                                sold: soldEl?.textContent?.trim() || '',
                                location: locationEl?.textContent?.trim() || '',
                                store: storeEl?.textContent?.trim() || '',
                                is_official: isOfficial,
                                is_preferred: isPreferred,
                            };
                            
                            if (product.title && product.price) {
                                products.push(product);
                            }
                        } catch (e) {
                            console.error('Error parsing product:', e);
                        }
                    });
                    
                    return products;
                }
            """)
            
            # Parse extracted data
            for data in products_data:
                try:
                    price = self.parse_price(data.get('price', ''))
                    if not price:
                        continue
                    
                    original_price = self.parse_price(data.get('original_price', ''))
                    
                    # Parse discount percentage
                    discount_percent = None
                    discount_text = data.get('discount', '')
                    if discount_text:
                        match = re.search(r'(\d+)%', discount_text)
                        if match:
                            discount_percent = int(match.group(1))
                    
                    # Parse rating
                    rating = None
                    rating_text = data.get('rating', '')
                    if rating_text:
                        try:
                            match = re.search(r'[\d.]+', rating_text)
                            if match:
                                rating = float(match.group())
                        except (AttributeError, ValueError):
                            pass
                    
                    product = SearchResult(
                        title=data.get('title', ''),
                        price=price,
                        currency='PHP',
                        original_price=original_price,
                        discount_percent=discount_percent,
                        product_url=data.get('url', ''),
                        image_url=data.get('image', ''),
                        rating=rating,
                        sold_count=data.get('sold', ''),
                        location=data.get('location', ''),
                        store_name=data.get('store', ''),
                        is_official=data.get('is_official', False),
                        is_preferred=data.get('is_preferred', False),
                    )
                    result.products.append(product)
                except Exception as e:
                    logger.warning(f"Error parsing product data: {e}")
                    continue
            
            # Check pagination
            pagination_info = await self.page.evaluate("""
                () => {
                    const pagination = document.querySelector('.ant-pagination');
                    if (!pagination) return { hasNext: false, totalPages: 1 };
                    
                    const nextBtn = pagination.querySelector('.ant-pagination-next');
                    const hasNext = nextBtn && !nextBtn.classList.contains('ant-pagination-disabled');
                    
                    // Get total pages from last page number
                    const pageItems = pagination.querySelectorAll('.ant-pagination-item');
                    let totalPages = 1;
                    pageItems.forEach(item => {
                        const num = parseInt(item.getAttribute('title') || item.textContent);
                        if (!isNaN(num) && num > totalPages) {
                            totalPages = num;
                        }
                    });
                    
                    return { hasNext, totalPages };
                }
            """)
            
            result.has_next_page = pagination_info.get('hasNext', False)
            result.total_pages = pagination_info.get('totalPages', 1)
            
            logger.info(f"Lazada page {page}: Found {len(result.products)} products, "
                       f"has_next={result.has_next_page}, total_pages={result.total_pages}")
            
        except Exception as e:
            logger.error(f"Lazada scraping error: {e}")
            result.error = str(e)
        
        return result


async def scrape_lazada_search(
    search_term: str,
    max_pages: int = 10,
    delay: float = 5.0,
    headless: bool = True
) -> list[SearchResult]:
    """
    Convenience function to scrape Lazada search results.
    
    Args:
        search_term: What to search for
        max_pages: Maximum pages to scrape
        delay: Delay between pages in seconds
        headless: Run browser in headless mode
        
    Returns:
        List of SearchResult objects
    """
    async with LazadaScraper(delay=delay, headless=headless) as scraper:
        return await scraper.scrape_all_pages(search_term, max_pages)
