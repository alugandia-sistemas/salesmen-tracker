# ==============================================================================
# MODEL: SELLER - Vendedores/Comerciales de Alugandia
# ==============================================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class Seller(Base):
    """
    Modelo de Vendedor/Comercial.
    """
    
    __tablename__ = "sellers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    zone_id = Column(UUID(as_uuid=True), nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    routes = relationship("Route", back_populates="seller", cascade="all, delete-orphan")
    visits = relationship("Visit", back_populates="seller", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", back_populates="seller", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Seller {self.name} ({self.email})>"
    
    def to_dict(self, include_sensitive=False):
        data = {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "zone_id": str(self.zone_id) if self.zone_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
        if include_sensitive:
            data["notes"] = self.notes
        return data
    
    def verify_password(self, password: str) -> bool:
        import bcrypt
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self.password_hash.encode('utf-8')
        )
    
    @staticmethod
    def hash_password(password: str) -> str:
        import bcrypt
        return bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
