# ==============================================================================
# MODEL: OPPORTUNITY - Oportunidades de venta (Pipeline)
# ==============================================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    estimated_value = Column(Float, default=0.0)
    probability = Column(Float, default=0.5)
    status = Column(
        SQLEnum('new', 'contacted', 'proposal', 'negotiation', 'won', 'lost', name='opportunity_status_enum'),
        default='new',
        index=True
    )
    lost_reason = Column(
        SQLEnum('price', 'competition', 'timing', 'no_budget', 'no_response', 'other', name='lost_reason_enum'),
        nullable=True
    )
    lost_notes = Column(Text)
    expected_close_date = Column(DateTime)
    actual_close_date = Column(DateTime)
    notes = Column(Text)
    next_action = Column(String(200))
    next_action_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    seller = relationship("Seller", back_populates="opportunities")
    client = relationship("Client", back_populates="opportunities")
    
    @property
    def weighted_value(self) -> float:
        return self.estimated_value * self.probability
    
    def to_dict(self, include_relations=False):
        data = {
            "id": str(self.id),
            "seller_id": str(self.seller_id),
            "client_id": str(self.client_id),
            "title": self.title,
            "description": self.description,
            "estimated_value": self.estimated_value,
            "probability": self.probability,
            "weighted_value": self.weighted_value,
            "status": self.status,
            "expected_close_date": self.expected_close_date.isoformat() if self.expected_close_date else None,
            "next_action": self.next_action,
            "next_action_date": self.next_action_date.isoformat() if self.next_action_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        return data
