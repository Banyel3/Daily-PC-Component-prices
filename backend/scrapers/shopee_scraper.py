"""
Shopee PH scraper using Playwright.
Handles search-based product discovery with pagination.
"""

import logging
import re
from typing import Optional
from urllib.parse import urlencode, quote_plus

from .playwright_base import PlaywrightBaseScraper, SearchResult, SearchPageResult

logger = logging.getLogger(__name__)


class ShopeeScraper(PlaywrightBaseScraper):
    """
    Scraper for Shopee Philippines (shopee.ph).
    
    Search URL format: https://shopee.ph/search?keyword={query}&page={page}
    Note: Shopee uses 0-indexed pagination
    """
    
    BASE_URL = "https://shopee.ph"
    
    # CSS Selectors for Shopee search results
    SELECTORS = {
        # Product grid
        "product_grid": ".shopee-search-item-result__items",
        "product_item": ".shopee-search-item-result__item",
        
        # Alternative selectors
        "product_card": "[data-sqe='item']",
        "product_link": "a[data-sqe='link']",
        
        # Product details
        "title": ".Cve6sh, .ie3A\\+n, [data-sqe='name']",
        "price": ".ZEgDH9, .vioxXd, [data-sqe='price']",
        "original_price": ".Lmw3ax, .price--original",
        "discount": ".IY7Jxq, .percent-discount",
        "image": "img.jFEiVQ, img[data-sqe='image']",
        "rating": ".shopee-rating-stars, [data-sqe='rating']",
        "sold": ".OwmBnn, .r6HknA, [data-sqe='sold']",
        "location": ".zGGwiV, .lt\\+XtK",
        
        # Shop badges
        "mall_badge": ".shopee-badge--mall, .official-shop-badge",
        "preferred_badge": ".shopee-badge--preferred",
        
        # Pagination
        "pagination": ".shopee-page-controller",
        "next_page": ".shopee-icon-button--right:not(.shopee-icon-button--disabled)",
        "current_page": ".shopee-button-solid--primary",
    }
    
    def build_search_url(self, search_term: str, page: int = 1) -> str:
        """
        Build Shopee search URL.
        Note: Shopee uses 0-indexed pages in URL but we use 1-indexed externally.
        """
        params = {
            'keyword': search_term,
            'page': page - 1,  # Convert to 0-indexed
        }
        return f"{self.BASE_URL}/search?{urlencode(params)}"
    
    async def search_products(self, search_term: str, page: int = 1) -> SearchPageResult:
        """
        Search for products on Shopee PH.
        
        Args:
            search_term: The search query (e.g., "graphics card", "RTX 4090")
            page: Page number (1-indexed, will be converted to 0-indexed for Shopee)
            
        Returns:
            SearchPageResult with products and pagination info
        """
        url = self.build_search_url(search_term, page)
        result = SearchPageResult(page_number=page)
        
        logger.info(f"Shopee search: {url}")
        
        try:
            # Navigate to search page
            success = await self.navigate_to(url)
            if not success:
                result.error = "Failed to load search page"
                return result
            
            # Shopee is very JS-heavy, give it more time to render
            assert self.page is not None  # For type checker
            await self.page.wait_for_timeout(3000)
            
            # Scroll multiple times to trigger lazy loading
            for _ in range(5):
                await self.page.evaluate("window.scrollBy(0, 500)")
                await self.page.wait_for_timeout(300)
            
            # Scroll back to top
            await self.page.evaluate("window.scrollTo(0, 0)")
            await self.page.wait_for_timeout(500)
            
            # Extract products using JavaScript evaluation
            products_data = await self.page.evaluate("""
                () => {
                    const products = [];
                    
                    // Try multiple selector strategies for Shopee
                    const selectors = [
                        '.shopee-search-item-result__item',
                        '[data-sqe="item"]',
                        '.col-xs-2-4',  // Grid layout selector
                    ];
                    
                    let items = [];
                    for (const selector of selectors) {
                        items = document.querySelectorAll(selector);
                        if (items.length > 0) break;
                    }
                    
                    // Alternative: look for all links with product URL pattern
                    if (items.length === 0) {
                        const productLinks = document.querySelectorAll('a[href*="-i."]');
                        items = Array.from(productLinks).map(link => link.closest('[class*="col"]') || link.parentElement);
                        items = items.filter(item => item !== null);
                    }
                    
                    items.forEach(item => {
                        try {
                            // Get link - Shopee product URLs have format: /product-name-i.shopid.itemid
                            const linkEl = item.querySelector('a[href*="-i."]') ||
                                          item.querySelector('a[data-sqe="link"]') ||
                                          item.querySelector('a');
                            
                            // Get title from various possible locations
                            const titleEl = item.querySelector('.Cve6sh') ||
                                           item.querySelector('.ie3A\\+n') ||
                                           item.querySelector('[data-sqe="name"]') ||
                                           item.querySelector('.yQmmFK') ||
                                           item.querySelector('div[style*="line-clamp"]') ||
                                           linkEl;
                            
                            // Get prices
                            const priceEl = item.querySelector('.ZEgDH9') ||
                                           item.querySelector('.vioxXd') ||
                                           item.querySelector('[data-sqe="price"]') ||
                                           item.querySelector('.k9JZlv');
                            
                            const originalPriceEl = item.querySelector('.Lmw3ax') ||
                                                   item.querySelector('.price--original');
                            
                            const discountEl = item.querySelector('.IY7Jxq') ||
                                              item.querySelector('.percent-discount') ||
                                              item.querySelector('[data-sqe="discount"]');
                            
                            // Get image
                            const imgEl = item.querySelector('img.jFEiVQ') ||
                                         item.querySelector('img[data-sqe="image"]') ||
                                         item.querySelector('img');
                            
                            // Get sold count
                            const soldEl = item.querySelector('.OwmBnn') ||
                                          item.querySelector('.r6HknA') ||
                                          item.querySelector('[data-sqe="sold"]');
                            
                            // Get location
                            const locationEl = item.querySelector('.zGGwiV') ||
                                              item.querySelector('.lt\\+XtK');
                            
                            // Get rating
                            const ratingEl = item.querySelector('.shopee-rating-stars') ||
                                            item.querySelector('[data-sqe="rating"]');
                            
                            // Check for badges
                            const isMall = item.querySelector('.shopee-badge--mall') !== null ||
                                          item.textContent.includes('Mall');
                            const isPreferred = item.querySelector('.shopee-badge--preferred') !== null ||
                                               item.textContent.includes('Preferred');
                            
                            // Extract text content
                            let title = '';
                            if (titleEl) {
                                title = titleEl.textContent?.trim() ||
                                       titleEl.getAttribute('title') ||
                                       titleEl.innerText?.trim() || '';
                            }
                            
                            const product = {
                                title: title,
                                price: priceEl?.textContent?.trim() || '',
                                original_price: originalPriceEl?.textContent?.trim() || '',
                                discount: discountEl?.textContent?.trim() || '',
                                url: linkEl?.href || '',
                                image: imgEl?.src || imgEl?.dataset?.src || '',
                                rating: ratingEl?.textContent?.trim() || ratingEl?.getAttribute('style') || '',
                                sold: soldEl?.textContent?.trim() || '',
                                location: locationEl?.textContent?.trim() || '',
                                is_mall: isMall,
                                is_preferred: isPreferred,
                            };
                            
                            // Only add if we have basic required data
                            if (product.title && product.url && product.url.includes('-i.')) {
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
                    price = self.parse_shopee_price(data.get('price', ''))
                    if not price:
                        continue
                    
                    original_price = self.parse_shopee_price(data.get('original_price', ''))
                    
                    # Parse discount percentage
                    discount_percent = None
                    discount_text = data.get('discount', '')
                    if discount_text:
                        match = re.search(r'(\d+)%', discount_text)
                        if match:
                            discount_percent = int(match.group(1))
                    
                    # Parse rating from style or text
                    rating = None
                    rating_text = data.get('rating', '')
                    if rating_text:
                        # Try to parse from width percentage (Shopee uses stars width)
                        width_match = re.search(r'width:\s*([\d.]+)%', rating_text)
                        if width_match:
                            rating = float(width_match.group(1)) / 20  # Convert to 5-star scale
                        else:
                            try:
                                match = re.search(r'[\d.]+', rating_text)
                                if match:
                                    rating = float(match.group())
                            except (AttributeError, ValueError):
                                pass
                    
                    # Parse sold count
                    sold_count = data.get('sold', '')
                    if sold_count:
                        # Clean up "X sold" format
                        sold_count = sold_count.replace('sold', '').replace('Sold', '').strip()
                    
                    product = SearchResult(
                        title=data.get('title', ''),
                        price=price,
                        currency='PHP',
                        original_price=original_price,
                        discount_percent=discount_percent,
                        product_url=data.get('url', ''),
                        image_url=data.get('image', ''),
                        rating=rating,
                        sold_count=sold_count if sold_count else None,
                        location=data.get('location', ''),
                        is_official=data.get('is_mall', False),
                        is_preferred=data.get('is_preferred', False),
                    )
                    result.products.append(product)
                except Exception as e:
                    logger.warning(f"Error parsing product data: {e}")
                    continue
            
            # Check pagination
            pagination_info = await self.page.evaluate("""
                () => {
                    // Look for pagination controller
                    const pagination = document.querySelector('.shopee-page-controller') ||
                                      document.querySelector('[class*="pagination"]');
                    
                    if (!pagination) {
                        // Check if there are more results by looking for next button
                        const nextBtn = document.querySelector('.shopee-icon-button--right');
                        return { 
                            hasNext: nextBtn && !nextBtn.classList.contains('shopee-icon-button--disabled'),
                            totalPages: 1 
                        };
                    }
                    
                    // Get next button state
                    const nextBtn = pagination.querySelector('.shopee-icon-button--right') ||
                                   pagination.querySelector('[class*="next"]');
                    const hasNext = nextBtn && 
                                   !nextBtn.classList.contains('shopee-icon-button--disabled') &&
                                   !nextBtn.disabled;
                    
                    // Try to get total pages
                    const pageButtons = pagination.querySelectorAll('button.shopee-button-no-outline');
                    let totalPages = 1;
                    pageButtons.forEach(btn => {
                        const num = parseInt(btn.textContent);
                        if (!isNaN(num) && num > totalPages) {
                            totalPages = num;
                        }
                    });
                    
                    return { hasNext, totalPages };
                }
            """)
            
            result.has_next_page = pagination_info.get('hasNext', False)
            result.total_pages = pagination_info.get('totalPages', 1)
            
            logger.info(f"Shopee page {page}: Found {len(result.products)} products, "
                       f"has_next={result.has_next_page}, total_pages={result.total_pages}")
            
        except Exception as e:
            logger.error(f"Shopee scraping error: {e}")
            result.error = str(e)
        
        return result
    
    def parse_shopee_price(self, price_text: str) -> Optional[float]:
        """Parse Shopee price format."""
        if not price_text:
            return None
        
        # Shopee formats: ₱1,234 or ₱1,234 - ₱5,678 (price range)
        cleaned = price_text.replace('₱', '').replace('PHP', '').replace(',', '').strip()
        
        # Handle price ranges - take the lower price
        if ' - ' in cleaned:
            cleaned = cleaned.split(' - ')[0].strip()
        elif '-' in cleaned and cleaned.count('-') == 1:
            cleaned = cleaned.split('-')[0].strip()
        
        try:
            return float(cleaned)
        except ValueError:
            logger.warning(f"Could not parse Shopee price: {price_text}")
            return None


async def scrape_shopee_search(
    search_term: str,
    max_pages: int = 10,
    delay: float = 5.0,
    headless: bool = True
) -> list[SearchResult]:
    """
    Convenience function to scrape Shopee search results.
    
    Args:
        search_term: What to search for
        max_pages: Maximum pages to scrape
        delay: Delay between pages in seconds
        headless: Run browser in headless mode
        
    Returns:
        List of SearchResult objects
    """
    async with ShopeeScraper(delay=delay, headless=headless) as scraper:
        return await scraper.scrape_all_pages(search_term, max_pages)
