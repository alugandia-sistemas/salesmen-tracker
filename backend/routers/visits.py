# ==============================================================================
# ROUTER: VISITS - Visitas con validación GPS
# ==============================================================================
# Sistema de check-in con validación:
# - Distancia máxima: 100 metros
# - Horario: 7:00 - 21:00
# - Detección de fraude (mock location)
# ==============================================================================

import uuid
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from ..database import get_db
from ..models import Visit, Client, Route
from ..schemas.visit import CheckinRequest, CheckoutRequest, VisitStats
from ..config import settings

router = APIRouter(prefix="/visits", tags=["visits"])


# ==============================================================================
# VALIDACIÓN GPS
# ==============================================================================

def validate_checkin(
    seller_lat: float,
    seller_lng: float,
    client_lat: float,
    client_lng: float,
    accuracy: Optional[float] = None
) -> dict:
    """
    Valida el check-in del vendedor.
    
    Returns:
        dict con:
        - is_valid: bool
        - distance_meters: float
        - fraud_flags: list
        - message: str
    """
    fraud_flags = []
    
    # Calcular distancia usando fórmula de Haversine simplificada
    # (PostGIS lo hace mejor, pero esto funciona para validación rápida)
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371000  # Radio de la Tierra en metros
    
    lat1, lon1 = radians(seller_lat), radians(seller_lng)
    lat2, lon2 = radians(client_lat), radians(client_lng)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    # Validar distancia
    max_distance = settings.GPS_MAX_DISTANCE_METERS
    is_valid_distance = distance <= max_distance
    
    # Validar horario
    current_hour = datetime.now().hour
    is_valid_hour = settings.GPS_BUSINESS_HOUR_START <= current_hour <= settings.GPS_BUSINESS_HOUR_END
    
    if not is_valid_hour:
        fraud_flags.append("outside_business_hours")
    
    # Validar precisión GPS
    if accuracy and accuracy > 50:  # Más de 50m de incertidumbre
        fraud_flags.append("low_gps_accuracy")
    
    # Validar coordenadas sospechosas (0,0 o valores exactos)
    if seller_lat == 0 or seller_lng == 0:
        fraud_flags.append("zero_coordinates")
    
    if seller_lat == client_lat and seller_lng == client_lng:
        fraud_flags.append("exact_match_suspicious")
    
    is_valid = is_valid_distance and is_valid_hour and len(fraud_flags) == 0
    
    message = "Check-in válido" if is_valid else f"Check-in inválido: {distance:.0f}m del cliente (máx: {max_distance}m)"
    
    return {
        "is_valid": is_valid,
        "distance_meters": round(distance, 2),
        "fraud_flags": fraud_flags,
        "message": message
    }


# ==============================================================================
# ENDPOINTS
# ==============================================================================

@router.get("/")
def list_visits(
    db: Session = Depends(get_db),
    seller_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    result: Optional[str] = Query(None, description="venta, no_venta, interesado, seguimiento, ausente"),
    days: int = Query(default=30, ge=1, le=180),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100)
):
    """Listar visitas con filtros"""
    date_limit = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(Visit).filter(Visit.checkin_time >= date_limit)
    
    if seller_id:
        try:
            seller_uuid = uuid.UUID(seller_id)
            query = query.filter(Visit.seller_id == seller_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="seller_id inválido")
    
    if client_id:
        try:
            client_uuid = uuid.UUID(client_id)
            query = query.filter(Visit.client_id == client_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="client_id inválido")
    
    if result:
        query = query.filter(Visit.visit_result == result)
    
    # Contar y paginar
    total = query.count()
    offset = (page - 1) * limit
    visits = query.order_by(Visit.checkin_time.desc()).offset(offset).limit(limit).all()
    
    # Enriquecer con datos del cliente
    result_list = []
    for visit in visits:
        client = db.query(Client).filter(Client.id == visit.client_id).first()
        result_list.append({
            "id": str(visit.id),
            "seller_id": str(visit.seller_id),
            "client_id": str(visit.client_id),
            "route_id": str(visit.route_id) if visit.route_id else None,
            "checkin_time": visit.checkin_time.isoformat(),
            "checkout_time": visit.checkout_time.isoformat() if visit.checkout_time else None,
            "checkin_distance_meters": visit.checkin_distance_meters,
            "checkin_is_valid": visit.checkin_is_valid,
            "visit_result": visit.visit_result,
            "quick_note": visit.quick_note,
            "duration_minutes": visit.duration_minutes,
            "client_name": client.name if client else None,
            "client_address": client.address if client else None
        })
    
    return {
        "data": result_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.post("/checkin/")
def do_checkin(checkin_data: CheckinRequest, db: Session = Depends(get_db)):
    """
    Realizar check-in con validación GPS.
    
    El vendedor envía:
    - Su ubicación GPS actual
    - ID del cliente
    - Resultado de la visita
    - Nota rápida obligatoria
    
    El sistema:
    - Calcula distancia al cliente
    - Valida horario y GPS
    - Detecta posible fraude
    - Registra la visita
    """
    try:
        seller_uuid = uuid.UUID(checkin_data.seller_id)
        client_uuid = uuid.UUID(checkin_data.client_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="IDs inválidos")
    
    # Obtener cliente con coordenadas
    client_data = db.query(
        Client.id,
        Client.name,
        func.ST_Y(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('latitude'),
        func.ST_X(func.ST_GeomFromWKB(func.ST_AsBinary(Client.location))).label('longitude')
    ).filter(Client.id == client_uuid).first()
    
    if not client_data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    if not client_data.latitude or not client_data.longitude:
        raise HTTPException(status_code=400, detail="Cliente sin coordenadas registradas")
    
    # Validar check-in
    validation = validate_checkin(
        seller_lat=checkin_data.latitude,
        seller_lng=checkin_data.longitude,
        client_lat=float(client_data.latitude),
        client_lng=float(client_data.longitude),
        accuracy=checkin_data.accuracy
    )
    
    # Crear ubicación PostGIS del vendedor
    seller_location = func.ST_SetSRID(
        func.ST_MakePoint(checkin_data.longitude, checkin_data.latitude),
        4326
    )
    
    # Crear visita
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
    
    # Si hay ruta asociada, marcarla como completada
    if checkin_data.route_id:
        try:
            route_uuid = uuid.UUID(checkin_data.route_id)
            route = db.query(Route).filter(Route.id == route_uuid).first()
            if route:
                route.status = 'completed'
                route.completed_at = datetime.utcnow()
        except ValueError:
            pass
    
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
        "validation": {
            "is_valid": validation["is_valid"],
            "distance_meters": validation["distance_meters"],
            "max_allowed_meters": settings.GPS_MAX_DISTANCE_METERS,
            "fraud_flags": validation["fraud_flags"]
        }
    }


@router.post("/checkout/")
def do_checkout(checkout_data: CheckoutRequest, db: Session = Depends(get_db)):
    """Realizar check-out de una visita"""
    try:
        visit_uuid = uuid.UUID(checkout_data.visit_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="visit_id inválido")
    
    visit = db.query(Visit).filter(Visit.id == visit_uuid).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visita no encontrada")
    
    if visit.checkout_time:
        raise HTTPException(status_code=400, detail="Ya se realizó check-out de esta visita")
    
    # Registrar check-out
    visit.checkout_time = datetime.utcnow()
    visit.checkout_location = func.ST_SetSRID(
        func.ST_MakePoint(checkout_data.longitude, checkout_data.latitude),
        4326
    )
    
    if checkout_data.additional_notes:
        existing_notes = visit.detailed_notes or ""
        visit.detailed_notes = f"{existing_notes}\n[Checkout] {checkout_data.additional_notes}".strip()
    
    db.commit()
    
    return {
        "success": True,
        "message": "Check-out registrado",
        "visit_id": str(visit.id),
        "duration_minutes": visit.duration_minutes
    }


@router.get("/stats/{seller_id}")
def get_visit_stats(
    seller_id: str,
    months: int = Query(default=3, ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Estadísticas de visitas de un vendedor"""
    try:
        seller_uuid = uuid.UUID(seller_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="seller_id inválido")
    
    date_limit = datetime.utcnow() - timedelta(days=months * 30)
    
    stats = db.query(
        func.count(Visit.id).label('total'),
        func.count(Visit.id).filter(Visit.visit_result == 'venta').label('ventas'),
        func.count(Visit.id).filter(Visit.visit_result == 'no_venta').label('no_ventas'),
        func.count(Visit.id).filter(Visit.visit_result == 'interesado').label('interesados'),
        func.count(Visit.id).filter(Visit.visit_result == 'seguimiento').label('seguimientos'),
        func.count(Visit.id).filter(Visit.visit_result == 'ausente').label('ausentes'),
        func.avg(Visit.checkin_distance_meters).label('avg_distance'),
        func.count(Visit.id).filter(Visit.checkin_is_valid == True).label('valid_checkins')
    ).filter(
        Visit.seller_id == seller_uuid,
        Visit.checkin_time >= date_limit
    ).first()
    
    total = stats.total or 0
    valid = stats.valid_checkins or 0
    ventas = stats.ventas or 0
    
    return {
        "seller_id": seller_id,
        "period_months": months,
        "total_visits": total,
        "ventas": ventas,
        "no_ventas": stats.no_ventas or 0,
        "interesados": stats.interesados or 0,
        "seguimientos": stats.seguimientos or 0,
        "ausentes": stats.ausentes or 0,
        "conversion_rate": round((ventas / total * 100) if total > 0 else 0, 2),
        "avg_distance_meters": round(stats.avg_distance, 2) if stats.avg_distance else None,
        "valid_checkins_percentage": round((valid / total * 100) if total > 0 else 0, 2)
    }
