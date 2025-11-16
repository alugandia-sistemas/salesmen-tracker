# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_Distance, ST_DWithin
import os

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/salesmen_tracker")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==================== MODELOS DE BASE DE DATOS ====================

class Seller(Base):
    __tablename__ = "sellers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    routes = relationship("Route", back_populates="seller")
    visits = relationship("Visit", back_populates="seller")
    opportunities = relationship("Opportunity", back_populates="seller")


class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    address = Column(String(300))
    phone = Column(String(20))
    email = Column(String(100))
    status = Column(String(20), default="active")  # active, inactive, pending
    # PostGIS geometry column para coordenadas
    location = Column(Geometry('POINT', srid=4326))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    routes = relationship("Route", back_populates="client")
    visits = relationship("Visit", back_populates="client")
    opportunities = relationship("Opportunity", back_populates="client")


class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    seller = relationship("Seller", back_populates="routes")
    client = relationship("Client", back_populates="routes")
    visits = relationship("Visit", back_populates="route")


class Visit(Base):
    __tablename__ = "visits"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    check_in_time = Column(DateTime, nullable=False)
    check_out_time = Column(DateTime)
    # Ubicación del check-in (PostGIS)
    check_in_location = Column(Geometry('POINT', srid=4326))
    # Ubicación del check-out (PostGIS)
    check_out_location = Column(Geometry('POINT', srid=4326))
    notes = Column(Text)
    distance_to_client = Column(Float)  # Distancia en metros desde el check-in al cliente
    created_at = Column(DateTime, default=datetime.utcnow)
    
    route = relationship("Route", back_populates="visits")
    seller = relationship("Seller", back_populates="visits")
    client = relationship("Client", back_populates="visits")


class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    estimated_value = Column(Float)
    status = Column(String(20), default="open")  # open, negotiating, won, lost
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)
    
    client = relationship("Client", back_populates="opportunities")
    seller = relationship("Seller", back_populates="opportunities")


# ==================== MODELOS PYDANTIC (SCHEMAS) ====================

class SellerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None

class SellerResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    active: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ClientCreate(BaseModel):
    name: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    latitude: float
    longitude: float

class ClientResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    status: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RouteCreate(BaseModel):
    seller_id: int
    client_id: int
    scheduled_date: datetime
    notes: Optional[str] = None

class RouteResponse(BaseModel):
    id: int
    seller_id: int
    client_id: int
    scheduled_date: datetime
    status: str
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CheckInCreate(BaseModel):
    route_id: int
    latitude: float
    longitude: float
    notes: Optional[str] = None

class CheckOutCreate(BaseModel):
    visit_id: int
    latitude: float
    longitude: float

class VisitResponse(BaseModel):
    id: int
    route_id: int
    seller_id: int
    client_id: int
    check_in_time: datetime
    check_out_time: Optional[datetime]
    notes: Optional[str]
    distance_to_client: Optional[float]
    check_in_lat: Optional[float] = None
    check_in_lng: Optional[float] = None
    
    class Config:
        from_attributes = True


class OpportunityCreate(BaseModel):
    client_id: int
    seller_id: int
    title: str
    description: Optional[str]
    estimated_value: Optional[float]

class OpportunityResponse(BaseModel):
    id: int
    client_id: int
    seller_id: int
    title: str
    description: Optional[str]
    estimated_value: Optional[float]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    active_sellers: int
    total_visits_today: int
    pending_routes: int
    open_opportunities: int


# ==================== FASTAPI APP ====================

app = FastAPI(title="Salesmen Tracker API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== ENDPOINTS ====================

@app.on_event("startup")
def startup_event():
    # Crear tablas
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Salesmen Tracker API", "version": "1.0.0"}


# ===== SELLERS =====

@app.post("/sellers/", response_model=SellerResponse)
def create_seller(seller: SellerCreate, db: Session = Depends(get_db)):
    db_seller = Seller(**seller.dict())
    db.add(db_seller)
    db.commit()
    db.refresh(db_seller)
    return db_seller


@app.get("/sellers/", response_model=List[SellerResponse])
def get_sellers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sellers = db.query(Seller).offset(skip).limit(limit).all()
    return sellers


@app.get("/sellers/{seller_id}", response_model=SellerResponse)
def get_seller(seller_id: int, db: Session = Depends(get_db)):
    seller = db.query(Seller).filter(Seller.id == seller_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return seller


# ===== CLIENTS =====

@app.post("/clients/", response_model=ClientResponse)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    # Crear punto geográfico con PostGIS
    from geoalchemy2.shape import from_shape
    from shapely.geometry import Point
    
    point = Point(client.longitude, client.latitude)
    
    db_client = Client(
        name=client.name,
        address=client.address,
        phone=client.phone,
        email=client.email,
        location=f'POINT({client.longitude} {client.latitude})'
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    # Agregar coordenadas a la respuesta
    response = ClientResponse.from_orm(db_client)
    response.latitude = client.latitude
    response.longitude = client.longitude
    return response


@app.get("/clients/", response_model=List[ClientResponse])
def get_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    from geoalchemy2.functions import ST_X, ST_Y
    
    clients = db.query(Client).offset(skip).limit(limit).all()  # ← CORREGIDO: Client en vez de Seller
    result = []
    
    for client in clients:
        client_dict = ClientResponse.model_validate(client)
        # Extraer coordenadas del geometry si existen
        if client.location:
            coords = db.query(ST_X(client.location), ST_Y(client.location)).first()
            if coords:
                client_dict.longitude = coords[0]
                client_dict.latitude = coords[1]
        result.append(client_dict)
    
    return result


@app.get("/clients/nearby/")
def get_nearby_clients(latitude: float, longitude: float, radius_km: float = 5, db: Session = Depends(get_db)):
    """Obtener clientes cercanos a una ubicación (radio en kilómetros)"""
    from geoalchemy2.functions import ST_DWithin
    from geoalchemy2 import Geography
    
    # Crear punto de referencia
    point = f'POINT({longitude} {latitude})'
    radius_meters = radius_km * 1000
    
    # Consulta con PostGIS para encontrar clientes cercanos
    clients = db.query(Client).filter(
        ST_DWithin(
            Client.location.cast(Geography),
            point,
            radius_meters
        )
    ).all()
    
    return clients


# ===== ROUTES =====

@app.post("/routes/", response_model=RouteResponse)
def create_route(route: RouteCreate, db: Session = Depends(get_db)):
    db_route = Route(**route.dict())
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route


@app.get("/routes/", response_model=List[RouteResponse])
def get_routes(
    seller_id: Optional[int] = None,
    status: Optional[str] = None,
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Route)
    
    if seller_id:
        query = query.filter(Route.seller_id == seller_id)
    if status:
        query = query.filter(Route.status == status)
    if date:
        query = query.filter(Route.scheduled_date >= date)
    
    return query.all()


@app.put("/routes/{route_id}/status")
def update_route_status(route_id: int, status: str, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    route.status = status
    db.commit()
    return {"message": "Status updated", "route_id": route_id, "status": status}


# ===== VISITS (CHECK-IN/CHECK-OUT) =====

@app.post("/visits/checkin/", response_model=VisitResponse)
def check_in(checkin: CheckInCreate, db: Session = Depends(get_db)):
    from geoalchemy2.functions import ST_Distance
    from geoalchemy2 import Geography
    
    # Verificar que la ruta existe
    route = db.query(Route).filter(Route.id == checkin.route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Obtener cliente para calcular distancia
    client = db.query(Client).filter(Client.id == route.client_id).first()
    
    # Crear punto de check-in
    checkin_point = f'POINT({checkin.longitude} {checkin.latitude})'
    
    # Calcular distancia al cliente (en metros)
    distance = None
    if client and client.location:
        distance_query = db.query(
            ST_Distance(
                client.location.cast(Geography),
                checkin_point
            )
        ).scalar()
        distance = float(distance_query) if distance_query else None
    
    # Crear visita
    db_visit = Visit(
        route_id=checkin.route_id,
        seller_id=route.seller_id,
        client_id=route.client_id,
        check_in_time=datetime.utcnow(),
        check_in_location=checkin_point,
        notes=checkin.notes,
        distance_to_client=distance
    )
    
    db.add(db_visit)
    
    # Actualizar estado de la ruta
    route.status = "in_progress"
    
    db.commit()
    db.refresh(db_visit)
    
    response = VisitResponse.from_orm(db_visit)
    response.check_in_lat = checkin.latitude
    response.check_in_lng = checkin.longitude
    
    return response


@app.put("/visits/checkout/", response_model=VisitResponse)
def check_out(checkout: CheckOutCreate, db: Session = Depends(get_db)):
    visit = db.query(Visit).filter(Visit.id == checkout.visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    
    if visit.check_out_time:
        raise HTTPException(status_code=400, detail="Already checked out")
    
    # Actualizar check-out
    visit.check_out_time = datetime.utcnow()
    visit.check_out_location = f'POINT({checkout.longitude} {checkout.latitude})'
    
    # Actualizar ruta a completada
    route = db.query(Route).filter(Route.id == visit.route_id).first()
    if route:
        route.status = "completed"
    
    db.commit()
    db.refresh(visit)
    
    return visit


@app.get("/visits/", response_model=List[VisitResponse])
def get_visits(
    seller_id: Optional[int] = None,
    client_id: Optional[int] = None,
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Visit)
    
    if seller_id:
        query = query.filter(Visit.seller_id == seller_id)
    if client_id:
        query = query.filter(Visit.client_id == client_id)
    if date:
        query = query.filter(Visit.check_in_time >= date)
    
    return query.all()


# ===== OPPORTUNITIES =====

@app.post("/opportunities/", response_model=OpportunityResponse)
def create_opportunity(opportunity: OpportunityCreate, db: Session = Depends(get_db)):
    db_opportunity = Opportunity(**opportunity.dict())
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity


@app.get("/opportunities/", response_model=List[OpportunityResponse])
def get_opportunities(
    seller_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Opportunity)
    
    if seller_id:
        query = query.filter(Opportunity.seller_id == seller_id)
    if status:
        query = query.filter(Opportunity.status == status)
    
    return query.all()


# ===== DASHBOARD =====

@app.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func
    from datetime import date
    
    active_sellers = db.query(func.count(Seller.id)).filter(Seller.active == 1).scalar()
    
    today = date.today()
    total_visits_today = db.query(func.count(Visit.id)).filter(
        func.date(Visit.check_in_time) == today
    ).scalar()
    
    pending_routes = db.query(func.count(Route.id)).filter(Route.status == "pending").scalar()
    
    open_opportunities = db.query(func.count(Opportunity.id)).filter(
        Opportunity.status == "open"
    ).scalar()
    
    return DashboardStats(
        active_sellers=active_sellers or 0,
        total_visits_today=total_visits_today or 0,
        pending_routes=pending_routes or 0,
        open_opportunities=open_opportunities or 0
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)