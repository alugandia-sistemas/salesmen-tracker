# ==============================================================================
# SCHEMAS: ZONE - Validación de datos de zonas
# ==============================================================================

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ZoneBase(BaseModel):
    """Schema base de zona"""
    name: str = Field(..., min_length=2, max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    color: str = Field(default="#4f46e5", pattern=r'^#[0-9A-Fa-f]{6}$')


class ZoneCreate(ZoneBase):
    """Schema para crear zona"""
    # Centro de la zona
    center_latitude: Optional[float] = Field(None, ge=-90, le=90)
    center_longitude: Optional[float] = Field(None, ge=-180, le=180)


class ZoneUpdate(BaseModel):
    """Schema para actualizar zona"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_active: Optional[bool] = None
    center_latitude: Optional[float] = Field(None, ge=-90, le=90)
    center_longitude: Optional[float] = Field(None, ge=-180, le=180)


class ZoneResponse(BaseModel):
    """Schema de respuesta de zona"""
    id: str
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    client_count: int = 0
    is_active: bool = True
    color: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ZoneListResponse(BaseModel):
    """Lista de zonas"""
    data: List[ZoneResponse]
    total: int
