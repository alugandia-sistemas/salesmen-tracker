# ==============================================================================
# ROUTER: ROUTES - Rutas programadas de vendedores
# ==============================================================================

import uuid
from typing import Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Route, Client, Seller
from ..schemas.route import RouteCreate, RouteUpdate, RouteBulkCreate

router = APIRouter(prefix="/routes", tags=["routes"])


# ==============================================================================
# CRUD BÁSICO
# ==============================================================================

@router.get("/")
def list_routes(
    db: Session = Depends(get_db),
    seller_id: Optional[str] = Query(None),
    date_str: Optional[str] = Query(None, description="Fecha YYYY-MM-DD"),
    status: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100)
):
    """Listar rutas con filtros"""
    query = db.query(Route)
    
    if seller_id:
        try:
            seller_uuid = uuid.UUID(seller_id)
            query = query.filter(Route.seller_id == seller_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="seller_id inválido")
    
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            query = query.filter(func.date(Route.scheduled_date) == filter_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    if status:
        query = query.filter(Route.status == status)
    
    # Contar total
    total = query.count()
    
    # Paginar y ordenar
    offset = (page - 1) * limit
    routes = query.order_by(
        Route.scheduled_date, 
        Route.visit_order
    ).offset(offset).limit(limit).all()
    
    # Enriquecer con datos del cliente
    result = []
    for route in routes:
        client = db.query(Client).filter(Client.id == route.client_id).first()
        
        # Obtener coordenadas del cliente
        client_coords = db.query(
            func.ST_X(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('longitude'),
            func.ST_Y(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('latitude')
        ).filter(Client.id == route.client_id).first()
        
        result.append({
            "id": str(route.id),
            "seller_id": str(route.seller_id),
            "client_id": str(route.client_id),
            "scheduled_date": route.scheduled_date.isoformat(),
            "scheduled_time": route.scheduled_time,
            "visit_order": route.visit_order,
            "status": route.status,
            "notes": route.notes,
            "client": {
                "id": str(client.id),
                "name": client.name,
                "address": client.address,
                "phone": client.phone,
                "latitude": float(client_coords.latitude) if client_coords and client_coords.latitude else None,
                "longitude": float(client_coords.longitude) if client_coords and client_coords.longitude else None
            } if client else None
        })
    
    return {
        "data": result,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.get("/today/{seller_id}")
def get_today_routes(seller_id: str, db: Session = Depends(get_db)):
    """Rutas de hoy para un vendedor"""
    try:
        seller_uuid = uuid.UUID(seller_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="seller_id inválido")
    
    today = date.today()
    
    routes = db.query(Route).filter(
        Route.seller_id == seller_uuid,
        func.date(Route.scheduled_date) == today,
        Route.status.in_(['pending', 'in_progress'])
    ).order_by(Route.visit_order).all()
    
    result = []
    for route in routes:
        client = db.query(Client).filter(Client.id == route.client_id).first()
        client_coords = db.query(
            func.ST_X(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('longitude'),
            func.ST_Y(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('latitude')
        ).filter(Client.id == route.client_id).first()
        
        result.append({
            "id": str(route.id),
            "visit_order": route.visit_order,
            "scheduled_time": route.scheduled_time,
            "status": route.status,
            "notes": route.notes,
            "client": {
                "id": str(client.id),
                "name": client.name,
                "address": client.address,
                "phone": client.phone,
                "latitude": float(client_coords.latitude) if client_coords and client_coords.latitude else None,
                "longitude": float(client_coords.longitude) if client_coords and client_coords.longitude else None
            } if client else None
        })
    
    return {
        "seller_id": seller_id,
        "date": today.isoformat(),
        "total_routes": len(result),
        "routes": result
    }


@router.post("/")
def create_route(route_data: RouteCreate, db: Session = Depends(get_db)):
    """Crear nueva ruta"""
    # Validar seller y client
    try:
        seller_uuid = uuid.UUID(route_data.seller_id)
        client_uuid = uuid.UUID(route_data.client_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="IDs inválidos")
    
    seller = db.query(Seller).filter(Seller.id == seller_uuid).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    client = db.query(Client).filter(Client.id == client_uuid).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    new_route = Route(
        seller_id=seller_uuid,
        client_id=client_uuid,
        scheduled_date=route_data.scheduled_date,
        scheduled_time=route_data.scheduled_time,
        visit_order=route_data.visit_order,
        notes=route_data.notes
    )
    
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    
    return {
        "id": str(new_route.id),
        "message": "Ruta creada correctamente"
    }


@router.post("/bulk")
def create_bulk_routes(bulk_data: RouteBulkCreate, db: Session = Depends(get_db)):
    """Crear múltiples rutas a la vez"""
    try:
        seller_uuid = uuid.UUID(bulk_data.seller_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="seller_id inválido")
    
    seller = db.query(Seller).filter(Seller.id == seller_uuid).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    created_routes = []
    for i, client_id in enumerate(bulk_data.client_ids, start=1):
        try:
            client_uuid = uuid.UUID(client_id)
        except ValueError:
            continue
        
        client = db.query(Client).filter(Client.id == client_uuid).first()
        if not client:
            continue
        
        new_route = Route(
            seller_id=seller_uuid,
            client_id=client_uuid,
            scheduled_date=bulk_data.scheduled_date,
            visit_order=i if bulk_data.auto_order else 1
        )
        db.add(new_route)
        created_routes.append(str(new_route.id))
    
    db.commit()
    
    return {
        "created_count": len(created_routes),
        "route_ids": created_routes,
        "message": f"{len(created_routes)} rutas creadas"
    }


@router.put("/{route_id}")
def update_route(
    route_id: str,
    route_data: RouteUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar ruta"""
    try:
        route_uuid = uuid.UUID(route_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="route_id inválido")
    
    route = db.query(Route).filter(Route.id == route_uuid).first()
    if not route:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    
    update_data = route_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(route, field, value)
    
    # Si se completa la ruta, registrar timestamp
    if route_data.status == 'completed':
        route.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Ruta actualizada", "id": str(route.id)}


@router.delete("/{route_id}")
def delete_route(route_id: str, db: Session = Depends(get_db)):
    """Eliminar ruta"""
    try:
        route_uuid = uuid.UUID(route_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="route_id inválido")
    
    route = db.query(Route).filter(Route.id == route_uuid).first()
    if not route:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    
    db.delete(route)
    db.commit()
    
    return {"message": "Ruta eliminada", "id": route_id}
