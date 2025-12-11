# ==============================================================================
# CONFIG.PY - Configuración centralizada
# ==============================================================================
# Salesmen Tracker - Alugandia
# Refactorizado: Diciembre 2025
# ==============================================================================

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    Las variables se cargan desde .env o variables de entorno.
    """
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/salesmen_tracker"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,https://tracker.alugandia.com"
    
    # App
    APP_NAME: str = "Salesmen Tracker - Alugandia"
    DEBUG: bool = False
    
    # GPS Validation
    GPS_MAX_DISTANCE_METERS: int = 100  # Distancia máxima para check-in válido
    GPS_BUSINESS_HOUR_START: int = 7   # Hora inicio jornada
    GPS_BUSINESS_HOUR_END: int = 19     # Hora fin jornada
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = 25
    MAX_PAGE_SIZE: int = 500
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Singleton para settings.
    Usa @lru_cache para evitar leer .env en cada request.
    """
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
