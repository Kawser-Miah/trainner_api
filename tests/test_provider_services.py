import pytest
from starlette.testclient import TestClient
from sqlalchemy import select

from src.main import app
from src.core.database import SessionLocal
from src.models.accounts.user import User
from src.models.provider.category import Category
from src.models.provider.coach_profile import CoachProfile
from src.models.provider.service.coach_service import CoachService
from src.utils.jwt import create_access_token


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_coach_and_category(db_session):
    # Ensure category exists
    category = db_session.execute(
        select(Category).where(Category.name == "Business")
    ).scalar_one_or_none()
    if not category:
        category = Category(
            name="Business",
            description="Business coaching",
            is_active=True,
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

    # Ensure approved coach exists
    coach = db_session.execute(
        select(User).where(User.email == "service_coach@coachhub.com")
    ).scalar_one_or_none()
    if not coach:
        coach = User(
            full_name="Service Coach",
            email="service_coach@coachhub.com",
            password_hash="test_hashed_password",
            phone="+1234567890",
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
            headline="Expert Service Coach",
            about="Coach profile for testing services",
            status="approved",
            is_completed=True,
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)

    # Ensure another coach for ownership tests
    other_coach = db_session.execute(
        select(User).where(User.email == "other_service_coach@coachhub.com")
    ).scalar_one_or_none()
    if not other_coach:
        other_coach = User(
            full_name="Other Coach",
            email="other_service_coach@coachhub.com",
            password_hash="test_hashed_password",
            phone="+9999999999",
            role="COACH",
            coach_status="approved",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(other_coach)
        db_session.commit()
        db_session.refresh(other_coach)

    other_profile = db_session.execute(
        select(CoachProfile).where(CoachProfile.user_id == other_coach.id)
    ).scalar_one_or_none()
    if not other_profile:
        other_profile = CoachProfile(
            user_id=other_coach.id,
            headline="Other Coach",
            about="Other coach profile",
            status="approved",
            is_completed=True,
        )
        db_session.add(other_profile)
        db_session.commit()
        db_session.refresh(other_profile)

    # Clean existing services for this coach
    existing_services = db_session.execute(
        select(CoachService).where(CoachService.coach_profile_id == profile.id)
    ).scalars().all()
    for s in existing_services:
        db_session.delete(s)
    db_session.commit()

    return coach, profile, category, other_coach, other_profile


def test_create_service_flow(test_coach_and_category, db_session):
    coach, profile, category, _, _ = test_coach_and_category
    client = TestClient(app)
    token, _ = create_access_token(
        user_id=coach.id,
        role=coach.role,
        full_name=coach.full_name,
    )
    headers = {"Authorization": f"Bearer {token}"}

    create_payload = {
        "title": "1:1 Career Session",
        "category": category.id,
        "description": "Plan your next career move.",
        "service_type": "one_time",
        "session_format": "video",
        "session_duration": 60,
        "currency": "USD",
        "price": "120.00",
        "booking_type": "instant",
        "who_is_this_service_for": "Engineers",
        "preparation_instructions": "Bring your CV",
        "cancellation_policy": "standard",
        "session_url": "https://meet.google.com/abc-defg-hij",
        "status": "published",
        "benefits": [
            {"outcome": "A clear career plan"},
            {"outcome": "CV feedback"},
        ],
    }

    # 1. Create service (POST /api/Provider/services/create)
    resp = client.post("/api/Provider/services/create", json=create_payload, headers=headers)
    assert resp.status_code == 201, resp.text
    res_data = resp.json()
    assert res_data["success"] is True
    assert res_data["status"] == 201
    assert res_data["message"] == "Service created successfully."

    data = res_data["data"]
    service_id = data["id"]
    assert data["coach"] == profile.id
    assert data["title"] == "1:1 Career Session"
    assert data["price"] == "120.00"
    assert data["status"] == "published"
    assert len(data["benefits"]) == 2
    assert data["category"]["id"] == category.id
    assert data["category"]["name"] == "Business"
    assert "created_at" in data
    assert "updated_at" in data

    # 2. List services with status filter (GET /api/Provider/services/list?status=published)
    list_resp = client.get("/api/Provider/services/list?status=published", headers=headers)
    assert list_resp.status_code == 200, list_resp.text
    list_data = list_resp.json()
    assert list_data["success"] is True
    assert list_data["status"] == 200
    assert list_data["message"] == "Services retrieved successfully."
    assert len(list_data["data"]) == 1
    assert list_data["data"][0]["id"] == service_id

    # Also test list all without status query param
    list_all_resp = client.get("/api/Provider/services/list", headers=headers)
    assert list_all_resp.status_code == 200
    assert len(list_all_resp.json()["data"]) == 1

    # 3. Get single service detail (GET /api/Provider/services/{service_id})
    detail_resp = client.get(f"/api/Provider/services/{service_id}", headers=headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["data"]["id"] == service_id

    # 4. Patch service (PATCH /api/Provider/services/{service_id})
    patch_payload = {
        "title": "Strategy Session",
        "price": "160.00",
        "cancellation_policy": "flexible",
        "benefits": [
            {"outcome": "A clear 90-day plan"},
            {"outcome": "Accountability"},
        ],
    }
    patch_resp = client.patch(
        f"/api/Provider/services/{service_id}",
        json=patch_payload,
        headers=headers,
    )
    assert patch_resp.status_code == 200
    patch_data = patch_resp.json()
    assert patch_data["message"] == "Service updated successfully."
    assert patch_data["data"]["title"] == "Strategy Session"
    assert patch_data["data"]["price"] == "160.00"
    assert patch_data["data"]["cancellation_policy"] == "flexible"
    assert len(patch_data["data"]["benefits"]) == 2
    assert patch_data["data"]["benefits"][0]["outcome"] == "A clear 90-day plan"
    assert patch_data["data"]["benefits"][1]["outcome"] == "Accountability"

    # 5. Delete service (DELETE /api/Provider/services/{service_id})
    del_resp = client.delete(f"/api/Provider/services/{service_id}", headers=headers)
    assert del_resp.status_code == 200
    del_data = del_resp.json()
    assert del_data["success"] is True
    assert del_data["message"] == "Service deleted successfully."
    assert del_data["data"]["id"] == service_id

    # Verify service is gone
    get_deleted = client.get(f"/api/Provider/services/{service_id}", headers=headers)
    assert get_deleted.status_code == 404


def test_services_access_and_validation(test_coach_and_category, db_session):
    coach, profile, category, other_coach, other_profile = test_coach_and_category
    client = TestClient(app)

    # 1. Pending coach blocked from creating service
    pending_user = db_session.execute(
        select(User).where(User.email == "pending_svc_coach@coachhub.com")
    ).scalar_one_or_none()
    if not pending_user:
        pending_user = User(
            full_name="Pending Coach User",
            email="pending_svc_coach@coachhub.com",
            password_hash="pw",
            role="COACH",
            coach_status="pending",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(pending_user)
        db_session.commit()
        db_session.refresh(pending_user)


    pending_token, _ = create_access_token(pending_user.id, pending_user.role, pending_user.full_name)
    pending_headers = {"Authorization": f"Bearer {pending_token}"}

    blocked_resp = client.post(
        "/api/Provider/services/create",
        json={"title": "Test", "category": category.id},
        headers=pending_headers,
    )
    assert blocked_resp.status_code == 403
    assert blocked_resp.json()["error"] == "COACH_NOT_APPROVED"

    # 2. Approved coach with non-existent category gets 404
    coach_token, _ = create_access_token(coach.id, coach.role, coach.full_name)
    coach_headers = {"Authorization": f"Bearer {coach_token}"}
    cat_err_resp = client.post(
        "/api/Provider/services/create",
        json={"title": "Test", "category": 999999},
        headers=coach_headers,
    )
    assert cat_err_resp.status_code == 404
    assert cat_err_resp.json()["error"] == "CATEGORY_NOT_FOUND"

    # 3. Cross-coach ownership protection
    # Create service as coach 1
    create_resp = client.post(
        "/api/Provider/services/create",
        json={"title": "Private Coach 1 Service", "category": category.id},
        headers=coach_headers,
    )
    svc_id = create_resp.json()["data"]["id"]

    # Coach 2 cannot get, patch or delete Coach 1's service
    other_token, _ = create_access_token(other_coach.id, other_coach.role, other_coach.full_name)
    other_headers = {"Authorization": f"Bearer {other_token}"}

    get_other = client.get(f"/api/Provider/services/{svc_id}", headers=other_headers)
    assert get_other.status_code == 404

    patch_other = client.patch(
        f"/api/Provider/services/{svc_id}",
        json={"title": "Hacked"},
        headers=other_headers,
    )
    assert patch_other.status_code == 404

    del_other = client.delete(f"/api/Provider/services/{svc_id}", headers=other_headers)
    assert del_other.status_code == 404
