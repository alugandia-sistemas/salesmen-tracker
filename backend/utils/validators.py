# ==============================================================================
# UTILS: VALIDATORS - Validaciones de negocio
# ==============================================================================

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

from .geo import calculate_distance, validate_coordinates


@dataclass
class GPSValidationResult:
    """Resultado de validación GPS"""
    is_valid: bool
    distance_meters: float
    fraud_flags: List[str]
    message: str


def validate_gps_checkin(
    seller_lat: float,
    seller_lon: float,
    client_lat: float,
    client_lon: float,
    max_distance_meters: int = 100,
    business_hour_start: int = 7,
    business_hour_end: int = 21,
    accuracy: Optional[float] = None
) -> GPSValidationResult:
    """
    Valida un check-in GPS de vendedor.
    
    Validaciones:
    1. Distancia al cliente <= max_distance_meters
    2. Dentro de horario laboral
    3. Precisión GPS aceptable
    4. Coordenadas no sospechosas
    
    Args:
        seller_lat, seller_lon: Ubicación del vendedor
        client_lat, client_lon: Ubicación del cliente
        max_distance_meters: Distancia máxima permitida
        business_hour_start: Hora inicio jornada (0-23)
        business_hour_end: Hora fin jornada (0-23)
        accuracy: Precisión GPS reportada (metros)
    
    Returns:
        GPSValidationResult
    """
    fraud_flags = []
    
    # Validar coordenadas del vendedor
    coords_valid, coords_msg = validate_coordinates(seller_lat, seller_lon)
    if not coords_valid:
        fraud_flags.append(f"invalid_seller_coords: {coords_msg}")
    
    # Calcular distancia
    distance = calculate_distance(
        seller_lat, seller_lon,
        client_lat, client_lon
    )
    
    # Validar distancia
    is_valid_distance = distance <= max_distance_meters
    
    # Validar horario
    current_hour = datetime.now().hour
    is_valid_hour = business_hour_start <= current_hour <= business_hour_end
    if not is_valid_hour:
        fraud_flags.append("outside_business_hours")
    
    # Validar precisión GPS
    if accuracy is not None:
        if accuracy > 50:
            fraud_flags.append("low_gps_accuracy")
        if accuracy > 100:
            fraud_flags.append("very_low_gps_accuracy")
    
    # Detectar coordenadas sospechosas
    if seller_lat == 0 or seller_lon == 0:
        fraud_flags.append("zero_coordinates")
    
    if seller_lat == client_lat and seller_lon == client_lon:
        fraud_flags.append("exact_match_suspicious")
    
    # Detectar posible mock location (coordenadas muy redondas)
    if seller_lat == round(seller_lat, 2) and seller_lon == round(seller_lon, 2):
        # Solo 2 decimales de precisión es sospechoso
        fraud_flags.append("possibly_mocked_location")
    
    # Determinar validez final
    is_valid = is_valid_distance and is_valid_hour and len(fraud_flags) == 0
    
    # Generar mensaje
    if is_valid:
        message = f"Check-in válido ({distance:.0f}m del cliente)"
    elif not is_valid_distance:
        message = f"Demasiado lejos del cliente: {distance:.0f}m (máx: {max_distance_meters}m)"
    elif not is_valid_hour:
        message = f"Fuera de horario laboral ({business_hour_start}:00 - {business_hour_end}:00)"
    elif fraud_flags:
        message = f"Check-in sospechoso: {', '.join(fraud_flags)}"
    else:
        message = "Check-in inválido"
    
    return GPSValidationResult(
        is_valid=is_valid,
        distance_meters=round(distance, 2),
        fraud_flags=fraud_flags,
        message=message
    )


def validate_quick_note(note: str) -> tuple[bool, str]:
    """
    Valida la nota rápida obligatoria.
    
    Args:
        note: Texto de la nota
    
    Returns:
        Tuple (is_valid, message)
    """
    if not note:
        return False, "La nota rápida es obligatoria"
    
    note = note.strip()
    
    if len(note) < 5:
        return False, "La nota debe tener al menos 5 caracteres"
    
    if len(note) > 100:
        return False, "La nota no puede exceder 100 caracteres"
    
    return True, "Nota válida"
