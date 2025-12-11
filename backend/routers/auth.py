# ==============================================================================
# ROUTER: AUTH - Autenticación de vendedores
# ==============================================================================

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Seller
from ..schemas.seller import SellerLogin, SellerLoginResponse, SellerCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(credentials: SellerLogin, db: Session = Depends(get_db)):
    """
    Login de vendedor.
    
    Retorna datos del vendedor si las credenciales son correctas.
    El frontend almacena estos datos en localStorage.
    """
    seller = db.query(Seller).filter(Seller.email == credentials.email).first()
    
    if not seller:
        raise HTTPException(status_code=401, detail="Email no registrado")
    
    if not seller.is_active:
        raise HTTPException(status_code=401, detail="Usuario desactivado")
    
    if not seller.verify_password(credentials.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    # Actualizar último login
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
def register(seller_data: SellerCreate, db: Session = Depends(get_db)):
    """
    Registro de nuevo vendedor.
    
    Solo para uso administrativo - el registro público está deshabilitado.
    """
    # Verificar email único
    existing = db.query(Seller).filter(Seller.email == seller_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Crear nuevo vendedor
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
        "message": f"Usuario {new_seller.name} creado correctamente. Ya puedes iniciar sesión.",
        "seller_id": str(new_seller.id)
    }


@router.post("/change-password")
def change_password(
    seller_id: str,
    current_password: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """Cambiar contraseña del vendedor"""
    import uuid
    
    try:
        seller_uuid = uuid.UUID(seller_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de vendedor inválido")
    
    seller = db.query(Seller).filter(Seller.id == seller_uuid).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    
    if not seller.verify_password(current_password):
        raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")
    
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 6 caracteres")
    
    seller.password_hash = Seller.hash_password(new_password)
    db.commit()
    
    return {"success": True, "message": "Contraseña actualizada correctamente"}
