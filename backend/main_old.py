from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/salesmen_tracker")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
    seller_id = Column(PG_UUID(as_uuid=True), nullable=False)
    client_id = Column(PG_UUID(as_uuid=True), nullable=False)
    
    planned_date = Column(DateTime, nullable=False)
    planned_time = Column(String(5), nullable=False)  # HH:MM
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys & Relaciones
    seller = relationship("Seller", back_populates="routes")
    client = relationship("Client", back_populates="routes")
    visits = relationship("Visit", back_populates="route")


class Visit(Base):
    __tablename__ = "visits"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(PG_UUID(as_uuid=True), nullable=False)
    seller_id = Column(PG_UUID(as_uuid=True), nullable=False)
    client_id = Column(PG_UUID(as_uuid=True), nullable=False)
    
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
    seller_id = Column(PG_UUID(as_uuid=True), nullable=False)
    client_id = Column(PG_UUID(as_uuid=True), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    estimated_value = Column(Float, nullable=False)
    status = Column(String(20), default="open")  # open, in_negotiation, won, lost
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    seller = relationship("Seller", back_populates="opportunities")
    client = relationship("Client", back_populates="opportunities")


# Crear tablas
Base.metadata.create_all(bind=engine)

# ============================================================================
# SCHEMAS PYDANTIC (Validación de Entrada/Salida)
# ============================================================================

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
    """Listar vendedores"""
    sellers = db.query(Seller).filter(Seller.is_active == True).all()
    return sellers


@app.post("/sellers/")
def create_seller(name: str, email: str, phone: str, db: Session = Depends(get_db)):
    """Crear vendedor"""
    seller = Seller(name=name, email=email, phone=phone)
    db.add(seller)
    db.commit()
    db.refresh(seller)
    return seller


# --- CLIENTES ---

@app.get("/clients/")
def list_clients(db: Session = Depends(get_db)):
    """Listar clientes"""
    from sqlalchemy import func
    
    clients = db.query(
        Client.id,
        Client.name,
        Client.address,
        Client.phone,
        Client.email,
        Client.client_type,
        Client.status,
        func.ST_AsText(Client.location).label("location")
    ).filter(Client.status == "active").all()
    
    return clients


@app.post("/clients/")
def create_client(
    name: str,
    address: str,
    phone: str,
    latitude: float,
    longitude: float,
    client_type: str,
    email: Optional[str] = None,
    db: Session = Depends(get_db) 
):
    """
    Crear cliente con ubicación GPS
    El location se guarda como POINT(lng lat) en WGS84
    """
    from sqlalchemy import func
    
    # PostGIS requiere: POINT(longitude latitude)
    location_wkt = f"POINT({longitude} {latitude})"
    
    client = Client(
        name=name,
        address=address,
        phone=phone,
        email=email,
        client_type=client_type,
        location=func.ST_GeomFromText(location_wkt, 4326)
    )
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    return {"id": str(client.id), "name": client.name, "message": "Cliente creado"}


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
    from sqlalchemy import func, text
    
    radius_meters = radius_km * 1000
    point_wkt = f"POINT({longitude} {latitude})"
    
    nearby = db.query(Client).filter(
        func.ST_DWithin(
            Client.location,
            func.ST_GeomFromText(point_wkt, 4326),
            radius_meters
        )
    ).all()
    
    return nearby


# --- RUTAS ---

@app.get("/routes/")
def list_routes(
    seller_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db) 
):
    """Listar rutas con filtros"""
    query = db.query(Route)
    
    if seller_id:
        query = query.filter(Route.seller_id == seller_id)
    if status:
        query = query.filter(Route.status == status)
    
    return query.all()


@app.post("/routes/")
def create_route(
    seller_id: str,
    client_id: str,
    planned_date: str,  # YYYY-MM-DD
    planned_time: str,  # HH:MM
    db: Session = Depends(get_db) 
):
    """Crear ruta"""
    route = Route(
        seller_id=seller_id,
        client_id=client_id,
        planned_date=datetime.fromisoformat(f"{planned_date}T{planned_time}:00"),
        planned_time=planned_time,
        status="pending"
    )
    
    db.add(route)
    db.commit()
    db.refresh(route)
    
    return route


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
        # Obtener cliente para extraer su ubicación
        client = db.query(Client).filter(Client.id == request.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Obtener ruta
        route = db.query(Route).filter(Route.id == request.route_id).first()
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
            seller_id=request.seller_id,
            client_id=request.client_id
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
            route_id=request.route_id,
            seller_id=request.seller_id,
            client_id=request.client_id,
            
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
        query = query.filter(Visit.seller_id == seller_id)
    if client_id:
        query = query.filter(Visit.client_id == client_id)
    
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
        query = query.filter(Opportunity.seller_id == seller_id)
    
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
    opportunity = Opportunity(
        seller_id=seller_id,
        client_id=client_id,
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
