# ==============================================================================
# ROUTER: OPPORTUNITIES - Pipeline de ventas
# ==============================================================================

import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from database import get_db
from models import Opportunity, Client

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


class OpportunityCreate(BaseModel):
    seller_id: str
    client_id: str
    title: str
    description: str = None
    estimated_value: float = 0.0
    probability: float = 0.5
    expected_close_date: datetime = None
    next_action: str = None
    next_action_date: datetime = None


@router.get("/")
def list_opportunities(
    db: Session = Depends(get_db),
    seller_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100)
):
    query = db.query(Opportunity)
    
    if seller_id:
        query = query.filter(Opportunity.seller_id == uuid.UUID(seller_id))
    if status:
        query = query.filter(Opportunity.status == status)
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
            "client_name": client.name if client else None,
            "created_at": opp.created_at.isoformat() if opp.created_at else None
        })
    
    return {"data": result, "pagination": {"page": page, "limit": limit, "total": total}}


@router.get("/pipeline")
def get_pipeline_summary(db: Session = Depends(get_db), seller_id: Optional[str] = Query(None)):
    query = db.query(Opportunity).filter(Opportunity.status.notin_(['lost']))
    if seller_id:
        query = query.filter(Opportunity.seller_id == uuid.UUID(seller_id))
    
    opportunities = query.all()
    
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


@router.post("/")
def create_opportunity(opp_data: OpportunityCreate, db: Session = Depends(get_db)):
    new_opp = Opportunity(
        seller_id=uuid.UUID(opp_data.seller_id),
        client_id=uuid.UUID(opp_data.client_id),
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
    
    return {"id": str(new_opp.id), "title": new_opp.title, "message": "Oportunidad creada"}
