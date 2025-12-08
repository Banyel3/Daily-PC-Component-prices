#!/usr/bin/env python3
"""
Database Seed Script

Seeds the database with initial stores for the PC Component Price Tracker.
Run this after starting the services to set up the base data.

Usage:
    python scripts/seed_database.py
"""

from sqlmodel import Session, create_engine, select
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.store import Store
from backend.config import DATABASE_URL


# Initial stores to seed
INITIAL_STORES = [
    {
        "name": "Newegg",
        "url": "https://www.newegg.com",
        "description": "Leading tech-focused e-retailer in North America.",
        "status": "active",
    },
    {
        "name": "Best Buy",
        "url": "https://www.bestbuy.com",
        "description": "Consumer electronics retailer with both online and physical stores.",
        "status": "active",
    },
    {
        "name": "Micro Center",
        "url": "https://www.microcenter.com",
        "description": "Computer department store known for in-store deals and bundles.",
        "status": "active",
    },
    {
        "name": "Amazon",
        "url": "https://www.amazon.com",
        "description": "Global e-commerce giant with a vast selection of PC components.",
        "status": "active",
    },
    # Philippine e-commerce stores for search-based scraping
    {
        "name": "Lazada Philippines",
        "url": "https://www.lazada.com.ph",
        "description": "Leading Southeast Asian e-commerce platform. Supports automated search scraping.",
        "status": "active",
    },
    {
        "name": "Shopee Philippines",
        "url": "https://shopee.ph",
        "description": "Popular Southeast Asian e-commerce and social commerce platform. Supports automated search scraping.",
        "status": "active",
    },
]


def seed_stores(session: Session) -> dict:
    """Seed the database with initial stores."""
    results = {"added": 0, "skipped": 0}
    
    for store_data in INITIAL_STORES:
        # Check if store already exists
        existing = session.exec(
            select(Store).where(Store.name == store_data["name"])
        ).first()
        
        if existing:
            print(f"  ⏭️  Store '{store_data['name']}' already exists, skipping...")
            results["skipped"] += 1
            continue
        
        store = Store(
            name=store_data["name"],
            url=store_data["url"],
            description=store_data.get("description"),
            status=store_data.get("status", "active"),
        )
        session.add(store)
        print(f"  ✅ Created store: {store_data['name']}")
        results["added"] += 1
    
    session.commit()
    return results


def main():
    print("\n🌱 PC Component Price Tracker - Database Seeder\n")
    print(f"Database: {DATABASE_URL}\n")
    
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as session:
        print("📦 Seeding stores...")
        store_results = seed_stores(session)
        print(f"\n   Added: {store_results['added']}, Skipped: {store_results['skipped']}")
    
    print("\n✓ Database seeding complete!\n")
    print("Next steps:")
    print("  1. Import product URLs using the API")
    print("  2. See backend/scrapers/README.md for URL import instructions")
    print("  3. Wait for the daily scrape at 11:59 PM UTC, or trigger manually\n")


if __name__ == "__main__":
    main()
