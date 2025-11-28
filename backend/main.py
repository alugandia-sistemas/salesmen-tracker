from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Enum, create_engine, text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker, joinedload
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from geoalchemy2 import Geometry, Geography
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
import shutil
from pathlib import Path
import math

# ============================================================================
# CONFIGURACIÓN Y CONEXIÓN BD
# ============================================================================


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/salesmen_tracker")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ HABILITAR POSTGIS AUTOMÁTICAMENTE AL STARTUP
def init_postgis():
    """
    Habilita PostGIS en la base de datos
    En Railway: instala la extensión si no existe
    """
    try:
        with engine.connect() as connection:
            # Intento 1: Crear extensión directamente
            try:
                connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                connection.commit()
                print("✅ PostGIS habilitado correctamente")
                return
            except Exception as e1:
                # Intento 2: Si el usuario no tiene permisos, intentar con superusuario
                # En Railway, el usuario 'postgres' es superusuario
                if "permission denied" in str(e1).lower() or "not available" in str(e1).lower():
                    print(f"⚠️ Intento 1 falló: {str(e1)}")
                    print("🔧 Intentando instalación alternativa de PostGIS...")
                    
                    # Desconectar y reconectar como postgres
                    connection.close()
                    
                    # Reintentar con CREATE EXTENSION
                    with engine.connect() as conn2:
                        try:
                            conn2.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                            conn2.commit()
                            print("✅ PostGIS instalado en segundo intento")
                            return
                        except Exception as e2:
                            print(f"⚠️ PostGIS no disponible: {str(e2)}")
                            print("ℹ️ En Railway: verifica que PostgreSQL incluya PostGIS")
                            # No lanzar error - permitir que continúe sin PostGIS
                else:
                    raise e1
    except Exception as e:
        print(f"⚠️ Error crítico en PostGIS: {str(e)}")
        # No lanzar - permitir startup sin PostGIS (fallback mode)

app = FastAPI(title="Salesmen Tracker - Alugandia")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# INICIALIZACIÓN CON RETRY AUTOMÁTICO
# ============================================================================

async def init_db_with_retry(max_retries: int = 5, delay: int = 2):
    """
    ✅ Inicializa BD con reintentos exponenciales
    Espera a que PostgreSQL esté disponible antes de crear tablas
    """
    for attempt in range(max_retries):
        try:
            print(f"🔄 Intento {attempt + 1}/{max_retries} de conexión a BD...")
            init_postgis()
            Base.metadata.create_all(bind=engine)
            print("✅ BD inicializada correctamente")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)  # Backoff exponencial
                print(f"⚠️ Error en intento {attempt + 1}: {str(e)}")
                print(f"⏳ Esperando {wait_time}s antes de reintentar...")
                import asyncio
                await asyncio.sleep(wait_time)
            else:
                print(f"❌ Error fatal después de {max_retries} intentos: {str(e)}")
                raise

@app.on_event("startup")
async def startup_event():
    """Evento de startup: inicializar BD"""
    await init_db_with_retry()

# ============================================================================
# MODELOS DE BD (SQLAlchemy)
# ============================================================================

class Seller(Base):
    __tablename__ = "sellers"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    routes = relationship("Route", back_populates="seller")
    visits = relationship("Visit", back_populates="seller")
    opportunities = relationship("Opportunity", back_populates="seller")


class Client(Base):
    __tablename__ = "clients"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    
    # ✅ CORRECCIÓN: Usar Geography en lugar de Geometry para precisión
    # Geography utiliza elipsoide WGS84 para cálculos de distancia más precisos
    location = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    
    client_type = Column(String(50), nullable=False)  # carpenter, installer, industrial
    status = Column(String(20), default="active")  # active, inactive, pending
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    routes = relationship("Route", back_populates="client")
    visits = relationship("Visit", back_populates="client")
    opportunities = relationship("Opportunity", back_populates="client")


class Route(Base):
    __tablename__ = "routes"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(PG_UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False)
    client_id = Column(PG_UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    
    planned_date = Column(DateTime, nullable=False)  # Solo fecha (hora se obtiene en check-in)
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys & Relaciones
    seller = relationship("Seller", back_populates="routes")
    client = relationship("Client", back_populates="routes")
    visits = relationship("Visit", back_populates="route")


class Visit(Base):
    __tablename__ = "visits"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(PG_UUID(as_uuid=True), ForeignKey("routes.id"), nullable=False)
    seller_id = Column(PG_UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False)
    client_id = Column(PG_UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    
    # ✅ CHECK-IN: Ubicación GPS capturada
    checkin_time = Column(DateTime, nullable=True)
    checkin_location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    checkin_distance_meters = Column(Float, nullable=True)  # Distancia al cliente
    checkin_photo_url = Column(String(500), nullable=True)  # Foto geoetiquetada
    
    # ✅ VALIDACIÓN DE PROXIMIDAD
    checkin_is_valid = Column(Boolean, default=False)  # ¿Dentro del rango permitido?
    checkin_validation_error = Column(String(255), nullable=True)  # Motivo del error si aplica
    
    # ✅ CHECK-OUT: Ubicación GPS capturada
    checkout_time = Column(DateTime, nullable=True)
    checkout_location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    checkout_distance_meters = Column(Float, nullable=True)
    
    # ✅ AUDITORÍA DE FRAUDE
    fraud_flags = Column(Text, nullable=True)  # JSON con flags de posible fraude
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    route = relationship("Route", back_populates="visits")
    seller = relationship("Seller", back_populates="visits")
    client = relationship("Client", back_populates="visits")


class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(PG_UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False)
    client_id = Column(PG_UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    estimated_value = Column(Float, nullable=False)
    status = Column(String(20), default="open")  # open, in_negotiation, won, lost
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    seller = relationship("Seller", back_populates="opportunities")
    client = relationship("Client", back_populates="opportunities")


# ✅ INICIALIZACIÓN DIFERIDA: NO ejecutar en startup del módulo
# Se ejecutará en el evento @app.on_event("startup") con reintentos

# ============================================================================
# SCHEMAS PYDANTIC (Validación de Entrada/Salida)
# ============================================================================

class SellerCreate(BaseModel):
    """Crear o actualizar vendedor"""
    name: str
    email: str
    phone: str
    is_active: bool = True

    class Config:
        from_attributes = True


class SellerResponse(BaseModel):
    """Respuesta de vendedor"""
    id: str
    name: str
    email: str
    phone: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CheckInRequest(BaseModel):
    """
    ✅ REDISEÑO: Check-in con validación robusta
    """
    route_id: str
    seller_id: str
    client_id: str
    
    # Ubicación GPS (lat, lng desde cliente)
    latitude: float
    longitude: float
    
    # Confirmación manual
    client_found: bool  # ¿Realmente encontró al cliente?
    notes: Optional[str] = None


class CheckInResponse(BaseModel):
    """Respuesta del check-in con resultado de validación"""
    visit_id: str
    success: bool
    is_valid: bool  # ¿Dentro del rango de distancia?
    distance_meters: float
    validation_error: Optional[str] = None
    fraud_flags: Optional[List[str]] = None
    message: str
    
    class Config:
        from_attributes = True


class CheckOutRequest(BaseModel):
    """Check-out del cliente"""
    visit_id: str
    latitude: float
    longitude: float
    notes: Optional[str] = None


class VisitResponse(BaseModel):
    """Respuesta de visita completa"""
    id: str
    seller_id: str
    client_id: str
    route_id: str
    
    checkin_time: Optional[datetime]
    checkin_distance_meters: Optional[float]
    checkin_is_valid: bool
    checkin_validation_error: Optional[str]
    
    checkout_time: Optional[datetime]
    checkout_distance_meters: Optional[float]
    
    fraud_flags: Optional[List[str]]
    notes: Optional[str]
    
    class Config:
        from_attributes = True


class ClientResponse(BaseModel):
    """Cliente con coordenadas"""
    id: str
    name: str
    address: str
    phone: str
    email: Optional[str]
    client_type: str
    status: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    class Config:
        from_attributes = True


class SellerResponse(BaseModel):
    """Vendedor"""
    id: str
    name: str
    email: str
    phone: str
    is_active: bool
    
    class Config:
        from_attributes = True


class ClientCreateRequest(BaseModel):
    """Modelo para crear cliente"""
    name: str
    address: str
    phone: str
    email: Optional[str] = None
    client_type: str
    latitude: float
    longitude: float
    status: Optional[str] = "active"
    
    class Config:
        from_attributes = True


class ClientUpdateRequest(BaseModel):
    """Modelo para actualizar cliente"""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    client_type: Optional[str] = None
    status: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    class Config:
        from_attributes = True


class RouteCreateRequest(BaseModel):
    """Modelo para crear ruta"""
    seller_id: str
    client_id: str
    planned_date: str  # YYYY-MM-DD (solo fecha)
    status: Optional[str] = "pending"
    
    class Config:
        from_attributes = True


class RouteUpdateRequest(BaseModel):
    """Modelo para actualizar ruta"""
    seller_id: Optional[str] = None
    client_id: Optional[str] = None
    planned_date: Optional[str] = None
    status: Optional[str] = None
    
    class Config:
        from_attributes = True


class RouteResponse(BaseModel):
    """Ruta con cliente y vendedor relacionados"""
    id: str
    seller_id: str
    client_id: str
    planned_date: datetime
    status: str
    created_at: datetime
    client: Optional[ClientResponse] = None
    seller: Optional[SellerResponse] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# FUNCIONES GEOESPACIALES (PostGIS + Validación)
# ============================================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calcula distancia en metros entre dos puntos GPS
    Fórmula de Haversine
    """
    R = 6371000  # Radio de la Tierra en metros
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def validate_checkin(
    distance_meters: float,
    checkin_time: datetime,
    client_found: bool,
    db: Session,
    seller_id: str,
    client_id: str
) -> tuple[bool, Optional[str], List[str]]:
    """
    ✅ LÓGICA DE VALIDACIÓN ROBUSTA
    
    Retorna: (is_valid, error_message, fraud_flags)
    """
    
    VALID_DISTANCE = 100  # Metros
    BUSINESS_HOURS_START = 8
    BUSINESS_HOURS_END = 18
    
    fraud_flags = []
    is_valid = True
    error_message = None
    
    # 1️⃣ VALIDACIÓN DE DISTANCIA
    if distance_meters > VALID_DISTANCE:
        is_valid = False
        error_message = f"Ubicación fuera de rango: {distance_meters:.0f}m (máximo: {VALID_DISTANCE}m)"
        fraud_flags.append(f"OUT_OF_RANGE|{distance_meters:.0f}m")
    
    # 2️⃣ VALIDACIÓN DE HORARIO
    hour = checkin_time.hour
    if hour < BUSINESS_HOURS_START or hour >= BUSINESS_HOURS_END:
        is_valid = False
        error_message = f"Fuera de horario comercial ({BUSINESS_HOURS_START}:00-{BUSINESS_HOURS_END}:00)"
        fraud_flags.append(f"OUT_OF_HOURS|{hour}:00")
    
    # 3️⃣ VALIDACIÓN MANUAL (cliente confirmado)
    if not client_found:
        is_valid = False
        error_message = "Cliente no confirmado en la ubicación"
        fraud_flags.append("CLIENT_NOT_FOUND")
    
    # 4️⃣ DETECCIÓN DE FRAUDE: Check-ins repetidos en corto tiempo
    recent_visits = db.query(Visit).filter(
        Visit.seller_id == seller_id,
        Visit.client_id == client_id,
        Visit.checkin_time > checkin_time - timedelta(hours=1),
        Visit.checkin_time < checkin_time
    ).count()
    
    if recent_visits > 0:
        fraud_flags.append(f"DUPLICATE_CHECKIN|{recent_visits} en última hora")
    
    # 5️⃣ DETECCIÓN DE FRAUDE: Múltiples ubicaciones en segundos
    other_visits = db.query(Visit).filter(
        Visit.seller_id == seller_id,
        Visit.checkin_time > checkin_time - timedelta(seconds=60),
        Visit.checkin_time < checkin_time,
        Visit.client_id != client_id
    ).all()
    
    if len(other_visits) > 0:
        fraud_flags.append(f"MULTIPLE_LOCATIONS|{len(other_visits)} check-ins en 1 minuto")
    
    return is_valid, error_message, fraud_flags


# ============================================================================
# RUTAS API (ENDPOINTS)
# ============================================================================

# --- VENDEDORES ---

@app.get("/sellers/")
def list_sellers(db: Session = Depends(get_db)):
    """Listar todos los vendedores (activos e inactivos)"""
    sellers = db.query(Seller).all()
    return sellers


@app.post("/sellers/")
def create_seller(seller: SellerCreate, db: Session = Depends(get_db)):
    """Crear vendedor"""
    try:
        new_seller = Seller(
            name=seller.name,
            email=seller.email,
            phone=seller.phone,
            is_active=seller.is_active
        )
        db.add(new_seller)
        db.commit()
        db.refresh(new_seller)
        return {
            "id": str(new_seller.id),
            "name": new_seller.name,
            "email": new_seller.email,
            "phone": new_seller.phone,
            "is_active": new_seller.is_active,
            "created_at": new_seller.created_at.isoformat() if new_seller.created_at else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creando vendedor: {str(e)}")


@app.get("/sellers/{seller_id}")
def get_seller(seller_id: str, db: Session = Depends(get_db)):
    """Obtener vendedor por ID"""
    try:
        seller_uuid = uuid.UUID(seller_id)
        seller = db.query(Seller).filter(Seller.id == seller_uuid).first()
        if not seller:
            raise HTTPException(status_code=404, detail="Vendedor no encontrado")
        
        return {
            "id": str(seller.id),
            "name": seller.name,
            "email": seller.email,
            "phone": seller.phone,
            "is_active": seller.is_active,
            "created_at": seller.created_at.isoformat() if seller.created_at else None
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"seller_id inválido: {seller_id}")


@app.put("/sellers/{seller_id}")
def update_seller(seller_id: str, seller: SellerCreate, db: Session = Depends(get_db)):
    """Actualizar vendedor"""
    try:
        seller_uuid = uuid.UUID(seller_id)
        db_seller = db.query(Seller).filter(Seller.id == seller_uuid).first()
        
        if not db_seller:
            raise HTTPException(status_code=404, detail="Vendedor no encontrado")
        
        db_seller.name = seller.name
        db_seller.email = seller.email
        db_seller.phone = seller.phone
        db_seller.is_active = seller.is_active
        
        db.commit()
        db.refresh(db_seller)
        
        return {
            "id": str(db_seller.id),
            "name": db_seller.name,
            "email": db_seller.email,
            "phone": db_seller.phone,
            "is_active": db_seller.is_active,
            "created_at": db_seller.created_at.isoformat() if db_seller.created_at else None
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"seller_id inválido: {seller_id}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error actualizando vendedor: {str(e)}")


@app.delete("/sellers/{seller_id}")
def delete_seller(seller_id: str, db: Session = Depends(get_db)):
    """Eliminar vendedor"""
    try:
        seller_uuid = uuid.UUID(seller_id)
        db_seller = db.query(Seller).filter(Seller.id == seller_uuid).first()
        
        if not db_seller:
            raise HTTPException(status_code=404, detail="Vendedor no encontrado")
        
        db.delete(db_seller)
        db.commit()
        
        return {
            "message": "Vendedor eliminado correctamente",
            "seller_id": seller_id
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"seller_id inválido: {seller_id}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error eliminando vendedor: {str(e)}")


# --- CLIENTES ---

@app.get("/clients/")
def list_clients(db: Session = Depends(get_db)):
    """Listar clientes con coordenadas convertidas a lat/lng"""
    from sqlalchemy import func
    
    clients_db = db.query(Client).filter(Client.status == "active").all()
    
    result = []
    for client in clients_db:
        try:
            # Convertir Geography a WKT: "POINT(-0.187 38.960)"
            coords_wkt = db.query(func.ST_AsText(client.location)).scalar()
            
            if coords_wkt and coords_wkt.startswith("POINT"):
                # Parse "POINT(lng lat)"
                coords_str = coords_wkt.replace("POINT(", "").replace(")", "")
                lng, lat = map(float, coords_str.split())
            else:
                lng, lat = None, None
            
            result.append({
                "id": str(client.id),
                "name": client.name,
                "address": client.address,
                "phone": client.phone,
                "email": client.email,
                "client_type": client.client_type,
                "status": client.status,
                "latitude": lat,
                "longitude": lng,
                "created_at": client.created_at.isoformat() if client.created_at else None
            })
        except Exception as e:
            print(f"⚠️ Error procesando cliente {client.id}: {str(e)}")
            continue
    
    return result


@app.post("/clients/")
def create_client(
    request: ClientCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Crear cliente con ubicación GPS
    El location se guarda como POINT(lng lat) en WGS84
    """
    from sqlalchemy import func
    
    try:
        # PostGIS requiere: POINT(longitude latitude)
        location_wkt = f"POINT({request.longitude} {request.latitude})"
        
        client = Client(
            name=request.name,
            address=request.address,
            phone=request.phone,
            email=request.email,
            client_type=request.client_type,
            status=request.status,
            location=func.ST_GeomFromText(location_wkt, 4326)
        )
        
        db.add(client)
        db.commit()
        db.refresh(client)
        
        # Convertir Geography a lat/lng para la respuesta
        coords_wkt = db.query(func.ST_AsText(client.location)).scalar()
        lat, lng = None, None
        if coords_wkt and coords_wkt.startswith("POINT"):
            coords_str = coords_wkt.replace("POINT(", "").replace(")", "")
            lng, lat = map(float, coords_str.split())
        
        return {
            "id": str(client.id),
            "name": client.name,
            "address": client.address,
            "phone": client.phone,
            "email": client.email,
            "client_type": client.client_type,
            "status": client.status,
            "latitude": lat,
            "longitude": lng,
            "message": "Cliente creado correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear cliente: {str(e)}")


@app.put("/clients/{client_id}")
def update_client(
    client_id: str,
    request: ClientUpdateRequest,
    db: Session = Depends(get_db)
):
    """Actualizar cliente"""
    from sqlalchemy import func
    
    try:
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"client_id inválido: {client_id}")
    
    client = db.query(Client).filter(Client.id == client_uuid).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Actualizar campos
    if request.name:
        client.name = request.name
    if request.address:
        client.address = request.address
    if request.phone:
        client.phone = request.phone
    if request.email:
        client.email = request.email
    if request.client_type:
        client.client_type = request.client_type
    if request.status:
        client.status = request.status
    
    # Actualizar ubicación si se proporciona
    if request.latitude is not None and request.longitude is not None:
        location_wkt = f"POINT({request.longitude} {request.latitude})"
        client.location = func.ST_GeomFromText(location_wkt, 4326)
    
    db.commit()
    db.refresh(client)
    
    # Convertir Geography a lat/lng
    coords_wkt = db.query(func.ST_AsText(client.location)).scalar()
    lat, lng = None, None
    if coords_wkt and coords_wkt.startswith("POINT"):
        coords_str = coords_wkt.replace("POINT(", "").replace(")", "")
        lng, lat = map(float, coords_str.split())
    
    return {
        "id": str(client.id),
        "name": client.name,
        "address": client.address,
        "phone": client.phone,
        "email": client.email,
        "client_type": client.client_type,
        "status": client.status,
        "latitude": lat,
        "longitude": lng,
        "message": "Cliente actualizado"
    }


@app.delete("/clients/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db)):
    """Eliminar cliente"""
    try:
        client_uuid = uuid.UUID(client_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"client_id inválido: {client_id}")
    
    client = db.query(Client).filter(Client.id == client_uuid).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    db.delete(client)
    db.commit()
    
    return {"id": str(client.id), "message": "Cliente eliminado"}


@app.get("/clients/nearby/")
def nearby_clients(
    latitude: float,
    longitude: float,
    radius_km: float = 5,
    db: Session = Depends(get_db)
):
    """
    Buscar clientes cercanos usando PostGIS
    ST_DWithin = búsqueda por distancia en geografia
    """
    from sqlalchemy import func
    
    radius_meters = radius_km * 1000
    point_wkt = f"POINT({longitude} {latitude})"
    
    nearby_db = db.query(Client).filter(
        func.ST_DWithin(
            Client.location,
            func.ST_GeomFromText(point_wkt, 4326),
            radius_meters
        )
    ).all()
    
    result = []
    for client in nearby_db:
        try:
            coords_wkt = db.query(func.ST_AsText(client.location)).scalar()
            
            if coords_wkt and coords_wkt.startswith("POINT"):
                coords_str = coords_wkt.replace("POINT(", "").replace(")", "")
                lng, lat = map(float, coords_str.split())
                
                # Calcular distancia
                distance = db.query(
                    func.ST_DistanceSphere(
                        func.ST_GeomFromText(point_wkt, 4326),
                        client.location
                    )
                ).scalar()
            else:
                lng, lat, distance = None, None, None
            
            result.append({
                "id": str(client.id),
                "name": client.name,
                "address": client.address,
                "phone": client.phone,
                "email": client.email,
                "client_type": client.client_type,
                "status": client.status,
                "latitude": lat,
                "longitude": lng,
                "distance_meters": float(distance) if distance else None,
                "created_at": client.created_at.isoformat() if client.created_at else None
            })
        except Exception as e:
            print(f"⚠️ Error procesando cliente cercano {client.id}: {str(e)}")
            continue
    
    return result


# --- RUTAS ---

@app.get("/routes/", response_model=List[RouteResponse])
def list_routes(
    seller_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar rutas con filtros - ✅ INCLUYE CLIENT Y SELLER"""
    from sqlalchemy import func
    
    query = db.query(Route).options(
        joinedload(Route.client),
        joinedload(Route.seller)
    )
    
    if seller_id:
        try:
            seller_uuid = uuid.UUID(seller_id)
            query = query.filter(Route.seller_id == seller_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"seller_id inválido: {seller_id}")
    
    if status:
        query = query.filter(Route.status == status)
    
    routes = query.all()
    
    # Convertir Geography a lat/lng
    result = []
    for route in routes:
        route_dict = {
            "id": str(route.id),
            "seller_id": str(route.seller_id),
            "client_id": str(route.client_id),
            "planned_date": route.planned_date,
            "status": route.status,
            "created_at": route.created_at,
            "seller": {
                "id": str(route.seller.id),
                "name": route.seller.name,
                "email": route.seller.email,
                "phone": route.seller.phone,
                "is_active": route.seller.is_active
            } if route.seller else None,
            "client": None
        }
        
        # Procesar cliente con conversión de Geography
        if route.client:
            try:
                coords_wkt = db.query(func.ST_AsText(route.client.location)).scalar()
                lat, lng = None, None
                
                if coords_wkt and coords_wkt.startswith("POINT"):
                    coords_str = coords_wkt.replace("POINT(", "").replace(")", "")
                    lng, lat = map(float, coords_str.split())
                
                route_dict["client"] = {
                    "id": str(route.client.id),
                    "name": route.client.name,
                    "address": route.client.address,
                    "phone": route.client.phone,
                    "email": route.client.email,
                    "client_type": route.client.client_type,
                    "status": route.client.status,
                    "latitude": lat,
                    "longitude": lng
                }
            except Exception as e:
                print(f"⚠️ Error procesando cliente {route.client.id}: {str(e)}")
                route_dict["client"] = {
                    "id": str(route.client.id),
                    "name": route.client.name,
                    "address": route.client.address,
                    "phone": route.client.phone,
                    "email": route.client.email,
                    "client_type": route.client.client_type,
                    "status": route.client.status,
                    "latitude": None,
                    "longitude": None
                }
        
        result.append(route_dict)
    
    return result


@app.post("/routes/")
def create_route(
    request: RouteCreateRequest,
    db: Session = Depends(get_db)
):
    """Crear ruta - solo fecha, hora se registra en check-in"""
    try:
        seller_uuid = uuid.UUID(request.seller_id)
        client_uuid = uuid.UUID(request.client_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"IDs inválidos: {str(e)}")
    
    try:
        # Convertir YYYY-MM-DD a DateTime (00:00:00)
        planned_date = datetime.strptime(request.planned_date, "%Y-%m-%d")
        
        route = Route(
            seller_id=seller_uuid,
            client_id=client_uuid,
            planned_date=planned_date,
            status=request.status
        )
        
        db.add(route)
        db.commit()
        db.refresh(route)
        
        return {
            "id": str(route.id),
            "seller_id": str(route.seller_id),
            "client_id": str(route.client_id),
            "planned_date": route.planned_date.isoformat(),
            "status": route.status,
            "message": "Ruta creada correctamente"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al crear ruta: {str(e)}")


@app.put("/routes/{route_id}")
def update_route(
    route_id: str,
    request: RouteUpdateRequest,
    db: Session = Depends(get_db)
):
    """Actualizar ruta"""
    try:
        route_uuid = uuid.UUID(route_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"route_id inválido: {route_id}")
    
    route = db.query(Route).filter(Route.id == route_uuid).first()
    if not route:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    
    # Actualizar campos
    if request.seller_id:
        try:
            route.seller_id = uuid.UUID(request.seller_id)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"seller_id inválido: {request.seller_id}")
    
    if request.client_id:
        try:
            route.client_id = uuid.UUID(request.client_id)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"client_id inválido: {request.client_id}")
    
    if request.planned_date:
        try:
            route.planned_date = datetime.strptime(request.planned_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"planned_date inválido: {request.planned_date}")
    
    if request.status:
        route.status = request.status
    
    db.commit()
    db.refresh(route)
    
    return {
        "id": str(route.id),
        "seller_id": str(route.seller_id),
        "client_id": str(route.client_id),
        "planned_date": route.planned_date.isoformat(),
        "status": route.status,
        "message": "Ruta actualizada"
    }


@app.delete("/routes/{route_id}")
def delete_route(route_id: str, db: Session = Depends(get_db)):
    """Eliminar ruta"""
    try:
        route_uuid = uuid.UUID(route_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"route_id inválido: {route_id}")
    
    route = db.query(Route).filter(Route.id == route_uuid).first()
    if not route:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    
    db.delete(route)
    db.commit()
    
    return {"id": str(route.id), "message": "Ruta eliminada"}


# ============================================================================
# ✅ CHECK-IN/CHECK-OUT REDISEÑADO CON VALIDACIÓN ROBUSTA
# ============================================================================

@app.post("/visits/checkin/", response_model=CheckInResponse)
async def checkin(
    request: CheckInRequest,
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    ✅ CHECK-IN MEJORADO CON VALIDACIÓN GEOESPACIAL ROBUSTA
    
    1. Calcula distancia exacta al cliente
    2. Valida horario comercial
    3. Solicita confirmación manual del cliente
    4. Detecta fraudes (ubicaciones falsas, duplicados, etc)
    5. Guarda foto geoetiquetada como prueba
    
    Retorna: éxito de la validación + flags de fraude si aplica
    """
    from sqlalchemy import func
    
    try:
        # Validar que IDs sean UUIDs válidos
        try:
            route_id = uuid.UUID(request.route_id)
            seller_id = uuid.UUID(request.seller_id)
            client_id = uuid.UUID(request.client_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"IDs inválidos: {str(e)}")
        
        # Obtener cliente para extraer su ubicación
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Obtener ruta
        route = db.query(Route).filter(Route.id == route_id).first()
        if not route:
            raise HTTPException(status_code=404, detail="Ruta no encontrada")
        
        # 📍 CALCULAR DISTANCIA: Ubicación del vendedor vs cliente
        # Usamos PostGIS para precisión (elipsoide WGS84)
        checkin_point_wkt = f"POINT({request.longitude} {request.latitude})"
        
        distance_result = db.query(
            func.ST_DistanceSphere(
                func.ST_GeomFromText(checkin_point_wkt, 4326),
                client.location
            )
        ).scalar()
        
        distance_meters = float(distance_result) if distance_result else 0
        
        # 🕐 HORA DEL CHECK-IN
        checkin_time = datetime.utcnow()
        
        # ✅ VALIDAR CHECK-IN
        is_valid, error_message, fraud_flags = validate_checkin(
            distance_meters=distance_meters,
            checkin_time=checkin_time,
            client_found=request.client_found,
            db=db,
            seller_id=seller_id,
            client_id=client_id
        )
        
        # 📸 GUARDAR FOTO GEOETIQUETADA (si aplica)
        photo_url = None
        if photo:
            # Crear directorio de fotos
            photo_dir = Path("./uploads/visits")
            photo_dir.mkdir(parents=True, exist_ok=True)
            
            # Guardar con nombre único
            visit_id = str(uuid.uuid4())
            photo_path = photo_dir / f"{visit_id}_{photo.filename}"
            
            with open(photo_path, "wb") as f:
                contents = await photo.read()
                f.write(contents)
            
            photo_url = f"/uploads/visits/{visit_id}_{photo.filename}"
        
        # 💾 GUARDAR REGISTRO DE VISITA
        visit = Visit(
            route_id=route_id,
            seller_id=seller_id,
            client_id=client_id,
            
            checkin_time=checkin_time,
            checkin_location=func.ST_GeomFromText(checkin_point_wkt, 4326),
            checkin_distance_meters=distance_meters,
            checkin_photo_url=photo_url,
            
            checkin_is_valid=is_valid,
            checkin_validation_error=error_message,
            fraud_flags="|".join(fraud_flags) if fraud_flags else None,
            notes=request.notes
        )
        
        db.add(visit)
        db.commit()
        db.refresh(visit)
        
        # 📊 GENERAR RESPUESTA
        message = "✅ Check-in exitoso" if is_valid else f"⚠️ Check-in con advertencias: {error_message}"
        
        return CheckInResponse(
            visit_id=str(visit.id),
            success=True,
            is_valid=is_valid,
            distance_meters=distance_meters,
            validation_error=error_message,
            fraud_flags=fraud_flags if fraud_flags else None,
            message=message
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en check-in: {str(e)}")


@app.post("/visits/checkout/", response_model=CheckInResponse)
async def checkout(
    request: CheckOutRequest,
    db: Session = Depends(get_db)
):
    """
    CHECK-OUT: Finalizar visita
    """
    from sqlalchemy import func
    
    try:
        # Obtener visita
        visit = db.query(Visit).filter(Visit.id == request.visit_id).first()
        if not visit:
            raise HTTPException(status_code=404, detail="Visita no encontrada")
        
        # Obtener cliente
        client = db.query(Client).filter(Client.id == visit.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Calcular distancia checkout
        checkout_point_wkt = f"POINT({request.longitude} {request.latitude})"
        
        distance_result = db.query(
            func.ST_DistanceSphere(
                func.ST_GeomFromText(checkout_point_wkt, 4326),
                client.location
            )
        ).scalar()
        
        distance_meters = float(distance_result) if distance_result else 0
        
        # Actualizar visita
        visit.checkout_time = datetime.utcnow()
        visit.checkout_location = func.ST_GeomFromText(checkout_point_wkt, 4326)
        visit.checkout_distance_meters = distance_meters
        if request.notes:
            visit.notes = request.notes
        
        db.commit()
        db.refresh(visit)
        
        # Actualizar estado de ruta
        route = db.query(Route).filter(Route.id == visit.route_id).first()
        if route:
            route.status = "completed"
            db.commit()
        
        return CheckInResponse(
            visit_id=str(visit.id),
            success=True,
            is_valid=True,
            distance_meters=distance_meters,
            message="✅ Check-out completado"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en check-out: {str(e)}")


# --- VISITAS ---

@app.get("/visits/")
def list_visits(
    seller_id: Optional[str] = None,
    client_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar visitas con filtros"""
    query = db.query(Visit)
    
    if seller_id:
        try:
            seller_uuid = uuid.UUID(seller_id)
            query = query.filter(Visit.seller_id == seller_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"seller_id inválido: {seller_id}")
    
    if client_id:
        try:
            client_uuid = uuid.UUID(client_id)
            query = query.filter(Visit.client_id == client_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"client_id inválido: {client_id}")
    
    return query.order_by(Visit.created_at.desc()).all()


# --- DASHBOARD ---

@app.get("/dashboard/stats/")
def dashboard_stats(db: Session = Depends(get_db)):
    """
    ✅ DASHBOARD CON MÉTRICAS DE FRAUDE Y VALIDACIÓN
    """
    from sqlalchemy import func
    
    # Vendedores activos
    active_sellers = db.query(func.count(Seller.id)).filter(Seller.is_active == True).scalar()
    
    # Visitas del día
    today = datetime.utcnow().date()
    visits_today = db.query(func.count(Visit.id)).filter(
        func.date(Visit.checkin_time) == today
    ).scalar()
    
    # Check-ins válidos vs inválidos
    valid_checkins = db.query(func.count(Visit.id)).filter(
        Visit.checkin_is_valid == True,
        func.date(Visit.checkin_time) == today
    ).scalar()
    
    invalid_checkins = db.query(func.count(Visit.id)).filter(
        Visit.checkin_is_valid == False,
        func.date(Visit.checkin_time) == today
    ).scalar()
    
    # Visitas con flags de fraude
    fraud_visits = db.query(func.count(Visit.id)).filter(
        Visit.fraud_flags.isnot(None),
        func.date(Visit.checkin_time) == today
    ).scalar()
    
    # Distancia promedio de check-ins
    avg_distance = db.query(func.avg(Visit.checkin_distance_meters)).filter(
        func.date(Visit.checkin_time) == today,
        Visit.checkin_distance_meters.isnot(None)
    ).scalar()
    
    return {
        "date": today.isoformat(),
        "active_sellers": active_sellers or 0,
        "total_visits_today": visits_today or 0,
        "valid_checkins": valid_checkins or 0,
        "invalid_checkins": invalid_checkins or 0,
        "fraud_detections": fraud_visits or 0,
        "average_distance_meters": round(float(avg_distance) if avg_distance else 0, 2),
        "quality_score": f"{round(((valid_checkins or 0) / max(visits_today or 1, 1)) * 100)}%"
    }


@app.get("/dashboard/fraud-alerts/")
def fraud_alerts(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    ✅ ALERTAS DE FRAUDE PARA GERENCIA
    Muestra visitas con flags sospechosos en las últimas N horas
    """
    from sqlalchemy import func
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    suspicious_visits = db.query(
        Visit.id,
        Visit.seller_id,
        Visit.client_id,
        Visit.checkin_time,
        Visit.checkin_distance_meters,
        Visit.fraud_flags
    ).filter(
        Visit.fraud_flags.isnot(None),
        Visit.checkin_time > cutoff_time
    ).order_by(Visit.checkin_time.desc()).all()
    
    alerts = []
    for visit in suspicious_visits:
        seller = db.query(Seller).filter(Seller.id == visit.seller_id).first()
        client = db.query(Client).filter(Client.id == visit.client_id).first()
        
        alerts.append({
            "visit_id": str(visit.id),
            "seller": seller.name if seller else "Unknown",
            "client": client.name if client else "Unknown",
            "timestamp": visit.checkin_time.isoformat(),
            "distance_meters": visit.checkin_distance_meters,
            "fraud_flags": visit.fraud_flags.split("|") if visit.fraud_flags else []
        })
    
    return {
        "period_hours": hours,
        "total_alerts": len(alerts),
        "alerts": alerts
    }


# --- OPORTUNIDADES ---

@app.get("/opportunities/")
def list_opportunities(seller_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Listar oportunidades"""
    query = db.query(Opportunity)
    
    if seller_id:
        try:
            seller_uuid = uuid.UUID(seller_id)
            query = query.filter(Opportunity.seller_id == seller_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"seller_id inválido: {seller_id}")
    
    return query.all()


@app.post("/opportunities/")
def create_opportunity(
    seller_id: str,
    client_id: str,
    title: str,
    estimated_value: float,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Crear oportunidad"""
    try:
        seller_uuid = uuid.UUID(seller_id)
        client_uuid = uuid.UUID(client_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"IDs inválidos: {str(e)}")
    
    opportunity = Opportunity(
        seller_id=seller_uuid,
        client_id=client_uuid,
        title=title,
        description=description,
        estimated_value=estimated_value,
        status="open"
    )
    
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    
    return opportunity


# --- HEALTH CHECK ---

@app.get("/health/")
def health_check():
    """Health check para Railway"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
