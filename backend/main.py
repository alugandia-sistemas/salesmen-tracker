# ==============================================================================
# MAIN.PY - Punto de entrada de la aplicación
# ==============================================================================
# Salesmen Tracker - Alugandia
# 
# Backend refactorizado en módulos:
# - config.py: Configuración centralizada
# - database.py: Conexión a PostgreSQL/PostGIS
# - models/: Modelos SQLAlchemy
# - schemas/: Schemas Pydantic
# - routers/: Endpoints FastAPI
# - utils/: Utilidades (geo, validators)
# ==============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Imports ABSOLUTOS (sin punto)
from config import settings, get_cors_origins
from database import init_db
from routers import (
    clients_router,
    sellers_router,
    routes_router,
    visits_router,
    zones_router,
    opportunities_router,
    auth_router
)


# ==============================================================================
# CREAR APLICACIÓN
# ==============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema de tracking de vendedores con validación GPS",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ==============================================================================
# CORS MIDDLEWARE
# ==============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# REGISTRAR ROUTERS
# ==============================================================================

app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(sellers_router)
app.include_router(routes_router)
app.include_router(visits_router)
app.include_router(zones_router)
app.include_router(opportunities_router)


# ==============================================================================
# EVENTOS DE CICLO DE VIDA
# ==============================================================================

@app.on_event("startup")
async def startup_event():
    """Inicializar base de datos al arrancar"""
    print("🚀 Iniciando Salesmen Tracker...")
    init_db()
    print(f"✅ API disponible en {settings.APP_NAME}")
    print(f"📊 Docs: /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar"""
    print("👋 Cerrando Salesmen Tracker...")


# ==============================================================================
# ENDPOINTS BÁSICOS
# ==============================================================================

@app.get("/")
def root():
    """Health check y bienvenida"""
    return {
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check para monitoreo"""
    return {"status": "healthy"}


# ==============================================================================
# EJECUTAR (desarrollo local)
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
