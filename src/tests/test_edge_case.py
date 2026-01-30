from datetime import datetime, timedelta, timezone

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.tests.test_happy_path import cleanup_event


# Sold Out
@pytest.mark.asyncio
async def test_sold_out():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:
            admin_login = await client.post(
                "/auth/login",
                data={
                    "username": "admin@test.com",
                    "password": "admin"
                }
            )

            assert admin_login.status_code == 200
            admin_token = admin_login.json()["access_token"]

            create_event = await client.post(
                "/events",
                json={
                    "title": "SOLD OUT EVENT",
                    "total_tickets": 1,
                    "venue": "Prem",
                    "price_in_rupee": 1,
                    "event_date": "2038-01-29T05:12:47.142Z"
                },
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert create_event.status_code == 201
            event_id = create_event.json()["id"]

            user_login = await client.post(
                "/auth/login",
                data={"username": "gurleen.kaur@test.com", "password": "password"},
            )
            user_token = user_login.json()["access_token"]

            book = await client.post(
                f"/bookings/{event_id}/book",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert book.status_code == 201

            user_login = await client.post(
                "/auth/login",
                data={"username": "harpreet.singh@test.com", "password": "password"},
            )
            user_token = user_login.json()["access_token"]

            book = await client.post(
                f"/bookings/{event_id}/book",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert book.status_code == 409

            await cleanup_event(event_id)

# Double Booking
@pytest.mark.asyncio
async def test_double_booking_same_user():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:
            admin_login = await client.post(
                "/auth/login",
                data={
                    "username": "admin@test.com",
                    "password": "admin"
                }
            )

            assert admin_login.status_code == 200
            admin_token = admin_login.json()["access_token"]

            create_event = await client.post(
                "/events",
                json={
                    "title": "Double Booking",
                    "total_tickets": 10,
                    "venue": "Prem",
                    "price_in_rupee": 1,
                    "event_date": "2038-01-29T05:12:47.142Z"
                },
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert create_event.status_code == 201
            event_id = create_event.json()["id"]


            user_login = await client.post(
                "/auth/login",
                data={"username": "gurleen.kaur@test.com", "password": "password"},
            )
            user_token = user_login.json()["access_token"]

            book = await client.post(
                f"/bookings/{event_id}/book",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert book.status_code == 201

            second_book = await client.post(
                f"/bookings/{event_id}/book",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert second_book.status_code == 409

            await cleanup_event(event_id)

@pytest.mark.asyncio
async def test_late_cancellation_forbidden():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:
            admin_login = await client.post(
                "/auth/login",
                data={
                    "username": "admin@test.com",
                    "password": "admin"
                }
            )

            assert admin_login.status_code == 200
            admin_token = admin_login.json()["access_token"]

            create_event = await client.post(
                "/events",
                json={
                    "title": "Late Cancellation",
                    "total_tickets": 10,
                    "venue": "Prem",
                    "price_in_rupee": 1,
                    "event_date": (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()
                },
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert create_event.status_code == 201
            event_id = create_event.json()["id"]

            user_login = await client.post(
                "/auth/login",
                data={"username": "gurleen.kaur@test.com", "password": "password"},
            )
            user_token = user_login.json()["access_token"]

            book = await client.post(
                f"/bookings/{event_id}/book",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert book.status_code == 201
            booking_id = book.json()["booking_id"]

            delete_booking = await client.delete(
                f"/bookings/{booking_id}",
                headers={"Authorization": f"Bearer {user_token}"},
            )

            assert delete_booking.status_code == 403

            await cleanup_event(event_id)

