# ==============================================================================
# ROUTER: CLIENTS - Endpoints de clientes
# ==============================================================================
# Optimizado: Una sola query con ST_X/ST_Y para coordenadas
# Antes: 1.746 queries para 1.745 clientes (8-12 seg)
# Ahora: 1 query para 1.745 clientes (200-400 ms)
# ==============================================================================

import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, text

from ..database import get_db
from ..models import Client
from ..schemas.client import (
    ClientCreate, ClientUpdate, ClientResponse, 
    ClientListResponse, ClientSearchResponse
)

router = APIRouter(prefix="/clients", tags=["clients"])


# ==============================================================================
# ENDPOINTS PRINCIPALES
# ==============================================================================

@router.get("/")
def list_clients(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(default="active", description="Filtrar: active, inactive, all"),
    page: Optional[int] = Query(default=1, ge=1),
    limit: Optional[int] = Query(default=25, ge=1, le=500),
    search: Optional[str] = Query(default=None, description="Buscar por nombre o dirección")
):
    """
    ✅ OPTIMIZADO: Una sola query extrae coordenadas con ST_X/ST_Y
    
    Soporta:
    - Paginación: ?page=1&limit=25
    - Filtro por status: ?status=active|inactive|all
    - Búsqueda: ?search=cerrajeria
    """
    # Query única con coordenadas extraídas directamente
    query = db.query(
        Client.id,
        Client.name,
        Client.address,
        Client.phone,
        Client.email,
        Client.client_type,
        Client.status,
        Client.created_at,
        # Extraer lon/lat casteando Geography → Geometry
        func.ST_X(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('longitude'),
        func.ST_Y(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('latitude')
    )
    
    # Filtrar por status
    if status and status != "all":
        query = query.filter(Client.status == status)
    
    # Aplicar búsqueda
    if search:
        term = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(Client.name).like(term),
                func.lower(Client.address).like(term)
            )
        )
    
    # Contar total para paginación
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
    
    # Ordenar y paginar
    query = query.order_by(Client.name)
    offset = (page - 1) * limit
    query = query.limit(limit).offset(offset)
    clients = query.all()
    
    # Construir respuesta
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
def count_clients(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(default="active")
):
    """Conteo rápido sin cargar datos"""
    query = db.query(func.count(Client.id))
    if status and status != "all":
        query = query.filter(Client.status == status)
    
    return {"count": query.scalar(), "status": status}


@router.get("/search/")
def search_clients(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, le=100)
):
    """Búsqueda rápida para autocomplete móvil"""
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
    """
    Endpoint optimizado para sincronización offline.
    Devuelve todos los clientes activos con datos mínimos.
    """
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
    """Obtener cliente por ID"""
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


@router.post("/")
def create_client(client_data: ClientCreate, db: Session = Depends(get_db)):
    """Crear nuevo cliente"""
    # Crear ubicación PostGIS si hay coordenadas
    location = None
    if client_data.latitude and client_data.longitude:
        location = func.ST_SetSRID(
            func.ST_MakePoint(client_data.longitude, client_data.latitude),
            4326
        )
    
    new_client = Client(
        name=client_data.name,
        address=client_data.address,
        phone=client_data.phone,
        email=client_data.email,
        client_type=client_data.client_type,
        status=client_data.status,
        location=location
    )
    
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    return {
        "id": str(new_client.id),
        "name": new_client.name,
        "message": "Cliente creado correctamente"
    }


@router.put("/{client_id}")
def update_client(
    client_id: str, 
    client_data: ClientUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar cliente existente"""
    try:
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de cliente inválido")
    
    client = db.query(Client).filter(Client.id == client_uuid).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Actualizar campos proporcionados
    update_data = client_data.model_dump(exclude_unset=True)
    
    # Manejar coordenadas
    if 'latitude' in update_data or 'longitude' in update_data:
        lat = update_data.pop('latitude', None)
        lng = update_data.pop('longitude', None)
        if lat and lng:
            client.location = func.ST_SetSRID(
                func.ST_MakePoint(lng, lat),
                4326
            )
    
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    
    return {"message": "Cliente actualizado", "id": str(client.id)}


@router.delete("/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db)):
    """Eliminar cliente (soft delete - cambia status a inactive)"""
    try:
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de cliente inválido")
    
    client = db.query(Client).filter(Client.id == client_uuid).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    client.status = "inactive"
    db.commit()
    
    return {"message": "Cliente desactivado", "id": str(client.id)}
