"""
API routes for search configuration management.
CRUD operations for SearchConfig and search scraping triggers.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from backend.database import get_session
from backend.models.search_config import (
    SearchConfig, SearchConfigCreate, SearchConfigRead, SearchConfigUpdate,
    ComponentCategory, CATEGORY_SEARCH_TERMS
)
from backend.models.store import Store
from backend.tasks.search_task import (
    scrape_search_config,
    scrape_all_search_configs,
    create_default_search_configs,
)

router = APIRouter(prefix="/api/search-configs", tags=["search-configs"])


@router.get("/", response_model=List[SearchConfigRead])
def get_search_configs(
    store_id: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    session: Session = Depends(get_session)
):
    """Get all search configurations with optional filters."""
    query = select(SearchConfig)
    
    if store_id:
        query = query.where(SearchConfig.store_id == store_id)
    if category:
        query = query.where(SearchConfig.category == category)
    if is_active is not None:
        query = query.where(SearchConfig.is_active == is_active)
    
    query = query.order_by(SearchConfig.category, SearchConfig.search_term)  # type: ignore[union-attr]
    configs = session.exec(query).all()
    return configs


@router.get("/categories")
def get_categories():
    """Get all available component categories and their search terms."""
    return {
        "categories": [cat.value for cat in ComponentCategory],
        "search_terms": {cat.value: terms for cat, terms in CATEGORY_SEARCH_TERMS.items()},
    }


@router.get("/{config_id}", response_model=SearchConfigRead)
def get_search_config(config_id: str, session: Session = Depends(get_session)):
    """Get a specific search configuration by ID."""
    config = session.get(SearchConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Search config not found")
    return config


@router.post("/", response_model=SearchConfigRead)
def create_search_config(
    config_data: SearchConfigCreate,
    session: Session = Depends(get_session)
):
    """Create a new search configuration."""
    # Validate store exists
    store = session.get(Store, config_data.store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Validate store is Lazada or Shopee
    store_name = store.name.lower()
    if "lazada" not in store_name and "shopee" not in store_name:
        raise HTTPException(
            status_code=400,
            detail="Search scraping only supports Lazada and Shopee stores"
        )
    
    # Check for duplicate
    existing = session.exec(
        select(SearchConfig)
        .where(SearchConfig.store_id == config_data.store_id)
        .where(SearchConfig.search_term == config_data.search_term)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="A search config with this store and search term already exists"
        )
    
    config = SearchConfig(**config_data.model_dump())
    session.add(config)
    session.commit()
    session.refresh(config)
    return config


@router.put("/{config_id}", response_model=SearchConfigRead)
def update_search_config(
    config_id: str,
    config_data: SearchConfigUpdate,
    session: Session = Depends(get_session)
):
    """Update a search configuration."""
    config = session.get(SearchConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Search config not found")
    
    # Update only provided fields
    update_data = config_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
    
    config.updated_at = datetime.utcnow()
    session.add(config)
    session.commit()
    session.refresh(config)
    return config


@router.delete("/{config_id}")
def delete_search_config(config_id: str, session: Session = Depends(get_session)):
    """Delete a search configuration."""
    config = session.get(SearchConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Search config not found")
    
    session.delete(config)
    session.commit()
    return {"message": "Search config deleted successfully"}


@router.post("/{config_id}/scrape")
def trigger_scrape_config(
    config_id: str,
    session: Session = Depends(get_session)
):
    """Trigger scraping for a specific search configuration."""
    config = session.get(SearchConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Search config not found")
    
    if not config.is_active:
        raise HTTPException(status_code=400, detail="Search config is inactive")
    
    # Queue the scrape task
    task = scrape_search_config.delay(config_id)
    
    return {
        "message": "Scrape task queued",
        "task_id": task.id,
        "config_id": config_id,
        "search_term": config.search_term,
    }


@router.post("/scrape-all")
def trigger_scrape_all():
    """Trigger scraping for all active search configurations."""
    task = scrape_all_search_configs.delay()
    
    return {
        "message": "Scrape all task queued",
        "task_id": task.id,
    }


@router.post("/setup-defaults")
def setup_default_configs():
    """Create default search configurations for PC components on Lazada and Shopee."""
    task = create_default_search_configs.delay()
    
    return {
        "message": "Default configs creation task queued",
        "task_id": task.id,
    }


@router.post("/{config_id}/reset")
def reset_search_config(config_id: str, session: Session = Depends(get_session)):
    """Reset a search config's pagination state to start fresh."""
    config = session.get(SearchConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Search config not found")
    
    config.last_page_scraped = 0
    config.total_pages_found = None
    config.total_products_found = 0
    config.status = "pending"
    config.last_error = None
    config.updated_at = datetime.utcnow()
    
    session.add(config)
    session.commit()
    session.refresh(config)
    
    return {"message": "Search config reset successfully", "config": config}
