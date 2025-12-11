# ==============================================================================
# ROUTER: OPPORTUNITIES - Pipeline de ventas
# ==============================================================================

import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Opportunity, Client
from ..schemas.opportunity import OpportunityCreate, OpportunityUpdate

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("/")
def list_opportunities(
    db: Session = Depends(get_db),
    seller_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100)
):
    """Listar oportunidades con filtros"""
    query = db.query(Opportunity)
    
    if seller_id:
        try:
            seller_uuid = uuid.UUID(seller_id)
            query = query.filter(Opportunity.seller_id == seller_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="seller_id inválido")
    
    if status:
        query = query.filter(Opportunity.status == status)
    
    # Excluir cerradas por defecto
    if not status:
        query = query.filter(Opportunity.status.notin_(['won', 'lost']))
    
    total = query.count()
    offset = (page - 1) * limit
    opportunities = query.order_by(Opportunity.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for opp in opportunities:
        client = db.query(Client).filter(Client.id == opp.client_id).first()
        result.append({
            "id": str(opp.id),
            "seller_id": str(opp.seller_id),
            "client_id": str(opp.client_id),
            "title": opp.title,
            "estimated_value": opp.estimated_value,
            "probability": opp.probability,
            "weighted_value": opp.weighted_value,
            "status": opp.status,
            "expected_close_date": opp.expected_close_date.isoformat() if opp.expected_close_date else None,
            "next_action": opp.next_action,
            "next_action_date": opp.next_action_date.isoformat() if opp.next_action_date else None,
            "client_name": client.name if client else None,
            "created_at": opp.created_at.isoformat() if opp.created_at else None
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


@router.get("/pipeline")
def get_pipeline_summary(
    db: Session = Depends(get_db),
    seller_id: Optional[str] = Query(None)
):
    """Resumen del pipeline de ventas"""
    query = db.query(Opportunity).filter(Opportunity.status.notin_(['lost']))
    
    if seller_id:
        try:
            seller_uuid = uuid.UUID(seller_id)
            query = query.filter(Opportunity.seller_id == seller_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="seller_id inválido")
    
    opportunities = query.all()
    
    # Calcular totales por status
    by_status = {}
    total_value = 0
    weighted_value = 0
    
    for opp in opportunities:
        status = opp.status
        if status not in by_status:
            by_status[status] = {"count": 0, "value": 0}
        by_status[status]["count"] += 1
        by_status[status]["value"] += opp.estimated_value
        total_value += opp.estimated_value
        weighted_value += opp.weighted_value
    
    # Calcular conversión
    total_won = len([o for o in opportunities if o.status == 'won'])
    total_closed = total_won + len([o for o in opportunities if o.status == 'lost'])
    conversion_rate = (total_won / total_closed * 100) if total_closed > 0 else 0
    
    return {
        "total_opportunities": len(opportunities),
        "total_value": round(total_value, 2),
        "weighted_value": round(weighted_value, 2),
        "by_status": by_status,
        "conversion_rate": round(conversion_rate, 2)
    }


@router.get("/{opportunity_id}")
def get_opportunity(opportunity_id: str, db: Session = Depends(get_db)):
    """Obtener oportunidad por ID"""
    try:
        opp_uuid = uuid.UUID(opportunity_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="opportunity_id inválido")
    
    opp = db.query(Opportunity).filter(Opportunity.id == opp_uuid).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    client = db.query(Client).filter(Client.id == opp.client_id).first()
    
    return {
        **opp.to_dict(),
        "client_name": client.name if client else None,
        "client_address": client.address if client else None
    }


@router.post("/")
def create_opportunity(opp_data: OpportunityCreate, db: Session = Depends(get_db)):
    """Crear nueva oportunidad"""
    try:
        seller_uuid = uuid.UUID(opp_data.seller_id)
        client_uuid = uuid.UUID(opp_data.client_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="IDs inválidos")
    
    new_opp = Opportunity(
        seller_id=seller_uuid,
        client_id=client_uuid,
        title=opp_data.title,
        description=opp_data.description,
        estimated_value=opp_data.estimated_value,
        probability=opp_data.probability,
        expected_close_date=opp_data.expected_close_date,
        next_action=opp_data.next_action,
        next_action_date=opp_data.next_action_date
    )
    
    db.add(new_opp)
    db.commit()
    db.refresh(new_opp)
    
    return {
        "id": str(new_opp.id),
        "title": new_opp.title,
        "message": "Oportunidad creada correctamente"
    }


@router.put("/{opportunity_id}")
def update_opportunity(
    opportunity_id: str,
    opp_data: OpportunityUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar oportunidad"""
    try:
        opp_uuid = uuid.UUID(opportunity_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="opportunity_id inválido")
    
    opp = db.query(Opportunity).filter(Opportunity.id == opp_uuid).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    update_data = opp_data.model_dump(exclude_unset=True)
    
    # Si se cierra (won/lost), registrar fecha
    if opp_data.status in ['won', 'lost']:
        opp.actual_close_date = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(opp, field, value)
    
    db.commit()
    
    return {"message": "Oportunidad actualizada", "id": str(opp.id)}


@router.delete("/{opportunity_id}")
def delete_opportunity(opportunity_id: str, db: Session = Depends(get_db)):
    """Eliminar oportunidad"""
    try:
        opp_uuid = uuid.UUID(opportunity_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="opportunity_id inválido")
    
    opp = db.query(Opportunity).filter(Opportunity.id == opp_uuid).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    
    db.delete(opp)
    db.commit()
    
    return {"message": "Oportunidad eliminada", "id": opportunity_id}
