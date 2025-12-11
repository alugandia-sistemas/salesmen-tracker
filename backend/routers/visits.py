# ==============================================================================
# ROUTER: VISITS - Visitas con validación GPS
# ==============================================================================

import uuid
from typing import Optional
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field

from database import get_db
from models import Visit, Client, Route
from config import settings

router = APIRouter(prefix="/visits", tags=["visits"])


class CheckinRequest(BaseModel):
    seller_id: str
    client_id: str
    route_id: str = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: float = None
    visit_result: str
    quick_note: str = Field(..., min_length=5, max_length=100)
    detailed_notes: str = None


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


def validate_checkin(seller_lat, seller_lng, client_lat, client_lng, accuracy=None):
    fraud_flags = []
    distance = calculate_distance(seller_lat, seller_lng, client_lat, client_lng)
    max_distance = settings.GPS_MAX_DISTANCE_METERS
    is_valid_distance = distance <= max_distance
    
    current_hour = datetime.now().hour
    is_valid_hour = settings.GPS_BUSINESS_HOUR_START <= current_hour <= settings.GPS_BUSINESS_HOUR_END
    
    if not is_valid_hour:
        fraud_flags.append("outside_business_hours")
    if accuracy and accuracy > 50:
        fraud_flags.append("low_gps_accuracy")
    if seller_lat == 0 or seller_lng == 0:
        fraud_flags.append("zero_coordinates")
    
    is_valid = is_valid_distance and is_valid_hour and len(fraud_flags) == 0
    message = "Check-in válido" if is_valid else f"Check-in inválido: {distance:.0f}m del cliente"
    
    return {
        "is_valid": is_valid,
        "distance_meters": round(distance, 2),
        "fraud_flags": fraud_flags,
        "message": message
    }


@router.get("/")
def list_visits(
    db: Session = Depends(get_db),
    seller_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
    days: int = Query(default=30, ge=1, le=180),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100)
):
    date_limit = datetime.utcnow() - timedelta(days=days)
    query = db.query(Visit).filter(Visit.checkin_time >= date_limit)
    
    if seller_id:
        query = query.filter(Visit.seller_id == uuid.UUID(seller_id))
    if client_id:
        query = query.filter(Visit.client_id == uuid.UUID(client_id))
    if result:
        query = query.filter(Visit.visit_result == result)
    
    total = query.count()
    offset = (page - 1) * limit
    visits = query.order_by(Visit.checkin_time.desc()).offset(offset).limit(limit).all()
    
    result_list = []
    for visit in visits:
        client = db.query(Client).filter(Client.id == visit.client_id).first()
        result_list.append({
            "id": str(visit.id),
            "seller_id": str(visit.seller_id),
            "client_id": str(visit.client_id),
            "checkin_time": visit.checkin_time.isoformat(),
            "checkout_time": visit.checkout_time.isoformat() if visit.checkout_time else None,
            "checkin_distance_meters": visit.checkin_distance_meters,
            "checkin_is_valid": visit.checkin_is_valid,
            "visit_result": visit.visit_result,
            "quick_note": visit.quick_note,
            "duration_minutes": visit.duration_minutes,
            "client_name": client.name if client else None
        })
    
    return {"data": result_list, "pagination": {"page": page, "limit": limit, "total": total}}


@router.post("/checkin/")
def do_checkin(checkin_data: CheckinRequest, db: Session = Depends(get_db)):
    try:
        seller_uuid = uuid.UUID(checkin_data.seller_id)
        client_uuid = uuid.UUID(checkin_data.client_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="IDs inválidos")
    
    client_data = db.query(
        Client.id,
        Client.name,
        func.ST_Y(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('latitude'),
        func.ST_X(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('longitude')
    ).filter(Client.id == client_uuid).first()
    
    if not client_data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    if not client_data.latitude or not client_data.longitude:
        raise HTTPException(status_code=400, detail="Cliente sin coordenadas")
    
    validation = validate_checkin(
        checkin_data.latitude, checkin_data.longitude,
        float(client_data.latitude), float(client_data.longitude),
        checkin_data.accuracy
    )
    
    seller_location = func.ST_SetSRID(
        func.ST_MakePoint(checkin_data.longitude, checkin_data.latitude), 4326
    )
    
    new_visit = Visit(
        seller_id=seller_uuid,
        client_id=client_uuid,
        route_id=uuid.UUID(checkin_data.route_id) if checkin_data.route_id else None,
        checkin_time=datetime.utcnow(),
        checkin_location=seller_location,
        checkin_distance_meters=validation["distance_meters"],
        checkin_is_valid=validation["is_valid"],
        checkin_accuracy=checkin_data.accuracy,
        visit_result=checkin_data.visit_result,
        quick_note=checkin_data.quick_note,
        detailed_notes=checkin_data.detailed_notes,
        fraud_flags=",".join(validation["fraud_flags"]) if validation["fraud_flags"] else None
    )
    
    db.add(new_visit)
    
    if checkin_data.route_id:
        route = db.query(Route).filter(Route.id == uuid.UUID(checkin_data.route_id)).first()
        if route:
            route.status = 'completed'
            route.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_visit)
    
    return {
        "success": True,
        "message": validation["message"],
        "visit": {
            "id": str(new_visit.id),
            "checkin_time": new_visit.checkin_time.isoformat(),
            "visit_result": new_visit.visit_result,
            "client_name": client_data.name
        },
        "validation": validation
    }


@router.get("/stats/{seller_id}")
def get_visit_stats(seller_id: str, months: int = Query(default=3), db: Session = Depends(get_db)):
    seller_uuid = uuid.UUID(seller_id)
    date_limit = datetime.utcnow() - timedelta(days=months * 30)
    
    stats = db.query(
        func.count(Visit.id).label('total'),
        func.count(Visit.id).filter(Visit.visit_result == 'venta').label('ventas'),
        func.count(Visit.id).filter(Visit.visit_result == 'no_venta').label('no_ventas'),
        func.count(Visit.id).filter(Visit.visit_result == 'interesado').label('interesados'),
        func.avg(Visit.checkin_distance_meters).label('avg_distance'),
        func.count(Visit.id).filter(Visit.checkin_is_valid == True).label('valid_checkins')
    ).filter(Visit.seller_id == seller_uuid, Visit.checkin_time >= date_limit).first()
    
    total = stats.total or 0
    ventas = stats.ventas or 0
    
    return {
        "seller_id": seller_id,
        "period_months": months,
        "total_visits": total,
        "ventas": ventas,
        "no_ventas": stats.no_ventas or 0,
        "interesados": stats.interesados or 0,
        "conversion_rate": round((ventas / total * 100) if total > 0 else 0, 2),
        "avg_distance_meters": round(stats.avg_distance, 2) if stats.avg_distance else None
    }
