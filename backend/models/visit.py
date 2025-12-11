# ==============================================================================
# MODEL: VISIT - Visitas realizadas con validación GPS
# ==============================================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

from database import Base


class Visit(Base):
    __tablename__ = "visits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"), nullable=True, index=True)
    
    checkin_time = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    checkin_location = Column(Geography(geometry_type='POINT', srid=4326))
    checkin_distance_meters = Column(Float)
    checkin_is_valid = Column(Boolean, default=False)
    checkin_accuracy = Column(Float)
    
    checkout_time = Column(DateTime, nullable=True)
    checkout_location = Column(Geography(geometry_type='POINT', srid=4326))
    
    visit_result = Column(
        SQLEnum('venta', 'no_venta', 'interesado', 'seguimiento', 'ausente', name='visit_result_enum'),
        nullable=False,
        index=True
    )
    
    quick_note = Column(String(100))
    detailed_notes = Column(Text)
    fraud_flags = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    seller = relationship("Seller", back_populates="visits")
    client = relationship("Client", back_populates="visits")
    route = relationship("Route", back_populates="visit")
    
    @property
    def duration_minutes(self) -> int:
        if self.checkin_time and self.checkout_time:
            delta = self.checkout_time - self.checkin_time
            return int(delta.total_seconds() / 60)
        return 0
