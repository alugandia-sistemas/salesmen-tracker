# ==============================================================================
# ROUTER: ROUTES - Rutas programadas de vendedores
# ==============================================================================

import uuid
from typing import Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from database import get_db
from models import Route, Client, Seller

router = APIRouter(prefix="/routes", tags=["routes"])


class RouteCreate(BaseModel):
    seller_id: str
    client_id: str
    scheduled_date: datetime
    scheduled_time: str = None
    visit_order: int = 1
    notes: str = None


@router.get("/")
def list_routes(
    db: Session = Depends(get_db),
    seller_id: Optional[str] = Query(None),
    date_str: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100)
):
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
            raise HTTPException(status_code=400, detail="Formato de fecha inválido")
    
    if status:
        query = query.filter(Route.status == status)
    
    total = query.count()
    offset = (page - 1) * limit
    routes = query.order_by(Route.scheduled_date, Route.visit_order).offset(offset).limit(limit).all()
    
    result = []
    for route in routes:
        client = db.query(Client).filter(Client.id == route.client_id).first()
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
    try:
        seller_uuid = uuid.UUID(route_data.seller_id)
        client_uuid = uuid.UUID(route_data.client_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="IDs inválidos")
    
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
    
    return {"id": str(new_route.id), "message": "Ruta creada correctamente"}
