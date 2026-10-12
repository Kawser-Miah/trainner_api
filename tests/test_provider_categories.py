import pytest
from starlette.testclient import TestClient
from sqlalchemy import select

from src.main import app
from src.core.database import SessionLocal
from src.models.provider.category import Category


@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def client():
    return TestClient(app)


def test_list_categories_endpoints(client, db_session):
    # Ensure default or test categories exist
    existing = db_session.execute(select(Category)).scalars().all()
    if not existing:
        cat1 = Category(name="Business", description="Business coaching", is_active=True, image="media/category_images/business.png")
        cat2 = Category(name="Fitness", description="Fitness coaching", is_active=True, image=None)
        db_session.add_all([cat1, cat2])
        db_session.commit()

    # Test GET /Provider/categories-list/
    response_slash = client.get("/Provider/categories-list/")
    assert response_slash.status_code == 200
    json_data = response_slash.json()
    assert json_data["success"] is True
    assert json_data["status"] == 200
    assert json_data["message"] == "Categories retrieved successfully."
    assert isinstance(json_data["data"], list)
    assert len(json_data["data"]) > 0

    first_item = json_data["data"][0]
    assert "id" in first_item
    assert "name" in first_item
    assert "description" in first_item
    assert "is_active" in first_item
    assert "image" in first_item

    # Test GET /Provider/categories-list without trailing slash
    response_no_slash = client.get("/Provider/categories-list")
    assert response_no_slash.status_code == 200
    assert response_no_slash.json()["success"] is True

    # Test GET with /api prefix /api/Provider/categories-list/
    response_api = client.get("/api/Provider/categories-list/")
    assert response_api.status_code == 200
    assert response_api.json()["success"] is True

    # Test filter by is_active=true
    response_active = client.get("/Provider/categories-list/?is_active=true")
    assert response_active.status_code == 200
    for item in response_active.json()["data"]:
        assert item["is_active"] is True
