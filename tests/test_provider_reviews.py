import pytest
from starlette.testclient import TestClient
from sqlalchemy import select

from src.main import app
from src.core.database import SessionLocal
from src.models.accounts.user import User
from src.models.provider.coach_profile import CoachProfile, CoachReview
from src.utils.jwt import create_access_token


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_coach_and_buyer(db_session):
    coach = db_session.execute(
        select(User).where(User.email == "review_coach@coachhub.com")
    ).scalar_one_or_none()

    if not coach:
        coach = User(
            full_name="Review Coach",
            email="review_coach@coachhub.com",
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
            headline="Expert Review Coach",
            about="Top rated coach",
            status="approved",
            is_completed=True,
            avg_rating=5.0,
            total_reviews=1,
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)

    buyer = db_session.execute(
        select(User).where(User.email == "jane_buyer@example.com")
    ).scalar_one_or_none()

    if not buyer:
        buyer = User(
            full_name="Jane Buyer",
            email="jane_buyer@example.com",
            password_hash="test_hashed_password",
            phone="+9876543210",
            role="USER",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(buyer)
        db_session.commit()
        db_session.refresh(buyer)

    # Clean existing reviews for this coach profile if any
    existing_reviews = db_session.execute(
        select(CoachReview).where(CoachReview.coach_profile_id == profile.id)
    ).scalars().all()
    for rev in existing_reviews:
        db_session.delete(rev)
    db_session.commit()

    # Add a sample review
    review = CoachReview(
        coach_profile_id=profile.id,
        user_id=buyer.id,
        rating=5,
        review="Brilliant session, very practical.",
    )
    db_session.add(review)
    db_session.commit()

    return coach, buyer, profile


def test_get_coach_reviews(test_coach_and_buyer, db_session):
    coach, buyer, profile = test_coach_and_buyer

    client = TestClient(app)
    token, _ = create_access_token(
        user_id=coach.id,
        role=coach.role,
        full_name=coach.full_name,
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/Provider/reviews", headers=headers)

    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["message"] == "Reviews retrieved successfully."

    data = res_data["data"]
    assert data["avg_rating"] == 5.0
    assert data["total_reviews"] == 1
    assert data["rating_breakdown"] == {
        "5": 1,
        "4": 0,
        "3": 0,
        "2": 0,
        "1": 0
    }

    assert len(data["reviews"]) == 1
    first_review = data["reviews"][0]
    assert first_review["user_name"] == "Jane Buyer"
    assert first_review["rating"] == 5
    assert first_review["review"] == "Brilliant session, very practical."
    assert "created_at" in first_review
