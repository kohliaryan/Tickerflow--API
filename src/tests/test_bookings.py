import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete

from src.main import app
from src.database.database import AsyncSessionLocal
from src.models import Event, Booking


async def cleanup_event(event_id: int):
    async with AsyncSessionLocal() as db:
        await db.execute(delete(Booking).where(Booking.event_id == event_id))
        await db.execute(delete(Event).where(Event.id == event_id))
        await db.commit()


@pytest.mark.asyncio
async def test_booking():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        # --- Admin login ---
        admin_login = await client.post(
            "/auth/login",
            data={"username": "admin@test.com", "password": "admin"},
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]

        # --- Create event ---
        payload = {
            "title": "Test Event - abc",
            "total_tickets": 10,
            "price_in_rupee": 100,
            "venue": "somewhere",
            "event_date": "2038-01-29T05:12:47.142Z",
        }

        create_event = await client.post(
            "/events",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert create_event.status_code == 201
        event_id = create_event.json()["id"]

        # --- User login ---
        user_login = await client.post(
            "/auth/login",
            data={"username": "gurleen.kaur@test.com", "password": "password"},
        )
        assert user_login.status_code == 200
        user_token = user_login.json()["access_token"]

        # --- Book ticket ---
        book = await client.post(
            f"/bookings/{event_id}/book",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert book.status_code == 201

        # --- Assert ticket reduced ---
        event_response = await client.get(f"/event/{event_id}")
        assert event_response.json()["available_tickets"] == 9

        # --- CLEANUP ---
        await cleanup_event(event_id)
