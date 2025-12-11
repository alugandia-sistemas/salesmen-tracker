# ==============================================================================
# SCHEMAS: SELLER - Validación de datos de vendedores
# ==============================================================================

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class SellerBase(BaseModel):
    """Schema base de vendedor"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)


class SellerCreate(SellerBase):
    """Schema para crear vendedor"""
    password: str = Field(..., min_length=6, max_length=100)
    is_admin: bool = False
    zone_id: Optional[str] = None


class SellerUpdate(BaseModel):
    """Schema para actualizar vendedor"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    zone_id: Optional[str] = None
    notes: Optional[str] = None


class SellerLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class SellerResponse(BaseModel):
    """Schema de respuesta de vendedor"""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    is_active: bool
    is_admin: bool
    zone_id: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SellerLoginResponse(BaseModel):
    """Schema de respuesta de login exitoso"""
    success: bool = True
    message: str
    seller: SellerResponse
    
    class Config:
        from_attributes = True


class SellerStats(BaseModel):
    """Estadísticas del vendedor"""
    seller_id: str
    period_months: int
    total_visits: int
    ventas: int
    no_ventas: int
    interesados: int
    seguimientos: int
    ausentes: int
    conversion_rate: float
    avg_distance: Optional[float] = None
    valid_checkins: int
    invalid_checkins: int
