from datetime import datetime, timedelta
import pytest
from starlette.testclient import TestClient
from sqlalchemy import select

from src.main import app
from src.core.database import SessionLocal
from src.models.accounts.user import User
from src.models.provider.category import Category
from src.models.provider.coach_profile import CoachProfile
from src.models.provider.service.coach_service import CoachService
from src.models.client.order import Order
from src.models.client.service_booking import ServiceBooking
from src.utils.jwt import create_access_token


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def setup_booking_data(db_session):
    # 1. Coach
    coach = db_session.execute(
        select(User).where(User.email == "booking_coach@test.com")
    ).scalar_one_or_none()
    if not coach:
        coach = User(
            full_name="Booking Coach",
            email="booking_coach@test.com",
            password_hash="hashed_pw",
            phone="+111222333",
            role="COACH",
            coach_status="approved",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(coach)
        db_session.commit()
        db_session.refresh(coach)

    profile = db_session.execute(
        select(CoachProfile).where(CoachProfile.user_id == coach.id)
    ).scalar_one_or_none()
    if not profile:
        profile = CoachProfile(
            user_id=coach.id,
            headline="Expert Coach",
            about="Coach description",
            status="approved",
            is_completed=True,
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)

    category = db_session.execute(
        select(Category).where(Category.name == "BookingCat")
    ).scalar_one_or_none()
    if not category:
        category = Category(name="BookingCat", description="Test Category", is_active=True)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

    service = db_session.execute(
        select(CoachService).where(CoachService.title == "Test 1-on-1 Session")
    ).scalar_one_or_none()
    if not service:
        service = CoachService(
            coach_profile_id=profile.id,
            category_id=category.id,
            title="Test 1-on-1 Session",
            description="Deep dive session",
            price="100.00",
            session_duration=60,
            session_format="video",
            service_type="one_time",
            status="published",
        )
        db_session.add(service)
        db_session.commit()
        db_session.refresh(service)

    # 2. Client User
    client_user = db_session.execute(
        select(User).where(User.email == "booking_client@test.com")
    ).scalar_one_or_none()
    if not client_user:
        client_user = User(
            full_name="Booking Client",
            email="booking_client@test.com",
            password_hash="hashed_pw",
            phone="+444555666",
            role="USER",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(client_user)
        db_session.commit()
        db_session.refresh(client_user)

    # 3. Other Client User
    other_user = db_session.execute(
        select(User).where(User.email == "other_booking_client@test.com")
    ).scalar_one_or_none()
    if not other_user:
        other_user = User(
            full_name="Other Client",
            email="other_booking_client@test.com",
            password_hash="hashed_pw",
            phone="+777888999",
            role="USER",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

    token, _ = create_access_token(
        user_id=client_user.id,
        role=client_user.role,
        full_name=client_user.full_name,
    )
    headers = {"Authorization": f"Bearer {token}"}

    return {
        "coach": coach,
        "profile": profile,
        "service": service,
        "client": client_user,
        "other_user": other_user,
        "headers": headers,
    }


def _cleanup_orders(db_session, user_ids: list[int]):
    orders = db_session.query(Order).filter(Order.user_id.in_(user_ids)).all()
    order_ids = [o.id for o in orders]
    if order_ids:
        db_session.query(ServiceBooking).filter(ServiceBooking.order_id.in_(order_ids)).delete(synchronize_session=False)
        db_session.query(Order).filter(Order.id.in_(order_ids)).delete(synchronize_session=False)
        db_session.commit()


def test_user_booking_list_only_returns_paid_bookings(client, db_session, setup_booking_data):
    setup = setup_booking_data
    client_user = setup["client"]
    other_user = setup["other_user"]
    coach = setup["coach"]
    profile = setup["profile"]
    service = setup["service"]

    _cleanup_orders(db_session, [client_user.id, other_user.id])

    # 1. Paid confirmed service booking (MUST be returned)
    paid_order = Order(
        user_id=client_user.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        service_id=service.id,
        booking_date="2026-12-01",
        booking_time="10:00:00",
        order_type="service",
        amount="100.00",
        currency="USD",
        status="confirmed",
        payment_status="paid",
        payment_method="stripe",
    )
    db_session.add(paid_order)

    # 2. Unpaid pending service order (MUST NOT be returned)
    unpaid_order = Order(
        user_id=client_user.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        service_id=service.id,
        booking_date="2026-12-02",
        booking_time="11:00:00",
        order_type="service",
        amount="100.00",
        currency="USD",
        status="pending",
        payment_status="pending",
        payment_method="stripe",
    )
    db_session.add(unpaid_order)

    # 3. Failed payment service order (MUST NOT be returned)
    failed_order = Order(
        user_id=client_user.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        service_id=service.id,
        booking_date="2026-12-03",
        booking_time="12:00:00",
        order_type="service",
        amount="100.00",
        currency="USD",
        status="failed",
        payment_status="failed",
    )
    db_session.add(failed_order)

    # 4. Paid product order (MUST NOT be returned in service booking list)
    product_order = Order(
        user_id=client_user.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        order_type="product",
        amount="30.00",
        currency="USD",
        status="completed",
        payment_status="paid",
    )
    db_session.add(product_order)

    # 5. Paid service order for a DIFFERENT user (MUST NOT be returned)
    other_order = Order(
        user_id=other_user.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        service_id=service.id,
        booking_date="2026-12-04",
        booking_time="14:00:00",
        order_type="service",
        amount="100.00",
        currency="USD",
        status="confirmed",
        payment_status="paid",
    )
    db_session.add(other_order)
    db_session.commit()

    # Call GET /api/user/user-booking-list
    res = client.get("/api/user/user-booking-list", headers=setup["headers"])
    assert res.status_code == 200
    data = res.json()["data"]

    # Only paid_order should be in the list
    assert len(data) == 1
    item = data[0]
    assert item["id"] == paid_order.id
    assert item["payment_status"] == "paid"
    assert item["status"] == "confirmed"
    assert item["service_id"] == service.id
    assert item["can_join"] is True


def test_user_booking_list_status_filters(client, db_session, setup_booking_data):
    setup = setup_booking_data
    client_user = setup["client"]
    coach = setup["coach"]
    profile = setup["profile"]
    service = setup["service"]

    _cleanup_orders(db_session, [client_user.id])

    # Paid confirmed order (upcoming)
    confirmed_order = Order(
        user_id=client_user.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        service_id=service.id,
        booking_date="2026-12-10",
        booking_time="10:00:00",
        order_type="service",
        amount="100.00",
        currency="USD",
        status="confirmed",
        payment_status="paid",
    )
    db_session.add(confirmed_order)

    # Paid completed order
    completed_order = Order(
        user_id=client_user.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        service_id=service.id,
        booking_date="2026-10-01",
        booking_time="10:00:00",
        order_type="service",
        amount="100.00",
        currency="USD",
        status="completed",
        payment_status="paid",
    )
    db_session.add(completed_order)

    # Paid cancelled order
    cancelled_order = Order(
        user_id=client_user.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        service_id=service.id,
        booking_date="2026-10-05",
        booking_time="10:00:00",
        order_type="service",
        amount="100.00",
        currency="USD",
        status="cancelled",
        payment_status="paid",
    )
    db_session.add(cancelled_order)
    db_session.commit()

    # 1. status=upcoming returns confirmed order
    res_upcoming = client.get("/api/user/user-booking-list?status=upcoming", headers=setup["headers"])
    assert res_upcoming.status_code == 200
    upcoming_data = res_upcoming.json()["data"]
    assert len(upcoming_data) == 1
    assert upcoming_data[0]["id"] == confirmed_order.id

    # 2. status=confirmed returns confirmed order (same thing)
    res_confirmed = client.get("/api/user/user-booking-list?status=confirmed", headers=setup["headers"])
    assert res_confirmed.status_code == 200
    confirmed_data = res_confirmed.json()["data"]
    assert len(confirmed_data) == 1
    assert confirmed_data[0]["id"] == confirmed_order.id

    # 3. status=completed returns completed order
    res_completed = client.get("/api/user/user-booking-list?status=completed", headers=setup["headers"])
    assert res_completed.status_code == 200
    completed_data = res_completed.json()["data"]
    assert len(completed_data) == 1
    assert completed_data[0]["id"] == completed_order.id

    # 4. status=cancelled returns cancelled order
    res_cancelled = client.get("/api/user/user-booking-list?status=cancelled", headers=setup["headers"])
    assert res_cancelled.status_code == 200
    cancelled_data = res_cancelled.json()["data"]
    assert len(cancelled_data) == 1
    assert cancelled_data[0]["id"] == cancelled_order.id

    # 5. status=upcoming,completed returns both
    res_multi = client.get("/api/user/user-booking-list?status=upcoming,completed", headers=setup["headers"])
    assert res_multi.status_code == 200
    multi_data = res_multi.json()["data"]
    assert len(multi_data) == 2
    multi_ids = {item["id"] for item in multi_data}
    assert multi_ids == {confirmed_order.id, completed_order.id}

    # 6. Invalid status filter returns 400
    res_invalid = client.get("/api/user/user-booking-list?status=invalid_status", headers=setup["headers"])
    assert res_invalid.status_code == 400
    assert "INVALID_STATUS_FILTER" in res_invalid.json()["error"]


def test_user_booking_detail(client, db_session, setup_booking_data):
    setup = setup_booking_data
    client_user = setup["client"]
    other_user = setup["other_user"]
    coach = setup["coach"]
    profile = setup["profile"]
    service = setup["service"]

    _cleanup_orders(db_session, [client_user.id, other_user.id])

    # Paid confirmed order
    paid_order = Order(
        user_id=client_user.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        service_id=service.id,
        booking_date="2026-12-15",
        booking_time="15:00:00",
        order_type="service",
        amount="100.00",
        currency="USD",
        status="confirmed",
        payment_status="paid",
    )
    db_session.add(paid_order)

    # Unpaid order
    unpaid_order = Order(
        user_id=client_user.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        service_id=service.id,
        booking_date="2026-12-16",
        booking_time="16:00:00",
        order_type="service",
        amount="100.00",
        currency="USD",
        status="pending",
        payment_status="pending",
    )
    db_session.add(unpaid_order)

    # Other user's paid order
    other_order = Order(
        user_id=other_user.id,
        coach_id=coach.id,
        coach_profile_id=profile.id,
        service_id=service.id,
        booking_date="2026-12-17",
        booking_time="17:00:00",
        order_type="service",
        amount="100.00",
        currency="USD",
        status="confirmed",
        payment_status="paid",
    )
    db_session.add(other_order)
    db_session.commit()

    # 1. Successful detail fetch for paid order
    res = client.get(f"/api/user/user-booking-detail/{paid_order.id}", headers=setup["headers"])
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["id"] == paid_order.id
    assert data["payment_status"] == "paid"
    assert data["status"] == "confirmed"
    assert data["service_title"] == "Test 1-on-1 Session"
    assert data["can_join"] is True

    # 2. 404 for unpaid order (not a valid booking)
    res_unpaid = client.get(f"/api/user/user-booking-detail/{unpaid_order.id}", headers=setup["headers"])
    assert res_unpaid.status_code == 404
    assert res_unpaid.json()["error"] == "BOOKING_NOT_FOUND"

    # 3. 404 for other user's order
    res_other = client.get(f"/api/user/user-booking-detail/{other_order.id}", headers=setup["headers"])
    assert res_other.status_code == 404
    assert res_other.json()["error"] == "BOOKING_NOT_FOUND"

    # 4. 404 for non-existent order
    res_none = client.get("/api/user/user-booking-detail/999999", headers=setup["headers"])
    assert res_none.status_code == 404
    assert res_none.json()["error"] == "BOOKING_NOT_FOUND"
