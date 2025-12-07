#!/usr/bin/env python3
"""
Price History Export Script

This script exports the price history database to JSON or CSV format.
Run manually to backup your price data before any cleanup operations.

Usage:
    python scripts/export_price_history.py --format json --output ./exports/
    python scripts/export_price_history.py --format csv --output ./exports/
    python scripts/export_price_history.py --format both --days 90
"""

import argparse
import json
import csv
import os
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

from sqlmodel import Session, select, create_engine

# Import models
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.product import Product
from backend.models.store import Store
from backend.models.price_history import PriceHistory
from backend.config import DATABASE_URL


def get_engine():
    """Create database engine."""
    return create_engine(DATABASE_URL)


def export_to_json(session: Session, output_dir: Path, days: Optional[int] = None) -> str:
    """Export price history to JSON format."""
    query = (
        select(PriceHistory, Product, Store)
        .join(Product, PriceHistory.product_id == Product.id)  # type: ignore[arg-type]
        .join(Store, Product.store_id == Store.id)  # type: ignore[arg-type]
    )
    
    if days:
        cutoff_date = date.today() - timedelta(days=days)
        query = query.where(PriceHistory.recorded_date >= cutoff_date)
    
    query = query.order_by(PriceHistory.recorded_date.desc())  # type: ignore[union-attr]
    results = session.exec(query).all()
    
    # Group by product
    products_data = {}
    for history, product, store in results:
        if product.id not in products_data:
            products_data[product.id] = {
                "product_id": product.id,
                "name": product.name,
                "category": product.category,
                "brand": product.brand,
                "store": store.name,
                "url": product.url,
                "current_price": product.current_price,
                "currency": product.currency,
                "price_history": []
            }
        
        products_data[product.id]["price_history"].append({
            "date": history.recorded_date.isoformat(),
            "price": history.price,
            "was_available": history.was_available,
            "recorded_at": history.recorded_at.isoformat()
        })
    
    # Create export data
    export_data = {
        "export_date": datetime.utcnow().isoformat(),
        "total_products": len(products_data),
        "total_price_entries": len(results),
        "date_range": {
            "days_included": days or "all",
            "from_date": (date.today() - timedelta(days=days)).isoformat() if days else "beginning",
            "to_date": date.today().isoformat()
        },
        "products": list(products_data.values())
    }
    
    # Write to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"price_history_export_{timestamp}.json"
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    return str(filepath)


def export_to_csv(session: Session, output_dir: Path, days: Optional[int] = None) -> str:
    """Export price history to CSV format."""
    query = (
        select(PriceHistory, Product, Store)
        .join(Product, PriceHistory.product_id == Product.id)  # type: ignore[arg-type]
        .join(Store, Product.store_id == Store.id)  # type: ignore[arg-type]
    )
    
    if days:
        cutoff_date = date.today() - timedelta(days=days)
        query = query.where(PriceHistory.recorded_date >= cutoff_date)
    
    query = query.order_by(PriceHistory.recorded_date.desc())  # type: ignore[union-attr]
    results = session.exec(query).all()
    
    # Create CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"price_history_export_{timestamp}.csv"
    filepath = output_dir / filename
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            "product_id",
            "product_name",
            "category",
            "brand",
            "store",
            "product_url",
            "current_price",
            "currency",
            "history_date",
            "history_price",
            "was_available",
            "recorded_at"
        ])
        
        # Data rows
        for history, product, store in results:
            writer.writerow([
                product.id,
                product.name,
                product.category,
                product.brand,
                store.name,
                product.url,
                product.current_price,
                product.currency,
                history.recorded_date.isoformat(),
                history.price,
                history.was_available,
                history.recorded_at.isoformat()
            ])
    
    return str(filepath)


def export_summary(session: Session, output_dir: Path) -> str:
    """Export a summary report of the database."""
    from sqlmodel import func, col
    
    # Get statistics
    total_products = session.exec(select(func.count(col(Product.id)))).one()
    total_stores = session.exec(select(func.count(col(Store.id)))).one()
    total_history = session.exec(select(func.count(col(PriceHistory.id)))).one()
    
    # Date range
    oldest_record = session.exec(
        select(col(PriceHistory.recorded_date))  # type: ignore[call-overload]
        .order_by(col(PriceHistory.recorded_date).asc())
        .limit(1)
    ).first()
    
    newest_record = session.exec(
        select(col(PriceHistory.recorded_date))  # type: ignore[call-overload]
        .order_by(col(PriceHistory.recorded_date).desc())
        .limit(1)
    ).first()
    
    # Products per category
    category_counts = session.exec(
        select(col(Product.category), func.count(col(Product.id)))  # type: ignore[call-overload]
        .group_by(col(Product.category))
    ).all()
    
    summary = {
        "export_date": datetime.utcnow().isoformat(),
        "database_statistics": {
            "total_products": total_products,
            "total_stores": total_stores,
            "total_price_history_entries": total_history
        },
        "date_range": {
            "oldest_record": oldest_record.isoformat() if oldest_record else None,
            "newest_record": newest_record.isoformat() if newest_record else None
        },
        "products_by_category": {cat: count for cat, count in category_counts}
    }
    
    # Write summary
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"database_summary_{timestamp}.json"
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    return str(filepath)


def main():
    parser = argparse.ArgumentParser(
        description="Export price history database to JSON or CSV format"
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv", "both", "summary"],
        default="json",
        help="Export format (default: json)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./exports",
        help="Output directory (default: ./exports)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Only export data from the last N days (default: all)"
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    engine = get_engine()
    
    print(f"Connecting to database...")
    print(f"Export format: {args.format}")
    print(f"Output directory: {output_dir.absolute()}")
    if args.days:
        print(f"Date filter: Last {args.days} days")
    
    with Session(engine) as session:
        exported_files = []
        
        if args.format in ["json", "both"]:
            print("\nExporting to JSON...")
            json_file = export_to_json(session, output_dir, args.days)
            exported_files.append(json_file)
            print(f"  Created: {json_file}")
        
        if args.format in ["csv", "both"]:
            print("\nExporting to CSV...")
            csv_file = export_to_csv(session, output_dir, args.days)
            exported_files.append(csv_file)
            print(f"  Created: {csv_file}")
        
        if args.format == "summary" or args.format == "both":
            print("\nExporting summary...")
            summary_file = export_summary(session, output_dir)
            exported_files.append(summary_file)
            print(f"  Created: {summary_file}")
    
    print(f"\n✓ Export completed successfully!")
    print(f"  Files created: {len(exported_files)}")
    for f in exported_files:
        print(f"    - {f}")


if __name__ == "__main__":
    main()
