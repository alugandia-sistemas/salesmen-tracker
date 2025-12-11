# ==============================================================================
# SCHEMAS: CLIENT - Validación de datos de clientes
# ==============================================================================

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, EmailStr


# Tipos permitidos de cliente
ClientType = Literal['cerrajero', 'carpintero_metalico', 'instalador', 'cristalero', 'industrial', 'otro']
ClientStatus = Literal['active', 'inactive', 'pending']


class ClientBase(BaseModel):
    """Schema base de cliente"""
    name: str = Field(..., min_length=2, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    client_type: ClientType = 'otro'
    status: ClientStatus = 'active'


class ClientCreate(ClientBase):
    """Schema para crear cliente"""
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class ClientUpdate(BaseModel):
    """Schema para actualizar cliente (todos los campos opcionales)"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    client_type: Optional[ClientType] = None
    status: Optional[ClientStatus] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class ClientResponse(ClientBase):
    """Schema de respuesta de cliente"""
    id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    """Schema para lista paginada de clientes"""
    data: List[ClientResponse]
    pagination: dict
    
    class Config:
        from_attributes = True


class ClientSearchResponse(BaseModel):
    """Schema para búsqueda rápida de clientes"""
    id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    client_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    class Config:
        from_attributes = True
