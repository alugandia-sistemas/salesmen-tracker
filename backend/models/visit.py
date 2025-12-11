# ==============================================================================
# MODEL: VISIT - Visitas realizadas con validación GPS
# ==============================================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

from ..database import Base


class Visit(Base):
    """
    Modelo de Visita.
    
    Registra una visita real de un vendedor a un cliente.
    Incluye:
    - Check-in con GPS y validación de distancia
    - Check-out con GPS
    - Resultado de la visita (venta, no_venta, interesado, etc.)
    - Notas rápidas y detalladas
    
    La validación GPS requiere:
    - Estar dentro de 100m del cliente
    - Estar en horario laboral (7:00-21:00)
    - GPS con precisión aceptable
    """
    
    __tablename__ = "visits"
    
    # Identificador único
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relaciones principales
    seller_id = Column(UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"), nullable=True, index=True)
    
    # Check-in
    checkin_time = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    checkin_location = Column(Geography(geometry_type='POINT', srid=4326))
    checkin_distance_meters = Column(Float)  # Distancia al cliente
    checkin_is_valid = Column(Boolean, default=False)  # ¿Cumple validación GPS?
    checkin_accuracy = Column(Float)  # Precisión GPS en metros
    
    # Check-out
    checkout_time = Column(DateTime, nullable=True)
    checkout_location = Column(Geography(geometry_type='POINT', srid=4326))
    
    # Resultado de la visita (OBLIGATORIO)
    visit_result = Column(
        SQLEnum(
            'venta', 'no_venta', 'interesado', 'seguimiento', 'ausente',
            name='visit_result_enum'
        ),
        nullable=False,
        index=True
    )
    
    # Notas
    quick_note = Column(String(100))  # Nota rápida obligatoria (5-100 chars)
    detailed_notes = Column(Text)     # Notas detalladas opcionales
    
    # Detección de fraude
    fraud_flags = Column(Text)  # JSON con flags: mock_location, outside_hours, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    seller = relationship("Seller", back_populates="visits")
    client = relationship("Client", back_populates="visits")
    route = relationship("Route", back_populates="visit")
    
    def __repr__(self):
        return f"<Visit {self.id} - {self.visit_result}>"
    
    @property
    def duration_minutes(self) -> int:
        """Calcula duración de la visita en minutos"""
        if self.checkin_time and self.checkout_time:
            delta = self.checkout_time - self.checkin_time
            return int(delta.total_seconds() / 60)
        return 0
    
    def to_dict(self, include_relations=False):
        """Serialización de la visita"""
        data = {
            "id": str(self.id),
            "seller_id": str(self.seller_id),
            "client_id": str(self.client_id),
            "route_id": str(self.route_id) if self.route_id else None,
            "checkin_time": self.checkin_time.isoformat() if self.checkin_time else None,
            "checkout_time": self.checkout_time.isoformat() if self.checkout_time else None,
            "checkin_distance_meters": self.checkin_distance_meters,
            "checkin_is_valid": self.checkin_is_valid,
            "visit_result": self.visit_result,
            "quick_note": self.quick_note,
            "detailed_notes": self.detailed_notes,
            "duration_minutes": self.duration_minutes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        
        if include_relations:
            if self.client:
                data["client"] = {
                    "id": str(self.client.id),
                    "name": self.client.name,
                    "address": self.client.address
                }
            if self.seller:
                data["seller"] = {
                    "id": str(self.seller.id),
                    "name": self.seller.name
                }
        
        return data
