"""Smoke tests for optimize-order, tracking, and SMTP helpers (no SMTP in tests)."""

import datetime as dt
import uuid


def test_optimize_order_invalid_seller(client):
    r = client.post(
        "/routes/optimize-order/",
        json={"seller_id": "x", "planned_date": "2026-06-01"},
    )
    assert r.status_code == 400


def test_optimize_order_invalid_date(client):
    r = client.post(
        "/routes/optimize-order/",
        json={"seller_id": str(uuid.uuid4()), "planned_date": "not-a-date"},
    )
    assert r.status_code == 400


def test_tracking_today_ok_shape(client):
    sid = str(uuid.uuid4())
    r = client.get(f"/sellers/{sid}/tracking/today")
    assert r.status_code == 200
    data = r.json()
    assert "distance_remaining_km" in data
    assert "eta_minutes" in data
    assert "next_stop_time" in data


def test_reports_still_works(client):
    r = client.get(
        "/reports/seller-performance/",
        params={
            "date_from": dt.date(2020, 1, 1).isoformat(),
            "date_to": dt.date(2030, 1, 1).isoformat(),
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "period" in body and "sellers" in body
