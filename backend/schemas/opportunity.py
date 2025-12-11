# ==============================================================================
# SCHEMAS: OPPORTUNITY - Validación de datos de oportunidades
# ==============================================================================

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


OpportunityStatus = Literal['new', 'contacted', 'proposal', 'negotiation', 'won', 'lost']
LostReason = Literal['price', 'competition', 'timing', 'no_budget', 'no_response', 'other']


class OpportunityBase(BaseModel):
    """Schema base de oportunidad"""
    seller_id: str
    client_id: str
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    estimated_value: float = Field(default=0.0, ge=0)
    probability: float = Field(default=0.5, ge=0, le=1)


class OpportunityCreate(OpportunityBase):
    """Schema para crear oportunidad"""
    expected_close_date: Optional[datetime] = None
    next_action: Optional[str] = Field(None, max_length=200)
    next_action_date: Optional[datetime] = None


class OpportunityUpdate(BaseModel):
    """Schema para actualizar oportunidad"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    estimated_value: Optional[float] = Field(None, ge=0)
    probability: Optional[float] = Field(None, ge=0, le=1)
    status: Optional[OpportunityStatus] = None
    expected_close_date: Optional[datetime] = None
    next_action: Optional[str] = Field(None, max_length=200)
    next_action_date: Optional[datetime] = None
    notes: Optional[str] = None
    
    # Campos para oportunidades perdidas
    lost_reason: Optional[LostReason] = None
    lost_notes: Optional[str] = None


class OpportunityResponse(BaseModel):
    """Schema de respuesta de oportunidad"""
    id: str
    seller_id: str
    client_id: str
    title: str
    description: Optional[str] = None
    estimated_value: float
    probability: float
    weighted_value: float
    status: str
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    next_action: Optional[str] = None
    next_action_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OpportunityWithClient(OpportunityResponse):
    """Oportunidad con datos del cliente"""
    client_name: Optional[str] = None


class OpportunityListResponse(BaseModel):
    """Lista de oportunidades"""
    data: List[OpportunityWithClient]
    pagination: dict


class PipelineSummary(BaseModel):
    """Resumen del pipeline de ventas"""
    total_opportunities: int
    total_value: float
    weighted_value: float
    by_status: dict  # {"new": 5, "proposal": 3, ...}
    conversion_rate: float
