import datetime

def test_create_sales_route(client):
    # Create Zone first
    z_resp = client.post("/zones/", json={"name": "Zone Test"})
    zone_id = z_resp.json()["id"] if z_resp.status_code == 200 else None
    
    # Create Seller
    s_resp = client.post("/sellers/", json={"name": "Seller Test", "email": "test@example.com", "phone": "123", "is_active": True})
    seller_id = s_resp.json()["id"] if s_resp.status_code == 200 else None

    response = client.post("/sales-routes/", json={
        "name": "Route 101",
        "zone_id": zone_id,
        "seller_id": seller_id
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Route 101"
    assert data["seller_id"] == seller_id

def test_assign_client_to_route_and_view(client):
    # Setup: Seller, Route, Client
    s_resp = client.post("/sellers/", json={"name": "Seller View", "email": "view@example.com", "phone": "123", "is_active": True})
    seller_id = s_resp.json()["id"]
    
    r_resp = client.post("/sales-routes/", json={"name": "Route View", "seller_id": seller_id})
    route_id = r_resp.json()["id"]
    
    c_resp = client.post("/clients/", json={
        "name": "Client Assigned", 
        "address": "Addr", 
        "phone": "999", 
        "client_type": "type", 
        "status":"active",
        "latitude": 0.0,
        "longitude": 0.0
    })
    client_id = c_resp.json()["id"]
    
    # Assign
    assign_resp = client.put(f"/clients/{client_id}/assign-route/", json={"sales_route_id": route_id})
    assert assign_resp.status_code == 200
    
    # Verify View "My Route Customers"
    view_resp = client.get(f"/my-route-customers/?seller_id={seller_id}")
    assert view_resp.status_code == 200
    customers = view_resp.json()
    assert len(customers) >= 1
    assert any(c["id"] == client_id for c in customers)
