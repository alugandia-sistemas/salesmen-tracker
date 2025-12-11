# ==============================================================================
# SCHEMAS: VISIT - Validación de datos de visitas
# ==============================================================================

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


VisitResult = Literal['venta', 'no_venta', 'interesado', 'seguimiento', 'ausente']


class VisitBase(BaseModel):
    """Schema base de visita"""
    seller_id: str
    client_id: str
    route_id: Optional[str] = None


class CheckinRequest(BaseModel):
    """
    Request para hacer check-in.
    El vendedor envía su ubicación GPS y resultado de visita.
    """
    seller_id: str
    client_id: str
    route_id: Optional[str] = None
    
    # Ubicación GPS del vendedor
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = Field(None, ge=0, description="Precisión GPS en metros")
    
    # Resultado obligatorio
    visit_result: VisitResult
    
    # Nota rápida obligatoria (5-100 caracteres)
    quick_note: str = Field(..., min_length=5, max_length=100)
    
    # Notas detalladas opcionales
    detailed_notes: Optional[str] = None


class CheckoutRequest(BaseModel):
    """Request para hacer check-out"""
    visit_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    
    # Actualizar notas al salir
    additional_notes: Optional[str] = None


class VisitResponse(BaseModel):
    """Schema de respuesta de visita"""
    id: str
    seller_id: str
    client_id: str
    route_id: Optional[str] = None
    
    checkin_time: datetime
    checkout_time: Optional[datetime] = None
    checkin_distance_meters: Optional[float] = None
    checkin_is_valid: bool
    
    visit_result: str
    quick_note: Optional[str] = None
    detailed_notes: Optional[str] = None
    duration_minutes: int = 0
    
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class VisitWithClient(VisitResponse):
    """Visita con datos del cliente incluidos"""
    client_name: Optional[str] = None
    client_address: Optional[str] = None


class VisitListResponse(BaseModel):
    """Lista de visitas con paginación"""
    data: List[VisitWithClient]
    pagination: dict


class VisitStats(BaseModel):
    """Estadísticas de visitas por período"""
    period_months: int
    total_visits: int
    ventas: int
    no_ventas: int
    interesados: int
    seguimientos: int
    ausentes: int
    conversion_rate: float
    avg_distance_meters: Optional[float] = None
    valid_checkins_percentage: float


class CheckinResponse(BaseModel):
    """Respuesta detallada de check-in"""
    success: bool
    message: str
    visit: Optional[VisitResponse] = None
    validation: Optional[dict] = None  # Detalles de validación GPS
    
    class Config:
        from_attributes = True
