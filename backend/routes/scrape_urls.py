from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List, Optional
import json
import csv
import io

from backend.database import get_session
from backend.models.scrape_url import ScrapeURL, ScrapeURLCreate, ScrapeURLRead, ScrapeURLBulkImport
from backend.models.store import Store

router = APIRouter(prefix="/api/scrape-urls", tags=["scrape-urls"])

@router.get("/", response_model=List[ScrapeURLRead])
def get_scrape_urls(
    session: Session = Depends(get_session),
    store_id: Optional[str] = None,
    category: Optional[str] = None,
    active_only: bool = True
):
    """Get all scrape URLs with optional filters."""
    query = select(ScrapeURL)
    
    if store_id:
        query = query.where(ScrapeURL.store_id == store_id)
    if category:
        query = query.where(ScrapeURL.category == category)
    if active_only:
        query = query.where(ScrapeURL.is_active == True)
    
    return session.exec(query).all()


@router.post("/", response_model=ScrapeURLRead)
def create_scrape_url(
    url_data: ScrapeURLCreate,
    session: Session = Depends(get_session)
):
    """Add a single URL to scrape."""
    # Verify store exists
    store = session.get(Store, url_data.store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Check for duplicate URL
    existing = session.exec(
        select(ScrapeURL).where(ScrapeURL.url == url_data.url)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="URL already exists")
    
    scrape_url = ScrapeURL(**url_data.model_dump())
    session.add(scrape_url)
    session.commit()
    session.refresh(scrape_url)
    return scrape_url


@router.post("/bulk")
def bulk_import_urls(
    import_data: ScrapeURLBulkImport,
    session: Session = Depends(get_session)
):
    """
    Bulk import URLs for a specific store and category.
    
    Expected format:
    {
        "store_name": "Newegg",
        "category": "GPU",
        "brand": "NVIDIA",  // optional
        "urls": [
            "https://www.newegg.com/product1",
            "https://www.newegg.com/product2"
        ]
    }
    """
    # Find store by name
    store = session.exec(
        select(Store).where(Store.name == import_data.store_name)
    ).first()
    
    if not store:
        raise HTTPException(
            status_code=404,
            detail=f"Store '{import_data.store_name}' not found. Create the store first."
        )
    
    added = 0
    skipped = 0
    errors = []
    
    for url in import_data.urls:
        # Check for duplicate
        existing = session.exec(
            select(ScrapeURL).where(ScrapeURL.url == url)
        ).first()
        
        if existing:
            skipped += 1
            continue
        
        try:
            scrape_url = ScrapeURL(
                url=url,
                store_id=store.id,
                category=import_data.category,
                brand=import_data.brand
            )
            session.add(scrape_url)
            added += 1
        except Exception as e:
            errors.append({"url": url, "error": str(e)})
    
    session.commit()
    
    return {
        "message": f"Import complete. Added: {added}, Skipped (duplicates): {skipped}",
        "added": added,
        "skipped": skipped,
        "errors": errors
    }


@router.post("/import-json")
async def import_from_json(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Import URLs from a JSON file.
    
    Expected JSON format:
    [
        {
            "store_name": "Newegg",
            "category": "GPU",
            "brand": "NVIDIA",
            "urls": ["url1", "url2"]
        },
        {
            "store_name": "Amazon",
            "category": "CPU",
            "urls": ["url3", "url4"]
        }
    ]
    """
    content = await file.read()
    
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    
    total_added = 0
    total_skipped = 0
    results = []
    
    for entry in data:
        # Find store
        store = session.exec(
            select(Store).where(Store.name == entry.get("store_name"))
        ).first()
        
        if not store:
            results.append({
                "store": entry.get("store_name"),
                "error": "Store not found"
            })
            continue
        
        added = 0
        skipped = 0
        
        for url in entry.get("urls", []):
            existing = session.exec(
                select(ScrapeURL).where(ScrapeURL.url == url)
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            scrape_url = ScrapeURL(
                url=url,
                store_id=store.id,
                category=entry.get("category", "Other"),
                brand=entry.get("brand")
            )
            session.add(scrape_url)
            added += 1
        
        total_added += added
        total_skipped += skipped
        results.append({
            "store": entry.get("store_name"),
            "category": entry.get("category"),
            "added": added,
            "skipped": skipped
        })
    
    session.commit()
    
    return {
        "total_added": total_added,
        "total_skipped": total_skipped,
        "details": results
    }


@router.delete("/{url_id}")
def delete_scrape_url(url_id: str, session: Session = Depends(get_session)):
    """Delete a scrape URL."""
    scrape_url = session.get(ScrapeURL, url_id)
    if not scrape_url:
        raise HTTPException(status_code=404, detail="Scrape URL not found")
    
    session.delete(scrape_url)
    session.commit()
    return {"message": "Scrape URL deleted"}


@router.patch("/{url_id}/toggle")
def toggle_scrape_url(url_id: str, session: Session = Depends(get_session)):
    """Toggle a scrape URL's active status."""
    scrape_url = session.get(ScrapeURL, url_id)
    if not scrape_url:
        raise HTTPException(status_code=404, detail="Scrape URL not found")
    
    scrape_url.is_active = not scrape_url.is_active
    session.add(scrape_url)
    session.commit()
    session.refresh(scrape_url)
    
    return {"message": f"URL {'activated' if scrape_url.is_active else 'deactivated'}", "is_active": scrape_url.is_active}
