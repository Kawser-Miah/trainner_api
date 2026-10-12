import pytest
from starlette.testclient import TestClient
from sqlalchemy import select

from src.main import app
from src.core.database import SessionLocal
from src.models.accounts.user import User
from src.models.provider.category import Category
from src.models.provider.coach_profile import CoachProfile
from src.models.provider.coach_profile.coach_availability import CoachAvailability
from src.models.provider.coach_profile.coach_review import CoachReview
from src.models.provider.service.coach_service import CoachService, CoachServiceBenefit
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
def client_user(db_session):
    u = db_session.execute(
        select(User).where(User.email == "test_client_browse@coachhub.com")
    ).scalar_one_or_none()
    if not u:
        u = User(
            full_name="Client Browser User",
            email="test_client_browse@coachhub.com",
            password_hash="test_pw_hash",
            phone="+123456789",
            role="USER",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(u)
        db_session.commit()
        db_session.refresh(u)
    return u


@pytest.fixture
def client_headers(client_user):
    token, _ = create_access_token(
        user_id=client_user.id,
        role=client_user.role,
        full_name=client_user.full_name,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seed_coach_data(db_session):
    # Ensure test category
    cat = db_session.execute(
        select(Category).where(Category.name == "Business")
    ).scalar_one_or_none()
    if not cat:
        cat = Category(name="Business", description="Business coaching", is_active=True)
        db_session.add(cat)
        db_session.commit()
        db_session.refresh(cat)

    # Ensure test coach user
    c_user = db_session.execute(
        select(User).where(User.email == "sarah_chen_browse@coachhub.com")
    ).scalar_one_or_none()
    if not c_user:
        c_user = User(
            full_name="Sarah Chen",
            email="sarah_chen_browse@coachhub.com",
            password_hash="test_pw_hash",
            phone="+1987654321",
            address="New York, USA",
            role="COACH",
            coach_status="approved",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(c_user)
        db_session.commit()
        db_session.refresh(c_user)

    # Ensure test coach profile
    profile = db_session.execute(
        select(CoachProfile).where(CoachProfile.user_id == c_user.id)
    ).scalar_one_or_none()
    if not profile:
        profile = CoachProfile(
            user_id=c_user.id,
            headline="Executive & Startup Coach",
            about="I help founders scale.",
            status="approved",
            is_completed=True,
            avg_rating=5.0,
            total_reviews=1,
            completed_sessions_count=2,
            success_rate=67.0,
            introduction_video_duration=222,
        )
        profile.categories.append(cat)
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)

    # Ensure availability
    avail = db_session.execute(
        select(CoachAvailability).where(CoachAvailability.coach_profile_id == profile.id)
    ).scalar_one_or_none()
    if not avail:
        avail = CoachAvailability(
            coach_profile_id=profile.id,
            weekly=[{"weekday": 0, "start_time": "09:00", "end_time": "17:00"}],
            on_call=[{"weekday": 0, "start_time": "17:00", "end_time": "21:00"}],
            on_call_enabled=True,
            time_off=[],
        )
        db_session.add(avail)
        db_session.commit()

    # Ensure review
    rev = db_session.execute(
        select(CoachReview).where(CoachReview.coach_profile_id == profile.id)
    ).scalar_one_or_none()
    if not rev:
        rev = CoachReview(
            coach_profile_id=profile.id,
            user_id=c_user.id,
            rating=5,
            review="Brilliant session, very practical.",
        )
        db_session.add(rev)
        db_session.commit()

    # Ensure service
    srv = db_session.execute(
        select(CoachService).where(CoachService.coach_profile_id == profile.id)
    ).scalar_one_or_none()
    if not srv:
        srv = CoachService(
            coach_profile_id=profile.id,
            category_id=cat.id,
            title="Strategy Session",
            description="A 1:1 strategy session.",
            price="160.00",
            session_duration=60,
            status="published",
        )
        db_session.add(srv)
        db_session.commit()
        db_session.refresh(srv)
        b1 = CoachServiceBenefit(service_id=srv.id, outcome="A clear 90-day plan")
        db_session.add(b1)
        db_session.commit()

    return {"profile": profile, "service": srv}


def test_user_category_list(client, client_headers, seed_coach_data):
    res = client.get("/user/user-category-list", headers=client_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["message"] == "Categories retrieved successfully."
    assert isinstance(data["data"], list)
    assert any(c["name"] == "Business" for c in data["data"])


def test_coach_profile_list(client, client_headers, seed_coach_data):
    res = client.get("/user/coach-profile-list?search=Sarah&ordering=rating", headers=client_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["message"] == "Coach profiles retrieved successfully."
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0
    assert data["data"][0]["user"]["full_name"] == "Sarah Chen"


def test_recommended_coach_profile_list(client, client_headers, seed_coach_data):
    res = client.get("/user/recommended-coach-profile-list", headers=client_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["message"] == "Recommended coach profiles retrieved successfully."
    assert isinstance(data["data"], list)


def test_coach_profile_detail(client, client_headers, seed_coach_data):
    prof_id = seed_coach_data["profile"].id
    res = client.get(f"/user/coach-profile/{prof_id}", headers=client_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["message"] == "Coach profile details retrieved successfully."
    assert data["data"]["id"] == prof_id
    assert data["data"]["introduction_video_duration_display"] == "3:42"
    assert "services" in data["data"]


def test_coach_availability_date_and_month(client, client_headers, seed_coach_data):
    prof_id = seed_coach_data["profile"].id
    # Test date query
    res_date = client.get(f"/user/coaches/{prof_id}/availability?date=2026-10-12", headers=client_headers)
    assert res_date.status_code == 200
    d_data = res_date.json()
    assert d_data["success"] is True
    assert d_data["message"] == "Availability retrieved successfully."
    assert "slots" in d_data["data"]
    assert "on_call" in d_data["data"]

    # Test month query
    res_month = client.get(f"/user/coaches/{prof_id}/availability?month=2026-10", headers=client_headers)
    assert res_month.status_code == 200
    m_data = res_month.json()
    assert m_data["success"] is True
    assert m_data["message"] == "Available dates retrieved successfully."
    assert "available_dates" in m_data["data"]


def test_coach_reviews(client, client_headers, seed_coach_data):
    prof_id = seed_coach_data["profile"].id
    res = client.get(f"/user/coaches/{prof_id}/reviews", headers=client_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["message"] == "Reviews retrieved successfully."
    assert data["data"]["coach_profile_id"] == prof_id
    assert "rating_breakdown" in data["data"]
    assert len(data["data"]["reviews"]) > 0


def test_user_service_list_and_detail(client, client_headers, seed_coach_data):
    prof_id = seed_coach_data["profile"].id
    srv_id = seed_coach_data["service"].id

    # List
    res_list = client.get(f"/user/user-service-list?coach_profile={prof_id}", headers=client_headers)
    assert res_list.status_code == 200
    data_list = res_list.json()
    assert data_list["success"] is True
    assert data_list["message"] == "Services retrieved successfully."
    assert len(data_list["data"]) > 0
    assert "provider_details" in data_list["data"][0]

    # Detail
    res_detail = client.get(f"/user/user-service-detail/{srv_id}", headers=client_headers)
    assert res_detail.status_code == 200
    data_detail = res_detail.json()
    assert data_detail["success"] is True
    assert data_detail["message"] == "Service details retrieved successfully."
    assert data_detail["data"]["id"] == srv_id
    assert "other_sessions" in data_detail["data"]


def test_client_endpoints_require_client_role(client, seed_coach_data):
    prof_id = seed_coach_data["profile"].id
    # No auth header -> 400 / 401
    res = client.get("/user/user-category-list")
    assert res.status_code in [400, 401, 403]
