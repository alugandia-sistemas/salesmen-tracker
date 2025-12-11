# ==============================================================================
# MODEL: OPPORTUNITY - Oportunidades de venta (Pipeline)
# ==============================================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Opportunity(Base):
    """
    Modelo de Oportunidad de Venta.
    
    Pipeline comercial para seguimiento de:
    - Presupuestos enviados
    - Negociaciones en curso
    - Proyectos de obra
    - Nuevos clientes potenciales
    
    Estados del funnel:
    - new: Nueva oportunidad identificada
    - contacted: Primer contacto realizado
    - proposal: Presupuesto enviado
    - negotiation: En negociación
    - won: Ganada (convertida a pedido)
    - lost: Perdida
    """
    
    __tablename__ = "opportunities"
    
    # Identificador único
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relaciones principales
    seller_id = Column(UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    
    # Datos de la oportunidad
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Valor estimado
    estimated_value = Column(Float, default=0.0)
    probability = Column(Float, default=0.5)  # 0.0 - 1.0
    
    # Estado del pipeline
    status = Column(
        SQLEnum(
            'new', 'contacted', 'proposal', 'negotiation', 'won', 'lost',
            name='opportunity_status_enum'
        ),
        default='new',
        index=True
    )
    
    # Motivo de pérdida (si aplica)
    lost_reason = Column(
        SQLEnum(
            'price', 'competition', 'timing', 'no_budget', 
            'no_response', 'other',
            name='lost_reason_enum'
        ),
        nullable=True
    )
    lost_notes = Column(Text)
    
    # Fechas importantes
    expected_close_date = Column(DateTime)
    actual_close_date = Column(DateTime)
    
    # Notas de seguimiento
    notes = Column(Text)
    next_action = Column(String(200))
    next_action_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    seller = relationship("Seller", back_populates="opportunities")
    client = relationship("Client", back_populates="opportunities")
    
    def __repr__(self):
        return f"<Opportunity {self.title} - {self.status}>"
    
    @property
    def weighted_value(self) -> float:
        """Valor ponderado por probabilidad"""
        return self.estimated_value * self.probability
    
    def to_dict(self, include_relations=False):
        """Serialización de la oportunidad"""
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
        
        if include_relations:
            if self.client:
                data["client"] = {
                    "id": str(self.client.id),
                    "name": self.client.name
                }
            if self.seller:
                data["seller"] = {
                    "id": str(self.seller.id),
                    "name": self.seller.name
                }
        
        return data
