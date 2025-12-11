# ==============================================================================
# UTILS: GEO - Funciones geoespaciales
# ==============================================================================

from math import radians, sin, cos, sqrt, atan2
from typing import Tuple, Optional


def calculate_distance(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float
) -> float:
    """
    Calcula la distancia entre dos puntos usando la fórmula de Haversine.
    
    Args:
        lat1, lon1: Coordenadas del punto 1
        lat2, lon2: Coordenadas del punto 2
    
    Returns:
        Distancia en metros
    """
    R = 6371000  # Radio de la Tierra en metros
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def validate_coordinates(lat: float, lon: float) -> Tuple[bool, str]:
    """
    Valida que las coordenadas sean válidas.
    
    Args:
        lat: Latitud
        lon: Longitud
    
    Returns:
        Tuple (is_valid, message)
    """
    if lat == 0 and lon == 0:
        return False, "Coordenadas en (0,0) - posible error de GPS"
    
    if not (-90 <= lat <= 90):
        return False, f"Latitud fuera de rango: {lat}"
    
    if not (-180 <= lon <= 180):
        return False, f"Longitud fuera de rango: {lon}"
    
    # Verificar que está en la zona de Valencia (aproximado)
    # Lat: 38.5 - 40.5, Lon: -1.5 - 0.5
    if not (38.0 <= lat <= 41.0):
        return False, "Latitud fuera de la zona de cobertura (España)"
    
    if not (-2.0 <= lon <= 1.0):
        return False, "Longitud fuera de la zona de cobertura (España)"
    
    return True, "Coordenadas válidas"


def get_bounding_box(
    lat: float, 
    lon: float, 
    radius_km: float
) -> Tuple[float, float, float, float]:
    """
    Calcula un bounding box alrededor de un punto.
    
    Args:
        lat, lon: Centro del bounding box
        radius_km: Radio en kilómetros
    
    Returns:
        Tuple (min_lat, min_lon, max_lat, max_lon)
    """
    # Aproximación: 1 grado de latitud ≈ 111 km
    # 1 grado de longitud ≈ 111 * cos(lat) km
    
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * cos(radians(lat)))
    
    return (
        lat - lat_delta,  # min_lat
        lon - lon_delta,  # min_lon
        lat + lat_delta,  # max_lat
        lon + lon_delta   # max_lon
    )


def format_distance(meters: float) -> str:
    """
    Formatea una distancia para mostrar al usuario.
    
    Args:
        meters: Distancia en metros
    
    Returns:
        String formateado ("150 m", "2.3 km", etc.)
    """
    if meters < 1000:
        return f"{meters:.0f} m"
    else:
        return f"{meters/1000:.1f} km"
