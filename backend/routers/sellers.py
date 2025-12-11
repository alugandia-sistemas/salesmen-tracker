# ==============================================================================
# ROUTER: SELLERS - Endpoints de vendedores
# ==============================================================================

import uuid
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Seller, Visit, Route

router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.get("/")
def list_sellers(db: Session = Depends(get_db), active_only: bool = Query(default=True)):
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
    try:
        seller_uuid = uuid.UUID(seller_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de vendedor inválido")
    
    seller = db.query(Seller).filter(Seller.id == seller_uuid).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    return seller.to_dict()


@router.get("/{seller_id}/summary/")
def get_seller_summary(
    seller_id: str,
    months: int = Query(default=3, ge=1, le=6),
    db: Session = Depends(get_db)
):
    try:
        seller_uuid = uuid.UUID(seller_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de vendedor inválido")
    
    date_limit = datetime.utcnow() - timedelta(days=months * 30)
    
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
            "valid_percentage": round((visit_stats.valid_checkins / total * 100) if total > 0 else 0, 2)
        },
        "routes": {
            "total": route_stats.total_routes or 0,
            "completed": route_stats.completed_routes or 0,
            "postponed": route_stats.postponed_routes or 0,
            "cancelled": route_stats.cancelled_routes or 0
        }
    }
