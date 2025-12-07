# PC Component Price Tracker

A full-stack web application that tracks PC component prices across multiple retailers with daily automated scraping using Celery and BeautifulSoup.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Compose                            │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│   Frontend  │   Backend   │   Celery    │   Celery    │         │
│   (React)   │  (FastAPI)  │   Worker    │    Beat     │  Redis  │
│    :80      │    :8000    │             │             │  :6379  │
├─────────────┴─────────────┴─────────────┴─────────────┴─────────┤
│                         PostgreSQL :5432                         │
│                    (Persistent Price History)                    │
└─────────────────────────────────────────────────────────────────┘
```

## ✨ Features

- **Daily Automated Scraping:** Products are scraped at 11:59 PM UTC daily
- **Price History Tracking:** All prices are stored for trend analysis
- **Dynamic Frontend:** Categories, stores, and filters populated from the database
- **Search Functionality:** Search operates on the current day's scraped data only
- **Price Drop Alerts:** Dashboard highlights biggest price drops
- **Multi-Store Support:** Newegg, Best Buy, Micro Center (Amazon limited due to anti-bot)
- **Export Tools:** Manual export scripts for price history backup

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### 1. Clone and Configure

```bash
git clone <repository-url>
cd Daily-PC-Component-prices

# Create environment file
cp .env.example .env

# Edit .env with your settings (especially POSTGRES_PASSWORD)
```

### 2. Start All Services

```bash
docker-compose up -d
```

This starts:

- **Frontend:** http://localhost (port 80)
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- PostgreSQL, Redis, Celery Worker, Celery Beat

### 3. Initialize Stores

Before importing URLs, create the stores:

```bash
# Create Newegg
curl -X POST "http://localhost:8000/api/stores" \
  -H "Content-Type: application/json" \
  -d '{"name": "Newegg", "url": "https://www.newegg.com", "description": "Tech-focused e-retailer", "status": "active"}'

# Create Best Buy
curl -X POST "http://localhost:8000/api/stores" \
  -H "Content-Type: application/json" \
  -d '{"name": "Best Buy", "url": "https://www.bestbuy.com", "description": "Electronics retailer", "status": "active"}'

# Create Micro Center
curl -X POST "http://localhost:8000/api/stores" \
  -H "Content-Type: application/json" \
  -d '{"name": "Micro Center", "url": "https://www.microcenter.com", "description": "Computer store", "status": "active"}'
```

### 4. Import Product URLs

See [Scraper README](backend/scrapers/README.md) for detailed import instructions.

Quick example:

```bash
curl -X POST "http://localhost:8000/api/scrape-urls/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "Newegg",
    "category": "GPU",
    "urls": ["https://www.newegg.com/your-product-url"]
  }'
```

## 📁 Project Structure

```
Daily-PC-Component-prices/
├── docker-compose.yml          # All services orchestration
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
│
├── backend/
│   ├── Dockerfile
│   ├── main.py                 # FastAPI application
│   ├── database.py             # SQLModel connection
│   ├── config.py               # Configuration
│   ├── celery_app.py           # Celery configuration (11:59 PM schedule)
│   │
│   ├── models/                 # SQLModel database models
│   │   ├── product.py          # Product with price tracking
│   │   ├── store.py            # Retailer stores
│   │   ├── price_history.py    # Historical prices
│   │   └── scrape_url.py       # URLs to scrape
│   │
│   ├── routes/                 # API endpoints
│   │   ├── products.py         # GET /api/products (today's data)
│   │   ├── stores.py           # GET /api/stores
│   │   ├── stats.py            # GET /api/stats, /api/stats/top-deals
│   │   └── scrape_urls.py      # Manage scrape URLs
│   │
│   ├── scrapers/
│   │   ├── README.md           # URL import documentation
│   │   ├── base_scraper.py     # BeautifulSoup scraper
│   │   └── url_manager.py      # URL import utilities
│   │
│   └── tasks/
│       └── scraping_task.py    # Celery scraping task
│
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf              # Production server config
│   ├── src/
│   │   ├── api/index.ts        # API client
│   │   ├── hooks/              # React hooks for data fetching
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx   # Stats & top deals
│   │   │   ├── Products.tsx    # Product grid with search
│   │   │   └── Stores.tsx      # Store listings
│   │   └── layouts/
│   │       └── DashboardLayout.tsx
│
└── scripts/
    └── export_price_history.py # Manual database export
```

## 🔧 API Endpoints

### Products

- `GET /api/products` - Get today's products (with filters)
- `GET /api/products?q=rtx` - Search in product names
- `GET /api/products?category=GPU&store=Newegg` - Filter by category/store
- `GET /api/products/{id}` - Get single product
- `GET /api/products/{id}/history` - Get price history

### Stores

- `GET /api/stores` - List all stores
- `POST /api/stores` - Create store
- `PUT /api/stores/{id}` - Update store
- `DELETE /api/stores/{id}` - Delete store

### Stats

- `GET /api/stats` - Today's statistics
- `GET /api/stats/top-deals` - Biggest price drops
- `GET /api/stats/by-category` - Stats per category

### Scrape URLs

- `GET /api/scrape-urls` - List all URLs
- `POST /api/scrape-urls` - Add single URL
- `POST /api/scrape-urls/bulk` - Bulk import
- `POST /api/scrape-urls/import-json` - Import from JSON file
- `PATCH /api/scrape-urls/{id}/toggle` - Toggle active status

## 📊 Exporting Price History

Manually export your price history for backup:

```bash
# Export to JSON
docker-compose exec backend python scripts/export_price_history.py --format json --output /app/exports

# Export to CSV
docker-compose exec backend python scripts/export_price_history.py --format csv --output /app/exports

# Export last 90 days only
docker-compose exec backend python scripts/export_price_history.py --format both --days 90

# Export summary
docker-compose exec backend python scripts/export_price_history.py --format summary
```

Exports are saved to the `./exports/` directory (mounted volume).

## ⏰ Scheduled Scraping

The Celery Beat scheduler runs the scraping task daily at **11:59 PM UTC**.

To manually trigger a scrape (for testing):

```bash
docker-compose exec celery-worker celery -A backend.celery_app:celery_app call backend.tasks.scraping_task.scrape_all_products
```

## 🔍 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat
docker-compose logs -f backend
```

### Check Service Status

```bash
docker-compose ps
```

### Database Access

```bash
docker-compose exec postgres psql -U postgres -d pc_prices
```

## 🛠️ Development

### Run Without Docker (Development)

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Start PostgreSQL and Redis locally or via Docker:

```bash
docker-compose up -d postgres redis
```

3. Run backend:

```bash
cd backend
uvicorn main:app --reload
```

4. Run frontend:

```bash
cd frontend
npm install
npm run dev
```

5. Run Celery worker:

```bash
celery -A backend.celery_app:celery_app worker --loglevel=info
```

6. Run Celery beat:

```bash
celery -A backend.celery_app:celery_app beat --loglevel=info
```

## 📝 Environment Variables

| Variable               | Default              | Description                     |
| ---------------------- | -------------------- | ------------------------------- |
| `POSTGRES_USER`        | postgres             | Database user                   |
| `POSTGRES_PASSWORD`    | postgres             | Database password               |
| `POSTGRES_DB`          | pc_prices            | Database name                   |
| `REDIS_URL`            | redis://redis:6379/0 | Redis connection URL            |
| `DATABASE_URL`         | postgresql://...     | Full database URL               |
| `CORS_ORIGINS`         | http://localhost,... | Allowed CORS origins            |
| `SCRAPE_DELAY_SECONDS` | 2.0                  | Delay between scrape requests   |
| `USER_AGENT`           | Mozilla/5.0...       | Browser user agent for scraping |

## ⚠️ Important Notes

1. **Search Limitation:** Search only works on the current day's scraped data. No on-demand scraping is performed.

2. **Price Change Calculation:** `priceChange` is calculated as the percentage difference between today's price and yesterday's price.

3. **Anti-Bot Measures:** Amazon has strict anti-bot protections. Consider using a rotating proxy service for reliable Amazon scraping.

4. **Data Retention:** All price history is stored indefinitely. Use the export script to backup and manually manage data.

5. **Rate Limiting:** Built-in 2-second delay between requests. Adjust `SCRAPE_DELAY_SECONDS` if needed.

## 📄 License

See [LICENSE](LICENSE) file.
