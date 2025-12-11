# ==============================================================================
# ROUTER: CLIENTS - Endpoints de clientes
# ==============================================================================

import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from database import get_db
from models import Client

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/")
def list_clients(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(default="active"),
    page: Optional[int] = Query(default=1, ge=1),
    limit: Optional[int] = Query(default=25, ge=1, le=500),
    search: Optional[str] = Query(default=None)
):
    """Lista paginada de clientes con búsqueda"""
    query = db.query(
        Client.id,
        Client.name,
        Client.address,
        Client.phone,
        Client.email,
        Client.client_type,
        Client.status,
        Client.created_at,
        func.ST_X(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('longitude'),
        func.ST_Y(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('latitude')
    )
    
    if status and status != "all":
        query = query.filter(Client.status == status)
    
    if search:
        term = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(Client.name).like(term),
                func.lower(Client.address).like(term)
            )
        )
    
    count_query = db.query(func.count(Client.id))
    if status and status != "all":
        count_query = count_query.filter(Client.status == status)
    if search:
        term = f"%{search.lower()}%"
        count_query = count_query.filter(
            or_(
                func.lower(Client.name).like(term),
                func.lower(Client.address).like(term)
            )
        )
    total = count_query.scalar() or 0
    
    query = query.order_by(Client.name)
    offset = (page - 1) * limit
    query = query.limit(limit).offset(offset)
    clients = query.all()
    
    clients_list = [
        {
            "id": str(c.id),
            "name": c.name,
            "address": c.address,
            "phone": c.phone,
            "email": c.email,
            "client_type": c.client_type,
            "status": c.status,
            "latitude": float(c.latitude) if c.latitude else None,
            "longitude": float(c.longitude) if c.longitude else None,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }
        for c in clients
    ]
    
    pagination = {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit if limit else 1,
        "has_next": (page * limit) < total,
        "has_prev": page > 1
    }
    
    return {"data": clients_list, "pagination": pagination}


@router.get("/count/")
def count_clients(db: Session = Depends(get_db), status: Optional[str] = Query(default="active")):
    query = db.query(func.count(Client.id))
    if status and status != "all":
        query = query.filter(Client.status == status)
    return {"count": query.scalar(), "status": status}


@router.get("/search/")
def search_clients(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100)
):
    search_term = f"%{q.lower()}%"
    clients = db.query(
        Client.id,
        Client.name,
        Client.address,
        Client.phone,
        Client.client_type,
        func.ST_X(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('longitude'),
        func.ST_Y(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('latitude')
    ).filter(
        Client.status == "active",
        or_(
            func.lower(Client.name).like(search_term),
            Client.phone.like(search_term),
            func.lower(Client.address).like(search_term)
        )
    ).order_by(Client.name).limit(limit).all()
    
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "address": c.address,
            "phone": c.phone,
            "client_type": c.client_type,
            "latitude": float(c.latitude) if c.latitude else None,
            "longitude": float(c.longitude) if c.longitude else None
        }
        for c in clients
    ]


@router.get("/sync/")
def sync_clients(db: Session = Depends(get_db)):
    clients = db.query(
        Client.id,
        Client.name,
        Client.address,
        Client.phone,
        Client.client_type,
        func.ST_X(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('longitude'),
        func.ST_Y(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('latitude')
    ).filter(Client.status == "active").all()
    
    return {
        "synced_count": len(clients),
        "timestamp": datetime.utcnow().isoformat(),
        "clients": [
            {
                "id": str(c.id),
                "name": c.name,
                "address": c.address,
                "phone": c.phone,
                "client_type": c.client_type,
                "lat": float(c.latitude) if c.latitude else None,
                "lng": float(c.longitude) if c.longitude else None
            }
            for c in clients
        ]
    }


@router.get("/{client_id}")
def get_client(client_id: str, db: Session = Depends(get_db)):
    try:
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de cliente inválido")
    
    result = db.query(
        Client.id,
        Client.name,
        Client.address,
        Client.phone,
        Client.email,
        Client.client_type,
        Client.status,
        Client.created_at,
        func.ST_X(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('longitude'),
        func.ST_Y(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('latitude')
    ).filter(Client.id == client_uuid).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return {
        "id": str(result.id),
        "name": result.name,
        "address": result.address,
        "phone": result.phone,
        "email": result.email,
        "client_type": result.client_type,
        "status": result.status,
        "latitude": float(result.latitude) if result.latitude else None,
        "longitude": float(result.longitude) if result.longitude else None,
        "created_at": result.created_at.isoformat() if result.created_at else None
    }
