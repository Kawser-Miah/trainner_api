import pytest
from sqlalchemy import select
from starlette.testclient import TestClient

from src.core.database import SessionLocal
from src.main import app
from src.models.accounts.user import User
from src.models.client.coach_favorite import CoachFavorite
from src.models.provider.category import Category
from src.models.provider.coach_profile import CoachProfile
from src.models.provider.coach_profile.coach_availability import CoachAvailability
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
        select(User).where(User.email == "client_favorites_test@coachhub.com")
    ).scalar_one_or_none()
    if not u:
        u = User(
            full_name="Favorite Test User",
            email="client_favorites_test@coachhub.com",
            password_hash="test_pw_hash",
            phone="+1234567890",
            address="San Francisco, USA",
            role="USER",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(u)
        db_session.commit()
        db_session.refresh(u)
    return u


@pytest.fixture
def coach_user(db_session):
    u = db_session.execute(
        select(User).where(User.email == "coach_favorites_test@coachhub.com")
    ).scalar_one_or_none()
    if not u:
        u = User(
            full_name="Sarah Chen",
            email="coach_favorites_test@coachhub.com",
            password_hash="test_pw_hash",
            phone="+1987654321",
            address="New York, USA",
            role="COACH",
            coach_status="approved",
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
def coach_headers(coach_user):
    token, _ = create_access_token(
        user_id=coach_user.id,
        role=coach_user.role,
        full_name=coach_user.full_name,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seed_coach_profile(db_session, coach_user):
    # Ensure category
    cat = db_session.execute(
        select(Category).where(Category.name == "Business")
    ).scalar_one_or_none()
    if not cat:
        cat = Category(name="Business", description="Business coaching", is_active=True)
        db_session.add(cat)
        db_session.commit()
        db_session.refresh(cat)

    # Ensure coach profile
    profile = db_session.execute(
        select(CoachProfile).where(CoachProfile.user_id == coach_user.id)
    ).scalar_one_or_none()
    if not profile:
        profile = CoachProfile(
            user_id=coach_user.id,
            headline="Executive & Startup Coach",
            about="I help founders scale.",
            status="approved",
            is_completed=True,
            avg_rating=5.0,
            total_reviews=2,
            completed_sessions_count=2,
            introduction_video_duration=222,
            linkedin_url="https://www.linkedin.com/in/sarah-chen",
            affiliate_commission_percent="12.50",
            expertises=["Leadership", "Strategy"],
            languages=["English", "French"],
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
            weekly=[],
            on_call=[],
            on_call_enabled=True,
            time_off=[],
        )
        db_session.add(avail)
        db_session.commit()

    return profile


def test_add_favorite_coach_success(client, client_user, seed_coach_profile, client_headers, db_session):
    # Ensure clean state
    db_session.query(CoachFavorite).filter(
        CoachFavorite.user_id == client_user.id,
        CoachFavorite.coach_profile_id == seed_coach_profile.id,
    ).delete()
    db_session.commit()

    resp = client.post(
        f"/user/favorites/{seed_coach_profile.id}",
        headers=client_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["status"] == 201
    assert body["message"] == "Coach added to favorites."
    assert body["data"]["coach_id"] == seed_coach_profile.id
    assert body["data"]["is_favorited"] is True


def test_add_favorite_coach_idempotent(client, client_user, seed_coach_profile, client_headers):
    # Post again
    resp = client.post(
        f"/user/favorites/{seed_coach_profile.id}",
        headers=client_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["is_favorited"] is True


def test_add_favorite_coach_not_found(client, client_headers):
    resp = client.post(
        "/user/favorites/999999",
        headers=client_headers,
    )
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "COACH_PROFILE_NOT_FOUND"


def test_get_favorite_coaches(client, client_user, seed_coach_profile, client_headers):
    # Ensure favorited
    client.post(
        f"/user/favorites/{seed_coach_profile.id}",
        headers=client_headers,
    )

    resp = client.get(
        "/user/favorites",
        headers=client_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["status"] == 200
    assert body["message"] == "Favorite coaches retrieved successfully."
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 1

    item = next((c for c in body["data"] if c["id"] == seed_coach_profile.id), None)
    assert item is not None
    assert item["id"] == seed_coach_profile.id
    assert item["is_favorited"] is True
    assert "user" in item
    assert item["user"]["full_name"] == "Sarah Chen"
    assert "categories" in item
    assert "Business" in item["categories"]
    assert item["headline"] == "Executive & Startup Coach"
    assert item["about"] == "I help founders scale."
    assert item["affiliate_commission_percent"] == "12.50"
    assert item["introduction_video_duration"] == 222
    assert item["linkedin_url"] == "https://www.linkedin.com/in/sarah-chen"
    assert item["on_call_enabled"] is True
    assert "affiliate_status" in item
    assert "affiliate_code" in item
    assert "timezone" in item


def test_browse_list_and_detail_reflect_favorited(client, client_user, seed_coach_profile, client_headers):
    # Detail check
    resp_detail = client.get(
        f"/user/coach-profile/{seed_coach_profile.id}",
        headers=client_headers,
    )
    assert resp_detail.status_code == 200
    assert resp_detail.json()["data"]["is_favorited"] is True

    # List check
    resp_list = client.get(
        "/user/coach-profile-list",
        headers=client_headers,
    )
    assert resp_list.status_code == 200
    coach_item = next((c for c in resp_list.json()["data"] if c["id"] == seed_coach_profile.id), None)
    assert coach_item is not None
    assert coach_item["is_favorited"] is True


def test_remove_favorite_coach_success(client, client_user, seed_coach_profile, client_headers):
    resp = client.delete(
        f"/user/favorites/{seed_coach_profile.id}",
        headers=client_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["status"] == 200
    assert body["message"] == "Coach removed from favorites."
    assert body["data"]["coach_id"] == seed_coach_profile.id
    assert body["data"]["is_favorited"] is False

    # Check GET /user/favorites no longer contains this coach
    resp_get = client.get(
        "/user/favorites",
        headers=client_headers,
    )
    assert resp_get.status_code == 200
    found = any(c["id"] == seed_coach_profile.id for c in resp_get.json()["data"])
    assert found is False

    # Check detail now shows is_favorited == False
    resp_detail = client.get(
        f"/user/coach-profile/{seed_coach_profile.id}",
        headers=client_headers,
    )
    assert resp_detail.status_code == 200
    assert resp_detail.json()["data"]["is_favorited"] is False


def test_remove_favorite_coach_idempotent(client, seed_coach_profile, client_headers):
    resp = client.delete(
        f"/user/favorites/{seed_coach_profile.id}",
        headers=client_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["is_favorited"] is False


def test_remove_favorite_coach_not_found(client, client_headers):
    resp = client.delete(
        "/user/favorites/999999",
        headers=client_headers,
    )
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "COACH_PROFILE_NOT_FOUND"


def test_favorites_access_control(client, coach_headers):
    # Unauthenticated (raises InvalidTokenException -> 400 INVALID_TOKEN)
    resp_unauth = client.get("/user/favorites")
    assert resp_unauth.status_code == 400
    assert resp_unauth.json()["error"] == "INVALID_TOKEN"

    resp_unauth_post = client.post("/user/favorites/1")
    assert resp_unauth_post.status_code == 400
    assert resp_unauth_post.json()["error"] == "INVALID_TOKEN"

    resp_unauth_del = client.delete("/user/favorites/1")
    assert resp_unauth_del.status_code == 400
    assert resp_unauth_del.json()["error"] == "INVALID_TOKEN"

    # Non-client role (COACH role -> 403 FORBIDDEN_ROLE)
    resp_forbidden = client.get("/user/favorites", headers=coach_headers)
    assert resp_forbidden.status_code == 403
    assert resp_forbidden.json()["error"] == "FORBIDDEN_ROLE"

    resp_forbidden_post = client.post("/user/favorites/1", headers=coach_headers)
    assert resp_forbidden_post.status_code == 403
    assert resp_forbidden_post.json()["error"] == "FORBIDDEN_ROLE"

    resp_forbidden_del = client.delete("/user/favorites/1", headers=coach_headers)
    assert resp_forbidden_del.status_code == 403
    assert resp_forbidden_del.json()["error"] == "FORBIDDEN_ROLE"
