import pytest
from fastapi import APIRouter, Depends, status
from starlette.testclient import TestClient

from src.main import app
from src.core.common_responses import CommonResponse
from src.core.database import SessionLocal
from src.core.dependencies import require_approved_coach, require_provider_role
from src.models.accounts.user import User
from src.utils.jwt import create_access_token

# Test dummy route requiring approved coach
dummy_router = APIRouter(prefix="/test-access", tags=["Test Access"])


@dummy_router.get("/operational", response_model=CommonResponse)
async def check_operational_route(user: User = Depends(require_approved_coach)):
    return CommonResponse(
        success=True,
        status=status.HTTP_200_OK,
        message="Operational access granted",
        data={"user_id": str(user.id), "coach_status": user.coach_status},
    )


app.include_router(dummy_router)


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_pending_coach_blocked_from_operational_route(db):
    client = TestClient(app)

    # Create test pending coach user
    user = User(
        full_name="Pending Coach",
        email="pending_coach@example.com",
        password_hash="hashed_pw",
        role="COACH",
        coach_status="pending",
        is_email_verified=True,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token, _ = create_access_token(user.id, user.role, user.full_name)
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt operational route
    response = client.get("/test-access/operational", headers=headers)
    assert response.status_code == 403, response.text
    res_data = response.json()
    assert res_data["success"] is False
    assert res_data["error"] == "COACH_NOT_APPROVED"
    assert res_data["data"]["coach_status"] == "pending"

    # Cleanup
    db.delete(user)
    db.commit()


def test_approved_coach_allowed_on_operational_route(db):
    client = TestClient(app)

    # Create test approved coach user
    user = User(
        full_name="Approved Coach",
        email="approved_coach@example.com",
        password_hash="hashed_pw",
        role="COACH",
        coach_status="approved",
        is_email_verified=True,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token, _ = create_access_token(user.id, user.role, user.full_name)
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt operational route
    response = client.get("/test-access/operational", headers=headers)
    assert response.status_code == 200, response.text
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["coach_status"] == "approved"

    # Cleanup
    db.delete(user)
    db.commit()
