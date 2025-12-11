# ==============================================================================
# CONFIG.PY - Configuración centralizada
# ==============================================================================

import os
from functools import lru_cache
from typing import List


class Settings:
    """Configuración de la aplicación"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/salesmen_tracker"
    )
    
    # CORS
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:5173,https://tracker.alugandia.com"
    )
    
    # App
    APP_NAME: str = "Salesmen Tracker - Alugandia"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # GPS Validation
    GPS_MAX_DISTANCE_METERS: int = int(os.getenv("GPS_MAX_DISTANCE_METERS", "100"))
    GPS_BUSINESS_HOUR_START: int = int(os.getenv("GPS_BUSINESS_HOUR_START", "7"))
    GPS_BUSINESS_HOUR_END: int = int(os.getenv("GPS_BUSINESS_HOUR_END", "21"))
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 25
    MAX_PAGE_SIZE: int = 500


@lru_cache()
def get_settings() -> Settings:
    """Singleton para settings"""
    return Settings()


# Alias para acceso rápido
settings = get_settings()


def get_cors_origins() -> List[str]:
    """Parsea CORS_ORIGINS string a lista"""
    origins = settings.CORS_ORIGINS.split(",")
    # Asegurar que tracker.alugandia.com siempre esté incluido
    if "https://tracker.alugandia.com" not in origins:
        origins.append("https://tracker.alugandia.com")
    return list(set(origins))  # Eliminar duplicados
