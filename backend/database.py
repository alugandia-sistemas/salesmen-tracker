# ==============================================================================
# DATABASE.PY - Conexión y sesiones de base de datos
# ==============================================================================
# Salesmen Tracker - Alugandia
# ==============================================================================

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Import ABSOLUTO
from config import settings

# ==============================================================================
# ENGINE CONFIGURATION
# ==============================================================================

# Configuración optimizada para producción
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,           # Conexiones permanentes
    max_overflow=10,       # Conexiones adicionales bajo carga
    pool_timeout=30,       # Timeout para obtener conexión
    pool_recycle=1800,     # Reciclar conexiones cada 30 min
    pool_pre_ping=True,    # Verificar conexión antes de usar
    echo=settings.DEBUG    # Log SQL solo en debug
)

# ==============================================================================
# SESSION FACTORY
# ==============================================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ==============================================================================
# BASE MODEL
# ==============================================================================

Base = declarative_base()

# ==============================================================================
# DEPENDENCY INJECTION
# ==============================================================================

def get_db():
    """
    Dependency para obtener sesión de DB.
    Uso: db: Session = Depends(get_db)
    
    Maneja automáticamente el ciclo de vida de la sesión.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================================================================
# POSTGIS SETUP
# ==============================================================================

def ensure_postgis():
    """
    Asegura que la extensión PostGIS esté instalada.
    Se ejecuta al iniciar la aplicación.
    """
    try:
        with engine.connect() as connection:
            # Verificar si PostGIS ya está instalado
            result = connection.execute(
                text("SELECT 1 FROM pg_extension WHERE extname = 'postgis'")
            )
            if result.fetchone():
                print("✅ PostGIS ya está instalado")
                return True
            
            # Intentar instalar
            try:
                connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                connection.commit()
                print("✅ PostGIS instalado correctamente")
                return True
            except Exception as e1:
                # Si falla por permisos, intentar con superusuario
                if "permission denied" in str(e1).lower():
                    print(f"⚠️ Intento 1 falló: {str(e1)}")
                    print("🔧 Intentando instalación alternativa de PostGIS...")
                    try:
                        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                        connection.commit()
                        print("✅ PostGIS instalado en segundo intento")
                        return True
                    except Exception as e2:
                        print(f"⚠️ PostGIS no disponible: {str(e2)}")
                        return False
                raise e1
                
    except Exception as e:
        print(f"⚠️ Error en PostGIS: {str(e)}")
        print("ℹ️ La aplicación continuará sin soporte geoespacial completo")
        return False


def init_db():
    """
    Inicializa la base de datos.
    - Crea extensión PostGIS
    - Crea todas las tablas
    """
    # Importar modelos para que SQLAlchemy los conozca
    from models import Client, Seller, Route, Visit, Zone, Opportunity
    
    ensure_postgis()
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada")
