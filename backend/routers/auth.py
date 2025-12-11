# ==============================================================================
# ROUTER: AUTH - Autenticación de vendedores
# ==============================================================================

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from database import get_db
from models import Seller

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str = None
    is_admin: bool = False


@router.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    seller = db.query(Seller).filter(Seller.email == credentials.email).first()
    
    if not seller:
        raise HTTPException(status_code=401, detail="Email no registrado")
    
    if not seller.is_active:
        raise HTTPException(status_code=401, detail="Usuario desactivado")
    
    if not seller.verify_password(credentials.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    seller.last_login = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": f"Bienvenido, {seller.name}",
        "seller": {
            "id": str(seller.id),
            "name": seller.name,
            "email": seller.email,
            "phone": seller.phone,
            "is_admin": seller.is_admin,
            "zone_id": str(seller.zone_id) if seller.zone_id else None
        }
    }


@router.post("/register")
def register(seller_data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Seller).filter(Seller.email == seller_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    new_seller = Seller(
        name=seller_data.name,
        email=seller_data.email,
        phone=seller_data.phone,
        password_hash=Seller.hash_password(seller_data.password),
        is_admin=seller_data.is_admin
    )
    
    db.add(new_seller)
    db.commit()
    db.refresh(new_seller)
    
    return {
        "success": True,
        "message": f"Usuario {new_seller.name} creado correctamente.",
        "seller_id": str(new_seller.id)
    }
