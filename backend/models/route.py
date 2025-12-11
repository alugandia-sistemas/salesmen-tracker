# ==============================================================================
# MODEL: ROUTE - Rutas/Visitas programadas
# ==============================================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class Route(Base):
    __tablename__ = "routes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    scheduled_date = Column(DateTime, nullable=False, index=True)
    scheduled_time = Column(String(10))
    visit_order = Column(Integer, default=1)
    status = Column(
        SQLEnum('pending', 'in_progress', 'completed', 'cancelled', 'postponed', name='route_status_enum'),
        default='pending',
        index=True
    )
    notes = Column(Text)
    cancellation_reason = Column(Text)
    postponed_to = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    seller = relationship("Seller", back_populates="routes")
    client = relationship("Client", back_populates="routes")
    visit = relationship("Visit", back_populates="route", uselist=False)
    
    def __repr__(self):
        return f"<Route {self.id} - {self.status}>"
