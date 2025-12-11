# ==============================================================================
# MODEL: CLIENT - Clientes de Alugandia
# ==============================================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

from database import Base


class Client(Base):
    """
    Modelo de Cliente.
    
    Representa a los clientes de Alugandia:
    - Cerrajeros
    - Carpinteros metálicos
    - Instaladores
    - Cristaleros
    - Industriales
    
    Incluye ubicación geográfica para validación GPS de visitas.
    """
    
    __tablename__ = "clients"
    
    # Identificador único
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Datos básicos
    name = Column(String(200), nullable=False, index=True)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    
    # Clasificación (tipos específicos de Alugandia)
    client_type = Column(
        SQLEnum(
            'cerrajero', 'carpintero_metalico', 'instalador', 
            'cristalero', 'industrial', 'otro',
            name='client_type_enum'
        ),
        default='otro'
    )
    
    # Estado del cliente
    status = Column(
        SQLEnum('active', 'inactive', 'pending', name='client_status_enum'),
        default='active',
        index=True
    )
    
    # Ubicación geográfica (PostGIS)
    # Geography type para cálculos de distancia precisos en metros
    location = Column(
        Geography(geometry_type='POINT', srid=4326),
        nullable=True
    )
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    routes = relationship("Route", back_populates="client", cascade="all, delete-orphan")
    visits = relationship("Visit", back_populates="client", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Client {self.name} ({self.client_type})>"
    
    def to_dict(self):
        """Serialización básica sin coordenadas (requiere query especial)"""
        return {
            "id": str(self.id),
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "client_type": self.client_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
