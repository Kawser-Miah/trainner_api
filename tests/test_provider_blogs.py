import io
import pytest
from starlette.testclient import TestClient
from sqlalchemy import select

from src.main import app
from src.core.database import SessionLocal
from src.models.accounts.user import User
from src.models.provider.category import Category
from src.models.provider.coach_profile import CoachProfile
from src.models.provider.blog.coach_blog import CoachBlog
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
        select(User).where(User.email == "blog_coach@coachhub.com")
    ).scalar_one_or_none()
    if not coach:
        coach = User(
            full_name="Blog Coach",
            email="blog_coach@coachhub.com",
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
            headline="Expert Founder Coach",
            about="I help founders build great companies.",
            is_completed=True,
            status="approved",
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)

    return coach, profile, category


@pytest.fixture
def coach_headers(test_coach_and_category):
    coach, _, _ = test_coach_and_category
    token, _ = create_access_token(
        user_id=coach.id,
        role=coach.role,
        full_name=coach.full_name,
    )
    return {"Authorization": f"Bearer {token}"}


def test_create_and_manage_blog(test_coach_and_category, coach_headers, db_session):
    coach, profile, category = test_coach_and_category
    client = TestClient(app)

    # 1. Create Blog with image
    fake_image_file = io.BytesIO(b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;")
    fake_image_file.name = "founder_habits.gif"

    create_data = {
        "title": "Five habits of great founders",
        "category": str(category.id),
        "content": "Long article text...",
        "status": "published",
    }
    files = {
        "image": ("founder_habits.gif", fake_image_file, "image/gif"),
    }

    resp = client.post(
        "/api/Provider/blogs/create",
        data=create_data,
        files=files,
        headers=coach_headers,
    )
    assert resp.status_code == 201, resp.text
    res_json = resp.json()
    assert res_json["success"] is True
    assert res_json["status"] == 201
    assert res_json["message"] == "Blog created successfully."
    blog_data = res_json["data"]
    assert blog_data["title"] == "Five habits of great founders"
    assert blog_data["coach"] == coach.id
    assert blog_data["category"] == category.id
    assert blog_data["category_details"]["name"] == "Business"
    assert blog_data["status"] == "published"
    assert blog_data["image"] is not None
    assert "/media/coach/blogs/" in blog_data["image"]
    blog_id = blog_data["id"]

    # 2. List blogs with filter ?status=published
    list_resp = client.get(
        "/api/Provider/blogs/create?status=published",
        headers=coach_headers,
    )
    assert list_resp.status_code == 200, list_resp.text
    list_json = list_resp.json()
    assert list_json["success"] is True
    assert list_json["message"] == "Blogs retrieved successfully."
    assert any(b["id"] == blog_id for b in list_json["data"])

    # 3. Also check list via /api/Provider/blogs
    list_resp2 = client.get(
        "/api/Provider/blogs?status=published",
        headers=coach_headers,
    )
    assert list_resp2.status_code == 200

    # 4. Get blog detail
    detail_resp = client.get(
        f"/api/Provider/blogs/{blog_id}",
        headers=coach_headers,
    )
    assert detail_resp.status_code == 200, detail_resp.text
    detail_json = detail_resp.json()
    assert detail_json["data"]["id"] == blog_id
    assert detail_json["data"]["title"] == "Five habits of great founders"

    # 5. Update blog (PATCH)
    patch_data = {
        "title": "Five habits of great founders (Updated)",
        "content": "Updated article content text...",
    }
    patch_resp = client.patch(
        f"/api/Provider/blogs/{blog_id}",
        data=patch_data,
        headers=coach_headers,
    )
    assert patch_resp.status_code == 200, patch_resp.text
    patch_json = patch_resp.json()
    assert patch_json["data"]["title"] == "Five habits of great founders (Updated)"
    assert patch_json["data"]["content"] == "Updated article content text..."

    # 6. Delete blog
    del_resp = client.delete(
        f"/api/Provider/blogs/{blog_id}",
        headers=coach_headers,
    )
    assert del_resp.status_code == 200, del_resp.text
    del_json = del_resp.json()
    assert del_json["success"] is True
    assert del_json["message"] == "Blog deleted successfully."
    assert del_json["data"]["id"] == blog_id

    # 7. Verify blog is deleted
    get_again = client.get(
        f"/api/Provider/blogs/{blog_id}",
        headers=coach_headers,
    )
    assert get_again.status_code == 404


def test_create_blog_without_image_and_lowercase_prefix(test_coach_and_category, coach_headers):
    coach, profile, category = test_coach_and_category
    client = TestClient(app)

    create_data = {
        "title": "How to Build Confidence",
        "category": str(category.id),
        "content": "Confidence is key. Confidence is key...",
        "status": "published",
    }

    # Test lowercase prefix /api/provider/blogs/create
    resp = client.post(
        "/api/provider/blogs/create",
        data=create_data,
        headers=coach_headers,
    )
    assert resp.status_code == 201, resp.text
    blog_data = resp.json()["data"]
    assert blog_data["title"] == "How to Build Confidence"
    assert blog_data["image"] is None
    blog_id = blog_data["id"]

    # Verify lowercase list
    list_resp = client.get(
        "/api/provider/blogs/create?status=published",
        headers=coach_headers,
    )
    assert list_resp.status_code == 200

    # Cleanup
    del_resp = client.delete(
        f"/api/provider/blogs/{blog_id}",
        headers=coach_headers,
    )
    assert del_resp.status_code == 200


def test_unapproved_coach_forbidden(db_session, test_coach_and_category):
    _, _, category = test_coach_and_category
    client = TestClient(app)

    unapproved = db_session.execute(
        select(User).where(User.email == "unapproved_coach@coachhub.com")
    ).scalar_one_or_none()
    if not unapproved:
        unapproved = User(
            full_name="Unapproved Coach",
            email="unapproved_coach@coachhub.com",
            password_hash="test_password",
            role="COACH",
            coach_status="pending",
            is_email_verified=True,
            is_active=True,
        )
        db_session.add(unapproved)
        db_session.commit()
        db_session.refresh(unapproved)

    token, _ = create_access_token(
        user_id=unapproved.id,
        role=unapproved.role,
        full_name=unapproved.full_name,
    )
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/Provider/blogs/create", headers=headers)
    assert resp.status_code == 403
    assert resp.json()["error"] == "COACH_NOT_APPROVED"
