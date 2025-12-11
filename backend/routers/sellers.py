# ==============================================================================
# ROUTER: SELLERS - Endpoints de vendedores
# ==============================================================================

import uuid
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Seller, Visit, Route
from ..schemas.seller import (
    SellerCreate, SellerUpdate, SellerResponse, SellerStats
)

router = APIRouter(prefix="/sellers", tags=["sellers"])


# ==============================================================================
# CRUD BÁSICO
# ==============================================================================

@router.get("/")
def list_sellers(
    db: Session = Depends(get_db),
    active_only: bool = Query(default=True)
):
    """Listar todos los vendedores"""
    query = db.query(Seller)
    if active_only:
        query = query.filter(Seller.is_active == True)
    
    sellers = query.order_by(Seller.name).all()
    
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "email": s.email,
            "phone": s.phone,
            "is_active": s.is_active,
            "is_admin": s.is_admin,
            "zone_id": str(s.zone_id) if s.zone_id else None,
            "last_login": s.last_login.isoformat() if s.last_login else None
        }
        for s in sellers
    ]


@router.get("/{seller_id}")
def get_seller(seller_id: str, db: Session = Depends(get_db)):
    """Obtener vendedor por ID"""
    try:
        seller_uuid = uuid.UUID(seller_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de vendedor inválido")
    
    seller = db.query(Seller).filter(Seller.id == seller_uuid).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    return seller.to_dict()


@router.post("/")
def create_seller(seller_data: SellerCreate, db: Session = Depends(get_db)):
    """Crear nuevo vendedor"""
    # Verificar email único
    existing = db.query(Seller).filter(Seller.email == seller_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    new_seller = Seller(
        name=seller_data.name,
        email=seller_data.email,
        phone=seller_data.phone,
        password_hash=Seller.hash_password(seller_data.password),
        is_admin=seller_data.is_admin,
        zone_id=uuid.UUID(seller_data.zone_id) if seller_data.zone_id else None
    )
    
    db.add(new_seller)
    db.commit()
    db.refresh(new_seller)
    
    return {
        "id": str(new_seller.id),
        "name": new_seller.name,
        "email": new_seller.email,
        "message": "Vendedor creado correctamente"
    }


@router.put("/{seller_id}")
def update_seller(
    seller_id: str,
    seller_data: SellerUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar vendedor"""
    try:
        seller_uuid = uuid.UUID(seller_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de vendedor inválido")
    
    seller = db.query(Seller).filter(Seller.id == seller_uuid).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    update_data = seller_data.model_dump(exclude_unset=True)
    
    # Manejar zone_id
    if 'zone_id' in update_data:
        zone_id = update_data.pop('zone_id')
        seller.zone_id = uuid.UUID(zone_id) if zone_id else None
    
    for field, value in update_data.items():
        setattr(seller, field, value)
    
    db.commit()
    
    return {"message": "Vendedor actualizado", "id": str(seller.id)}


# ==============================================================================
# ESTADÍSTICAS Y KPIs
# ==============================================================================

@router.get("/{seller_id}/summary/")
def get_seller_summary(
    seller_id: str,
    months: int = Query(default=3, ge=1, le=6),
    db: Session = Depends(get_db)
):
    """
    RESUMEN/KPIs DEL VENDEDOR
    
    Métricas del período:
    - Total visitas
    - Desglose por resultado
    - Tasa de conversión
    - Distancia promedio
    """
    try:
        seller_uuid = uuid.UUID(seller_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de vendedor inválido")
    
    date_limit = datetime.utcnow() - timedelta(days=months * 30)
    
    # Estadísticas de visitas
    visit_stats = db.query(
        func.count(Visit.id).label('total'),
        func.count(Visit.id).filter(Visit.visit_result == 'venta').label('ventas'),
        func.count(Visit.id).filter(Visit.visit_result == 'no_venta').label('no_ventas'),
        func.count(Visit.id).filter(Visit.visit_result == 'interesado').label('interesados'),
        func.count(Visit.id).filter(Visit.visit_result == 'seguimiento').label('seguimientos'),
        func.count(Visit.id).filter(Visit.visit_result == 'ausente').label('ausentes'),
        func.avg(Visit.checkin_distance_meters).label('avg_distance'),
        func.count(Visit.id).filter(Visit.checkin_is_valid == True).label('valid_checkins'),
        func.count(Visit.id).filter(Visit.checkin_is_valid == False).label('invalid_checkins')
    ).filter(
        Visit.seller_id == seller_uuid,
        Visit.checkin_time >= date_limit
    ).first()
    
    total = visit_stats.total or 0
    ventas = visit_stats.ventas or 0
    conversion_rate = (ventas / total * 100) if total > 0 else 0
    
    # Estadísticas de rutas
    route_stats = db.query(
        func.count(Route.id).label('total_routes'),
        func.count(Route.id).filter(Route.status == 'completed').label('completed_routes'),
        func.count(Route.id).filter(Route.status == 'postponed').label('postponed_routes'),
        func.count(Route.id).filter(Route.status == 'cancelled').label('cancelled_routes')
    ).filter(
        Route.seller_id == seller_uuid,
        Route.scheduled_date >= date_limit
    ).first()
    
    return {
        "seller_id": seller_id,
        "period_months": months,
        "visits": {
            "total": total,
            "ventas": ventas,
            "no_ventas": visit_stats.no_ventas or 0,
            "interesados": visit_stats.interesados or 0,
            "seguimientos": visit_stats.seguimientos or 0,
            "ausentes": visit_stats.ausentes or 0,
            "conversion_rate": round(conversion_rate, 2)
        },
        "gps": {
            "avg_distance_meters": round(visit_stats.avg_distance, 2) if visit_stats.avg_distance else None,
            "valid_checkins": visit_stats.valid_checkins or 0,
            "invalid_checkins": visit_stats.invalid_checkins or 0,
            "valid_percentage": round(
                (visit_stats.valid_checkins / total * 100) if total > 0 else 0, 2
            )
        },
        "routes": {
            "total": route_stats.total_routes or 0,
            "completed": route_stats.completed_routes or 0,
            "postponed": route_stats.postponed_routes or 0,
            "cancelled": route_stats.cancelled_routes or 0
        }
    }


@router.get("/{seller_id}/history/")
def get_seller_history(
    seller_id: str,
    months: int = Query(default=3, ge=1, le=6),
    status: Optional[str] = Query(None),
    visit_result: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    HISTORIAL DE RUTAS DEL VENDEDOR
    
    Retorna rutas de los últimos N meses con:
    - Datos del cliente
    - Resultado de visita
    - Notas
    """
    from ..models import Client
    
    try:
        seller_uuid = uuid.UUID(seller_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de vendedor inválido")
    
    date_limit = datetime.utcnow() - timedelta(days=months * 30)
    
    # Query base
    query = db.query(Route).filter(
        Route.seller_id == seller_uuid,
        Route.scheduled_date >= date_limit
    )
    
    if status:
        query = query.filter(Route.status == status)
    
    # Ordenar y paginar
    total = query.count()
    offset = (page - 1) * limit
    routes = query.order_by(Route.scheduled_date.desc()).offset(offset).limit(limit).all()
    
    result = []
    for route in routes:
        client = db.query(Client).filter(Client.id == route.client_id).first()
        visit = db.query(Visit).filter(Visit.route_id == route.id).first()
        
        route_data = {
            "id": str(route.id),
            "scheduled_date": route.scheduled_date.isoformat(),
            "status": route.status,
            "client": {
                "id": str(client.id),
                "name": client.name,
                "address": client.address
            } if client else None,
            "visit": {
                "result": visit.visit_result,
                "quick_note": visit.quick_note,
                "checkin_time": visit.checkin_time.isoformat() if visit.checkin_time else None,
                "is_valid": visit.checkin_is_valid
            } if visit else None
        }
        
        if visit_result and visit:
            if visit.visit_result == visit_result:
                result.append(route_data)
        elif visit_result and not visit:
            continue
        else:
            result.append(route_data)
    
    return {
        "seller_id": seller_id,
        "period_months": months,
        "total": len(result),
        "page": page,
        "limit": limit,
        "data": result
    }
