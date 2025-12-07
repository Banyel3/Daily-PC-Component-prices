from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from backend.database import get_session
from backend.models.store import Store, StoreCreate, StoreRead

router = APIRouter(prefix="/api/stores", tags=["stores"])


@router.get("/", response_model=List[StoreRead])
def get_stores(session: Session = Depends(get_session)):
    """Get all stores."""
    query = select(Store).order_by(Store.name)
    stores = session.exec(query).all()
    return stores


@router.get("/{store_id}", response_model=StoreRead)
def get_store(store_id: str, session: Session = Depends(get_session)):
    """Get a specific store by ID."""
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.post("/", response_model=StoreRead)
def create_store(store_data: StoreCreate, session: Session = Depends(get_session)):
    """Create a new store."""
    # Check if store with same name exists
    existing = session.exec(
        select(Store).where(Store.name == store_data.name)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Store with this name already exists")
    
    store = Store(**store_data.model_dump())
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


@router.put("/{store_id}", response_model=StoreRead)
def update_store(
    store_id: str,
    store_data: StoreCreate,
    session: Session = Depends(get_session)
):
    """Update an existing store."""
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    for key, value in store_data.model_dump().items():
        setattr(store, key, value)
    
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


@router.delete("/{store_id}")
def delete_store(store_id: str, session: Session = Depends(get_session)):
    """Delete a store."""
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    session.delete(store)
    session.commit()
    return {"message": "Store deleted successfully"}
