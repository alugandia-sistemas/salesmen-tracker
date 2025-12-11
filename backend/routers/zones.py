# ==============================================================================
# ROUTER: ZONES - Zonas geográficas
# ==============================================================================

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from database import get_db
from models import Zone

router = APIRouter(prefix="/zones", tags=["zones"])


class ZoneCreate(BaseModel):
    name: str
    code: str = None
    description: str = None
    color: str = "#4f46e5"
    center_latitude: float = None
    center_longitude: float = None


@router.get("/")
def list_zones(db: Session = Depends(get_db), active_only: bool = Query(default=True)):
    query = db.query(Zone)
    if active_only:
        query = query.filter(Zone.is_active == True)
    zones = query.order_by(Zone.name).all()
    return {"data": [z.to_dict() for z in zones], "total": len(zones)}


@router.get("/{zone_id}")
def get_zone(zone_id: str, db: Session = Depends(get_db)):
    try:
        zone_uuid = uuid.UUID(zone_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="zone_id inválido")
    
    zone = db.query(Zone).filter(Zone.id == zone_uuid).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    return zone.to_dict()


@router.post("/")
def create_zone(zone_data: ZoneCreate, db: Session = Depends(get_db)):
    existing = db.query(Zone).filter(Zone.name == zone_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una zona con ese nombre")
    
    center = None
    if zone_data.center_latitude and zone_data.center_longitude:
        center = func.ST_SetSRID(
            func.ST_MakePoint(zone_data.center_longitude, zone_data.center_latitude), 4326
        )
    
    new_zone = Zone(
        name=zone_data.name,
        code=zone_data.code,
        description=zone_data.description,
        color=zone_data.color,
        center=center
    )
    
    db.add(new_zone)
    db.commit()
    db.refresh(new_zone)
    
    return {"id": str(new_zone.id), "name": new_zone.name, "message": "Zona creada"}


@router.delete("/{zone_id}")
def delete_zone(zone_id: str, db: Session = Depends(get_db)):
    try:
        zone_uuid = uuid.UUID(zone_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="zone_id inválido")
    
    zone = db.query(Zone).filter(Zone.id == zone_uuid).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    
    zone.is_active = False
    db.commit()
    return {"message": "Zona desactivada", "id": zone_id}
