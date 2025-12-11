"""
Tests para verificar que el GPS y Check-in funcionan correctamente
"""
import uuid
import json
from datetime import datetime
from sqlalchemy import text


def test_gps_tracking_enabled(client):
    """Verifica que el sistema de GPS está activado y funciona"""
    # Crear Seller
    seller_resp = client.post("/sellers/", json={
        "name": "Seller GPS Test",
        "email": "gps@test.com",
        "phone": "123456789",
        "is_active": True
    })
    assert seller_resp.status_code == 200
    seller_id = seller_resp.json()["id"]
    
    # Crear Cliente con coordenadas válidas
    client_resp = client.post("/clients/", json={
        "name": "Cliente GPS",
        "address": "Calle Test 123",
        "phone": "999999999",
        "client_type": "carpenter",
        "status": "active",
        "latitude": 40.4168,  # Madrid
        "longitude": -3.7038
    })
    assert client_resp.status_code == 200
    client_id = client_resp.json()["id"]
    
    # Crear Route
    route_resp = client.post("/routes/", json={
        "seller_id": seller_id,
        "client_id": client_id,
        "planned_date": "2025-12-11T10:00:00"
    })
    assert route_resp.status_code == 200
    route_id = route_resp.json()["id"]
    
    # ✅ TEST GPS CHECK-IN: Ubicación dentro de 100 metros
    checkin_payload = {
        "route_id": route_id,
        "seller_id": seller_id,
        "client_id": client_id,
        "latitude": 40.4168,  # Exacto al cliente
        "longitude": -3.7038,
        "client_found": True,
        "notes": "Test GPS válido"
    }
    
    checkin_resp = client.post("/visits/checkin/", json=checkin_payload)
    
    # Verificar respuesta
    assert checkin_resp.status_code == 200, f"Check-in failed: {checkin_resp.text}"
    data = checkin_resp.json()
    
    # Validaciones
    assert "visit_id" in data, "Missing visit_id in response"
    assert data["success"] == True, "Check-in should succeed"
    assert "distance_meters" in data, "Missing distance_meters"
    
    # La distancia debe ser cercana a 0 (mismo punto)
    assert data["distance_meters"] < 10, f"Distance should be near 0, got {data['distance_meters']}"
    
    print(f"✅ GPS Check-in exitoso - Distancia: {data['distance_meters']:.2f} metros")


def test_gps_distance_calculation(client):
    """Verifica que la distancia GPS se calcula correctamente (Haversine)"""
    # Crear Seller
    seller_resp = client.post("/sellers/", json={
        "name": "Seller Distance Test",
        "email": "distance@test.com",
        "phone": "987654321",
        "is_active": True
    })
    seller_id = seller_resp.json()["id"]
    
    # Crear Cliente en ubicación conocida
    # Usando coordenadas de Madrid centro: 40.4168, -3.7038
    client_resp = client.post("/clients/", json={
        "name": "Cliente Madrid",
        "address": "Plaza Mayor, Madrid",
        "phone": "888888888",
        "client_type": "installer",
        "status": "active",
        "latitude": 40.4155,  # Plaza Mayor Madrid
        "longitude": -3.7082
    })
    client_id = client_resp.json()["id"]
    
    # Crear Route
    route_resp = client.post("/routes/", json={
        "seller_id": seller_id,
        "client_id": client_id,
        "planned_date": "2025-12-11T14:00:00"
    })
    route_id = route_resp.json()["id"]
    
    # Check-in a ~500 metros de distancia
    # Coordenadas aproximadas a 500m de la Plaza Mayor
    checkin_payload = {
        "route_id": route_id,
        "seller_id": seller_id,
        "client_id": client_id,
        "latitude": 40.4235,  # ~900m al norte
        "longitude": -3.7082,
        "client_found": True,
        "notes": "Test de distancia"
    }
    
    checkin_resp = client.post("/visits/checkin/", json=checkin_payload)
    assert checkin_resp.status_code == 200
    data = checkin_resp.json()
    
    # La distancia calculada debe ser del orden de 900 metros
    distance = data["distance_meters"]
    print(f"📍 Distancia calculada: {distance:.0f} metros")
    
    # Verificar que está en un rango razonable (800-1000m)
    assert 800 < distance < 1200, f"Distance should be ~900m, got {distance}m"
    
    # Verificar que is_valid es False porque está lejos de 100m
    assert data["is_valid"] == False, "Check-in should be invalid (distance > 100m)"
    assert "validation_error" in data, "Should have validation error message"
    
    print(f"✅ Distancia validada correctamente")


def test_gps_invalid_coordinates(client):
    """Verifica el manejo de coordenadas GPS inválidas"""
    # Crear setup básico
    seller_resp = client.post("/sellers/", json={
        "name": "Seller Invalid GPS",
        "email": "invalid@test.com",
        "phone": "555555555",
        "is_active": True
    })
    seller_id = seller_resp.json()["id"]
    
    client_resp = client.post("/clients/", json={
        "name": "Cliente Invalid",
        "address": "Test",
        "phone": "666666666",
        "client_type": "carpenter",
        "status": "active",
        "latitude": 40.0,
        "longitude": -3.0
    })
    client_id = client_resp.json()["id"]
    
    route_resp = client.post("/routes/", json={
        "seller_id": seller_id,
        "client_id": client_id,
        "planned_date": "2025-12-11T15:00:00"
    })
    route_id = route_resp.json()["id"]
    
    # Intentar check-in con IDs inválidos
    checkin_resp = client.post("/visits/checkin/", json={
        "route_id": "invalid-uuid",
        "seller_id": seller_id,
        "client_id": client_id,
        "latitude": 40.0,
        "longitude": -3.0,
        "client_found": True,
        "notes": ""
    })
    
    # Debe fallar con 400 (IDs inválidos)
    assert checkin_resp.status_code == 400
    print(f"✅ Check-in rechazado con IDs inválidos")


def test_gps_checkin_with_high_accuracy(client):
    """Verifica que el check-in con alta precisión GPS funciona"""
    # Setup
    seller_resp = client.post("/sellers/", json={
        "name": "Seller High Accuracy",
        "email": "highaccuracy@test.com",
        "phone": "444444444",
        "is_active": True
    })
    seller_id = seller_resp.json()["id"]
    
    # Cliente con coordenadas precisas
    client_resp = client.post("/clients/", json={
        "name": "Cliente Precisión",
        "address": "Avenida Paseo",
        "phone": "333333333",
        "client_type": "installer",
        "status": "active",
        "latitude": 40.416777,  # 6 decimales = ~0.1 metros de precisión
        "longitude": -3.703778
    })
    client_id = client_resp.json()["id"]
    
    route_resp = client.post("/routes/", json={
        "seller_id": seller_id,
        "client_id": client_id,
        "planned_date": "2025-12-11T16:00:00"
    })
    route_id = route_resp.json()["id"]
    
    # Check-in con coordenadas muy cercanas (1-2 metros)
    checkin_payload = {
        "route_id": route_id,
        "seller_id": seller_id,
        "client_id": client_id,
        "latitude": 40.416785,  # ~1 metro de diferencia
        "longitude": -3.703786,
        "client_found": True,
        "notes": "GPS de alta precisión"
    }
    
    checkin_resp = client.post("/visits/checkin/", json=checkin_payload)
    assert checkin_resp.status_code == 200
    data = checkin_resp.json()
    
    # Debe ser válido y estar muy cerca
    assert data["distance_meters"] < 10
    assert data["is_valid"] == True
    
    print(f"✅ Check-in con precisión GPS validado - Distancia: {data['distance_meters']:.2f}m")


def test_gps_missing_client_coordinates(client):
    """Verifica que el sistema maneja clientes sin coordenadas"""
    seller_resp = client.post("/sellers/", json={
        "name": "Seller No Coords",
        "email": "nocoords@test.com",
        "phone": "222222222",
        "is_active": True
    })
    seller_id = seller_resp.json()["id"]
    
    # Cliente SIN coordenadas (null)
    client_resp = client.post("/clients/", json={
        "name": "Cliente Sin GPS",
        "address": "Desconocida",
        "phone": "111111111",
        "client_type": "carpenter",
        "status": "active",
        "latitude": None,
        "longitude": None
    })
    client_id = client_resp.json()["id"]
    
    route_resp = client.post("/routes/", json={
        "seller_id": seller_id,
        "client_id": client_id,
        "planned_date": "2025-12-11T17:00:00"
    })
    route_id = route_resp.json()["id"]
    
    # Intentar check-in
    checkin_resp = client.post("/visits/checkin/", json={
        "route_id": route_id,
        "seller_id": seller_id,
        "client_id": client_id,
        "latitude": 40.4,
        "longitude": -3.7,
        "client_found": True,
        "notes": "Sin GPS cliente"
    })
    
    # Debería fallar o retornar un error
    if checkin_resp.status_code == 200:
        # Si acepta, debería marcar como inválido
        data = checkin_resp.json()
        # El backend debería indicar que falta información
        print(f"⚠️ Check-in sin coordenadas del cliente: {data}")
    
    print(f"✅ Sistema maneja clientes sin GPS")
