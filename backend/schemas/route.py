# ==============================================================================
# SCHEMAS: ROUTE - Validación de datos de rutas
# ==============================================================================

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


RouteStatus = Literal['pending', 'in_progress', 'completed', 'cancelled', 'postponed']


class RouteBase(BaseModel):
    """Schema base de ruta"""
    seller_id: str
    client_id: str
    scheduled_date: datetime
    scheduled_time: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')  # "HH:MM"
    visit_order: int = 1
    notes: Optional[str] = None


class RouteCreate(RouteBase):
    """Schema para crear ruta"""
    pass


class RouteUpdate(BaseModel):
    """Schema para actualizar ruta"""
    scheduled_date: Optional[datetime] = None
    scheduled_time: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')
    visit_order: Optional[int] = None
    status: Optional[RouteStatus] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    postponed_to: Optional[datetime] = None


class RouteResponse(BaseModel):
    """Schema de respuesta de ruta"""
    id: str
    seller_id: str
    client_id: str
    scheduled_date: datetime
    scheduled_time: Optional[str] = None
    visit_order: int
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ClientInRoute(BaseModel):
    """Cliente dentro de una ruta"""
    id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RouteWithClient(RouteResponse):
    """Ruta con datos del cliente incluidos"""
    client: Optional[ClientInRoute] = None


class RouteListResponse(BaseModel):
    """Lista de rutas con paginación"""
    data: List[RouteWithClient]
    pagination: dict


class RouteBulkCreate(BaseModel):
    """Crear múltiples rutas a la vez"""
    seller_id: str
    client_ids: List[str]
    scheduled_date: datetime
    auto_order: bool = True  # Auto-ordenar por proximidad
