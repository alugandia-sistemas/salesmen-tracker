# ==============================================================================
# MODEL: ROUTE - Rutas/Visitas programadas
# ==============================================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Route(Base):
    """
    Modelo de Ruta.
    
    Representa una visita programada de un vendedor a un cliente.
    La ruta puede estar:
    - pending: Programada, sin iniciar
    - in_progress: Vendedor en camino o en el cliente
    - completed: Visita realizada (genera Visit)
    - cancelled: Cancelada
    - postponed: Aplazada para otra fecha
    
    Incluye orden de visita para optimización de rutas.
    """
    
    __tablename__ = "routes"
    
    # Identificador único
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relaciones principales
    seller_id = Column(UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    
    # Programación
    scheduled_date = Column(DateTime, nullable=False, index=True)
    scheduled_time = Column(String(10))  # "09:00", "14:30"
    
    # Orden de visita en el día (para optimización)
    visit_order = Column(Integer, default=1)
    
    # Estado de la ruta
    status = Column(
        SQLEnum(
            'pending', 'in_progress', 'completed', 'cancelled', 'postponed',
            name='route_status_enum'
        ),
        default='pending',
        index=True
    )
    
    # Notas de planificación
    notes = Column(Text)
    
    # Motivo de cancelación/aplazamiento
    cancellation_reason = Column(Text)
    postponed_to = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relaciones
    seller = relationship("Seller", back_populates="routes")
    client = relationship("Client", back_populates="routes")
    visit = relationship("Visit", back_populates="route", uselist=False)
    
    def __repr__(self):
        return f"<Route {self.id} - {self.status}>"
    
    def to_dict(self, include_relations=False):
        """Serialización de la ruta"""
        data = {
            "id": str(self.id),
            "seller_id": str(self.seller_id),
            "client_id": str(self.client_id),
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "scheduled_time": self.scheduled_time,
            "visit_order": self.visit_order,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
        
        if include_relations:
            if self.client:
                data["client"] = {
                    "id": str(self.client.id),
                    "name": self.client.name,
                    "address": self.client.address,
                    "phone": self.client.phone
                }
            if self.seller:
                data["seller"] = {
                    "id": str(self.seller.id),
                    "name": self.seller.name
                }
        
        return data
