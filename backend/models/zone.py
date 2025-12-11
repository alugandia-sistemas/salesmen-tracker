# ==============================================================================
# MODEL: ZONE - Zonas geográficas
# ==============================================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography

from ..database import Base


class Zone(Base):
    """
    Modelo de Zona Geográfica.
    
    Organiza el territorio de la Comunitat Valenciana en zonas:
    - Gandia y comarca
    - Valencia ciudad
    - Alicante
    - Castellón
    - etc.
    
    Cada zona puede tener múltiples rutas asignadas.
    Usado para:
    - Asignación de vendedores por territorio
    - Optimización de rutas por proximidad
    - Reportes de cobertura geográfica
    """
    
    __tablename__ = "zones"
    
    # Identificador único
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Datos básicos
    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(20), unique=True)  # "GAN", "VLC", "ALC"
    description = Column(Text)
    
    # Geometría de la zona (polígono)
    boundary = Column(Geography(geometry_type='POLYGON', srid=4326))
    
    # Centro de la zona (para cálculos de distancia)
    center = Column(Geography(geometry_type='POINT', srid=4326))
    
    # Estadísticas
    client_count = Column(Integer, default=0)
    
    # Estado
    is_active = Column(Boolean, default=True)
    
    # Color para visualización en mapa
    color = Column(String(7), default="#4f46e5")  # Hex color
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Zone {self.name} ({self.code})>"
    
    def to_dict(self):
        """Serialización de la zona"""
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "client_count": self.client_count,
            "is_active": self.is_active,
            "color": self.color,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
