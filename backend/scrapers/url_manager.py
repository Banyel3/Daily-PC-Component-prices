"""
URL Manager for handling scrape URL import and management.
"""

import json
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path
from sqlmodel import Session, select

from backend.models.scrape_url import ScrapeURL
from backend.models.store import Store


class URLManager:
    """
    Manages scrape URLs including import from various formats.
    
    Supported import formats:
    - JSON file with structured data
    - CSV file with URL, store, category columns
    - Plain text file with one URL per line (requires store context)
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_store_by_name(self, name: str) -> Optional[Store]:
        """Find a store by name (case-insensitive)."""
        return self.session.exec(
            select(Store).where(Store.name.ilike(name))  # type: ignore[union-attr]
        ).first()
    
    def import_from_json(self, json_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Import URLs from JSON structure.
        
        Expected format:
        [
            {
                "store_name": "Newegg",
                "category": "GPU",
                "brand": "NVIDIA",  // optional
                "urls": [
                    "https://www.newegg.com/product1",
                    "https://www.newegg.com/product2"
                ],
                "selectors": {  // optional custom selectors
                    "name_selector": ".custom-name",
                    "price_selector": ".custom-price"
                }
            }
        ]
        """
        results = {
            "total_added": 0,
            "total_skipped": 0,
            "errors": []
        }
        
        for entry in json_data:
            store_name = entry.get("store_name")
            if not store_name:
                results["errors"].append("Missing store_name in entry")
                continue
            store = self.get_store_by_name(store_name)
            
            if not store:
                results["errors"].append(f"Store '{store_name}' not found")
                continue
            
            category = entry.get("category", "Other")
            brand = entry.get("brand")
            selectors = entry.get("selectors", {})
            
            for url in entry.get("urls", []):
                # Check for duplicate
                existing = self.session.exec(
                    select(ScrapeURL).where(ScrapeURL.url == url)
                ).first()
                
                if existing:
                    results["total_skipped"] += 1
                    continue
                
                scrape_url = ScrapeURL(
                    url=url,
                    store_id=store.id,
                    category=category,
                    brand=brand,
                    name_selector=selectors.get("name_selector"),
                    price_selector=selectors.get("price_selector"),
                    image_selector=selectors.get("image_selector"),
                    availability_selector=selectors.get("availability_selector"),
                )
                self.session.add(scrape_url)
                results["total_added"] += 1
        
        self.session.commit()
        return results
    
    def import_from_csv(self, csv_content: str) -> Dict[str, Any]:
        """
        Import URLs from CSV content.
        
        Expected columns: url, store_name, category, brand (optional)
        """
        results = {
            "total_added": 0,
            "total_skipped": 0,
            "errors": []
        }
        
        reader = csv.DictReader(csv_content.strip().split('\n'))
        
        for row in reader:
            url = row.get("url", "").strip()
            store_name = row.get("store_name", "").strip()
            category = row.get("category", "Other").strip()
            brand = row.get("brand", "").strip() or None
            
            if not url or not store_name:
                results["errors"].append(f"Invalid row: {row}")
                continue
            
            store = self.get_store_by_name(store_name)
            if not store:
                results["errors"].append(f"Store '{store_name}' not found for URL: {url}")
                continue
            
            # Check for duplicate
            existing = self.session.exec(
                select(ScrapeURL).where(ScrapeURL.url == url)
            ).first()
            
            if existing:
                results["total_skipped"] += 1
                continue
            
            scrape_url = ScrapeURL(
                url=url,
                store_id=store.id,
                category=category,
                brand=brand,
            )
            self.session.add(scrape_url)
            results["total_added"] += 1
        
        self.session.commit()
        return results
    
    def import_from_file(self, file_path: str) -> Dict[str, Any]:
        """Import URLs from a file (auto-detects format)."""
        path = Path(file_path)
        
        if not path.exists():
            return {"error": f"File not found: {file_path}"}
        
        content = path.read_text(encoding="utf-8")
        
        if path.suffix.lower() == ".json":
            data = json.loads(content)
            return self.import_from_json(data)
        elif path.suffix.lower() == ".csv":
            return self.import_from_csv(content)
        else:
            return {"error": f"Unsupported file format: {path.suffix}"}
    
    def get_active_urls(self, store_id: Optional[str] = None) -> List[ScrapeURL]:
        """Get all active scrape URLs, optionally filtered by store."""
        query = select(ScrapeURL).where(ScrapeURL.is_active == True)
        if store_id:
            query = query.where(ScrapeURL.store_id == store_id)
        return list(self.session.exec(query).all())
    
    def mark_url_error(self, url_id: str, error_message: str):
        """Mark a URL as having an error."""
        scrape_url = self.session.get(ScrapeURL, url_id)
        if scrape_url:
            scrape_url.last_error = error_message
            scrape_url.error_count += 1
            
            # Deactivate after too many errors
            if scrape_url.error_count >= 5:
                scrape_url.is_active = False
            
            self.session.add(scrape_url)
            self.session.commit()
    
    def mark_url_success(self, url_id: str):
        """Mark a URL as successfully scraped."""
        from datetime import datetime
        
        scrape_url = self.session.get(ScrapeURL, url_id)
        if scrape_url:
            scrape_url.last_scraped = datetime.utcnow()
            scrape_url.last_error = None
            scrape_url.error_count = 0
            self.session.add(scrape_url)
            self.session.commit()
