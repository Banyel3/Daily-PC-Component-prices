# Daily PC Component Prices

A price tracking application for PC components in the Philippines, monitoring prices from Lazada and Shopee.

## Features

- 📊 **Daily Price Tracking** - Automated scraping of PC component prices
- 🔍 **Search & Filter** - Query scraped products by category, store, price range
- 📈 **Price History** - Track price changes over time
- 🏷️ **Deal Detection** - Identify price drops and discounts
- 🛒 **Multi-Store Support** - Lazada PH & Shopee PH

## Tech Stack

- **Backend**: FastAPI, SQLModel, Celery, Redis, PostgreSQL
- **Frontend**: React, TypeScript, Vite, TailwindCSS
- **Scraping**: Playwright (for JS-rendered content)
- **Deployment**: Docker Compose

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Banyel3/Daily-PC-Component-prices.git
cd Daily-PC-Component-prices

# Start all services
docker-compose up -d

# Seed the database with stores
docker-compose exec backend python scripts/seed_database.py

# Setup default search configurations
curl -X POST http://localhost:8000/api/search-configs/setup-defaults
```

## Documentation

| Document                     | Description                             |
| ---------------------------- | --------------------------------------- |
| [Legal Compliance](LEGAL.md) | Robots.txt compliance & scraping ethics |
| [License](LICENSE)           | MIT License                             |

## API Endpoints

| Endpoint                              | Description                   |
| ------------------------------------- | ----------------------------- |
| `GET /api/products`                   | Query scraped products        |
| `GET /api/stores`                     | List all stores               |
| `GET /api/search-configs`             | View scraping configurations  |
| `POST /api/search-configs/scrape-all` | Trigger manual scrape (admin) |

## Legal & Compliance

This project respects robots.txt directives and implements conservative rate limiting. See [LEGAL.md](LEGAL.md) for full compliance details.

**Key Points:**

- ✅ 5-second delay between requests (exceeds robots.txt requirements)
- ✅ Only accesses publicly allowed endpoints
- ✅ No user-triggered scraping (scheduled only)
- ✅ No personal data collection

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
