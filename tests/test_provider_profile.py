import io
import struct
from pathlib import Path
import pytest
from starlette.testclient import TestClient
from sqlalchemy import select, text

from src.main import app
from src.core.database import SessionLocal
from src.models.accounts.user import User
from src.models.provider.coach_profile import CoachProfile
from src.utils.jwt import create_access_token


def create_sample_mp4(duration_seconds: int = 60, timescale: int = 1000) -> bytes:
    duration_units = int(duration_seconds * timescale)
    mvhd_payload = bytearray()
    mvhd_payload.extend(b"\x00\x00\x00\x00")
    mvhd_payload.extend(b"\x00\x00\x00\x00")
    mvhd_payload.extend(b"\x00\x00\x00\x00")
    mvhd_payload.extend(struct.pack(">I", timescale))
    mvhd_payload.extend(struct.pack(">I", duration_units))
    mvhd_payload.extend(b"\x00" * 76)

    mvhd_atom = struct.pack(">I4s", len(mvhd_payload) + 8, b"mvhd") + mvhd_payload
    moov_atom = struct.pack(">I4s", len(mvhd_atom) + 8, b"moov") + mvhd_atom
    ftyp_atom = struct.pack(">I4s4sI", 16, b"ftyp", b"isom", 512)
    return ftyp_atom + moov_atom


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_coach_user(db_session):
    # Find or create a test user
    user = db_session.execute(
        select(User).where(User.email == "test_provider@coachhub.com")
    ).scalar_one_or_none()

    if not user:
        user = User(
            full_name="Test Coach User",
            email="test_provider@coachhub.com",
            password_hash="test_hashed_password",
            phone="+1234567890",
            role="COACH",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    # Clean up existing coach profile for this test user if any
    existing_profile = db_session.execute(
        select(CoachProfile).where(CoachProfile.user_id == user.id)
    ).scalar_one_or_none()
    if existing_profile:
        db_session.delete(existing_profile)
        db_session.commit()

    return user


def test_create_and_fetch_profile_with_only_introvideo(test_coach_user, db_session):
    client = TestClient(app)
    token, _ = create_access_token(
        user_id=test_coach_user.id,
        role=test_coach_user.role,
        full_name=test_coach_user.full_name,
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Generate an 85-second test video (1:25)
    video_bytes = create_sample_mp4(85)

    # 1. User sends ONLY the introvideo file in multipart/form-data
    response = client.post(
        "/api/Provider/coach-profile",
        headers=headers,
        files={
            "introvideo": ("sample_intro.mp4", io.BytesIO(video_bytes), "video/mp4"),
        },
    )

    assert response.status_code == 201, response.text
    res_data = response.json()
    assert res_data["success"] is True
    profile_data = res_data["data"]

    # Check that video duration and video display duration were computed and returned
    assert profile_data["introduction_video_duration"] == 85
    assert profile_data["introduction_video_duration_display"] == "1:25"
    assert profile_data["introduction_video"] is not None

    # 2. Check directly in the database to verify it is stored
    db_session.expire_all()
    saved_profile = db_session.execute(
        select(CoachProfile).where(CoachProfile.user_id == test_coach_user.id)
    ).scalar_one()

    assert saved_profile.introduction_video_duration == 85

    # 3. Fetch from database using GET /api/Provider/coach-profile
    get_res = client.get("/api/Provider/coach-profile", headers=headers)
    assert get_res.status_code == 200
    get_data = get_res.json()["data"]
    assert get_data["introduction_video_duration"] == 85
    assert get_data["introduction_video_duration_display"] == "1:25"

    # 4. Update with a new 45-second video (0:45)
    new_video_bytes = create_sample_mp4(45)
    patch_res = client.patch(
        "/api/Provider/coach-profile",
        headers=headers,
        files={
            "intro_video": ("updated_intro.mp4", io.BytesIO(new_video_bytes), "video/mp4"),
        },
    )
    assert patch_res.status_code == 200
    patch_data = patch_res.json()["data"]
    assert patch_data["introduction_video_duration"] == 45
    assert patch_data["introduction_video_duration_display"] == "0:45"

    # 5. Check in the database that updated values are stored
    db_session.expire_all()
    updated_profile = db_session.execute(
        select(CoachProfile).where(CoachProfile.user_id == test_coach_user.id)
    ).scalar_one()
    assert updated_profile.introduction_video_duration == 45

    # 6. Update only text fields without re-uploading video - duration must remain intact
    patch_text_res = client.patch(
        "/api/Provider/coach-profile",
        headers=headers,
        data={"headline": "Updated Master Coach"},
    )
    assert patch_text_res.status_code == 200
    patch_text_data = patch_text_res.json()["data"]
    assert patch_text_data["headline"] == "Updated Master Coach"
    assert patch_text_data["introduction_video_duration"] == 45
    assert patch_text_data["introduction_video_duration_display"] == "0:45"


def test_refresh_token_with_db_user(test_coach_user):
    from src.utils.jwt import create_refresh_token

    client = TestClient(app)
    refresh_token_str = create_refresh_token(user_id=test_coach_user.id)

    response = client.post(
        "/api/auth/refresh-token/",
        json={"refresh_token": refresh_token_str},
    )

    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["success"] is True
    assert "access_token" in res_data["data"]
    assert res_data["data"]["access_token"] is not None
