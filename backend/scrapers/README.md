# BeautifulSoup Scraper - URL Import Guide

This guide explains how to import product URLs for the PC Component Price Tracker to scrape.

## Overview

The scraper uses BeautifulSoup to extract product information from retailer websites. URLs are imported into the database and scraped daily at **11:59 PM UTC**.

**Important:** The search functionality only works with already-scraped data from the current day. No on-demand scraping is performed.

## Supported Stores

The scraper has built-in CSS selectors for these stores:

| Store        | Domain          | Support Level                  |
| ------------ | --------------- | ------------------------------ |
| Newegg       | newegg.com      | ✅ Full                        |
| Amazon       | amazon.com      | ⚠️ Limited (anti-bot measures) |
| Best Buy     | bestbuy.com     | ✅ Full                        |
| Micro Center | microcenter.com | ✅ Full                        |

## URL Import Methods

### Method 1: JSON File Import (Recommended)

Create a JSON file with the following structure:

```json
[
  {
    "store_name": "Newegg",
    "category": "GPU",
    "brand": "NVIDIA",
    "urls": [
      "https://www.newegg.com/evga-geforce-rtx-4090-24g-p5-4981-kx/p/N82E16814487578",
      "https://www.newegg.com/msi-geforce-rtx-4080-rtx-4080-16g-gaming-x-trio/p/N82E16814137757"
    ]
  },
  {
    "store_name": "Best Buy",
    "category": "CPU",
    "brand": "AMD",
    "urls": [
      "https://www.bestbuy.com/site/amd-ryzen-9-7950x-16-core-32-thread-4-5ghz/6519873.p"
    ]
  }
]
```

Upload via API:

```bash
curl -X POST "http://localhost:8000/api/scrape-urls/import-json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@urls.json"
```

### Method 2: CSV File Import

Create a CSV file with these columns:

```csv
url,store_name,category,brand
https://www.newegg.com/product1,Newegg,GPU,NVIDIA
https://www.newegg.com/product2,Newegg,GPU,AMD
https://www.bestbuy.com/product1,Best Buy,CPU,Intel
```

### Method 3: Bulk API Import

Send a POST request with JSON body:

```bash
curl -X POST "http://localhost:8000/api/scrape-urls/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "Newegg",
    "category": "GPU",
    "brand": "NVIDIA",
    "urls": [
      "https://www.newegg.com/product-url-1",
      "https://www.newegg.com/product-url-2"
    ]
  }'
```

### Method 4: Single URL Import

```bash
curl -X POST "http://localhost:8000/api/scrape-urls" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.newegg.com/product-url",
    "store_id": "store-uuid-here",
    "category": "GPU",
    "brand": "NVIDIA"
  }'
```

## Categories

Use these standard category names:

- `GPU` - Graphics cards
- `CPU` - Processors
- `RAM` - Memory
- `Storage` - SSDs, HDDs
- `Motherboard` - Motherboards
- `Case` - Computer cases
- `PSU` - Power supplies
- `Cooling` - CPU coolers, fans
- `Monitor` - Displays
- `Other` - Miscellaneous

## How to Find Product URLs

### Newegg

1. Go to newegg.com
2. Search for the product
3. Click on the product to open its page
4. Copy the URL from your browser

Example URL format:

```
https://www.newegg.com/evga-geforce-rtx-4090/p/N82E16814487578
```

### Best Buy

1. Go to bestbuy.com
2. Navigate to the product
3. Copy the URL

Example URL format:

```
https://www.bestbuy.com/site/amd-ryzen-9-7950x/6519873.p
```

### Micro Center

1. Go to microcenter.com
2. Search and select the product
3. Copy the URL

Example URL format:

```
https://www.microcenter.com/product/649000/intel-core-i9-13900k
```

## Custom CSS Selectors

If the default selectors don't work for a specific product, you can provide custom selectors:

```json
{
  "store_name": "Newegg",
  "category": "GPU",
  "urls": ["https://www.newegg.com/special-product"],
  "selectors": {
    "name_selector": ".custom-product-title",
    "price_selector": ".custom-price-class",
    "image_selector": ".custom-image-class",
    "availability_selector": ".stock-status"
  }
}
```

### Default Selectors Reference

**Newegg:**

- Name: `h1.product-title`
- Price: `.price-current`
- Image: `.product-view-img-original`
- Availability: `.product-inventory`

**Best Buy:**

- Name: `.sku-title h1`
- Price: `.priceView-customer-price span`
- Image: `.primary-image`
- Availability: `.fulfillment-add-to-cart-button`

**Amazon:**

- Name: `#productTitle`
- Price: `.a-price .a-offscreen`
- Image: `#landingImage`
- Availability: `#availability`

**Micro Center:**

- Name: `h1.ProductLink`
- Price: `#pricing`
- Image: `#productImage`
- Availability: `.inventory`

## Prerequisites: Creating Stores

Before importing URLs, you must create the stores in the database:

```bash
# Create Newegg store
curl -X POST "http://localhost:8000/api/stores" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Newegg",
    "url": "https://www.newegg.com",
    "description": "Leading tech-focused e-retailer",
    "status": "active"
  }'

# Create Best Buy store
curl -X POST "http://localhost:8000/api/stores" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Best Buy",
    "url": "https://www.bestbuy.com",
    "description": "Consumer electronics retailer",
    "status": "active"
  }'

# Create Micro Center store
curl -X POST "http://localhost:8000/api/stores" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Micro Center",
    "url": "https://www.microcenter.com",
    "description": "Computer department store",
    "status": "active"
  }'
```

## Checking Import Status

View all imported URLs:

```bash
curl "http://localhost:8000/api/scrape-urls"
```

View URLs for a specific store:

```bash
curl "http://localhost:8000/api/scrape-urls?store_id=<store-uuid>"
```

## Error Handling

URLs that fail to scrape will have their `error_count` incremented. After 5 consecutive failures, the URL is automatically deactivated.

To reactivate a URL:

```bash
curl -X PATCH "http://localhost:8000/api/scrape-urls/<url-id>/toggle"
```

## Best Practices

1. **Start Small:** Import a few URLs first to test the selectors work correctly
2. **Use Consistent Categories:** Stick to the standard category names for filtering
3. **Verify Store Creation:** Ensure stores exist before importing URLs
4. **Monitor Errors:** Check the scrape URL status after the daily run
5. **Rate Limiting:** The scraper includes a 2-second delay between requests to avoid being blocked

## Troubleshooting

**URLs not scraping:**

- Check the store exists and is active
- Verify the URL is accessible in a browser
- Check if custom selectors are needed

**Missing data:**

- The website structure may have changed
- Try providing custom selectors
- Check the error logs in Docker

**Duplicate errors:**

- URLs are unique; attempting to add a duplicate will be skipped
