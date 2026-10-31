import io
from pathlib import Path
import pytest
from pypdf import PdfWriter, PdfReader
from starlette.testclient import TestClient
from sqlalchemy import select

from src.main import app
from src.core.database import SessionLocal
from src.models.accounts.user import User
from src.models.provider.category import Category
from src.models.provider.coach_profile import CoachProfile
from src.models.provider.product.coach_product import CoachProduct
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
        select(User).where(User.email == "product_coach@coachhub.com")
    ).scalar_one_or_none()
    if not coach:
        coach = User(
            full_name="Product Coach",
            email="product_coach@coachhub.com",
            password_hash="test_hashed_password",
            phone="+1234567899",
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
            headline="Author and Product Coach",
            about="I write guides and workbooks.",
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


def test_create_and_manage_product(test_coach_and_category, coach_headers, db_session):
    coach, profile, category = test_coach_and_category
    client = TestClient(app)

    fake_thumb = io.BytesIO(b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;")
    fake_thumb.name = "photo.gif"

    book_content = b"%PDF-1.4 Fake PDF Content for Workbook"
    fake_book = io.BytesIO(book_content)
    fake_book.name = "workbook.pdf"

    # 1. Create Product (POST /api/Provider/products/create)
    create_data = {
        "title": "Interview Workbook",
        "description": "Practice questions",
        "category": str(category.id),
        "price": "19.00",
        "status": "published",
    }
    files = {
        "Thumbnail": ("photo.gif", fake_thumb, "image/gif"),
        "book_file": ("workbook.pdf", fake_book, "application/pdf"),
    }

    resp = client.post(
        "/api/Provider/products/create",
        data=create_data,
        files=files,
        headers=coach_headers,
    )
    assert resp.status_code == 201, resp.text
    res_json = resp.json()
    assert res_json["success"] is True
    assert res_json["status"] == 201
    assert res_json["message"] == "Product created successfully."
    product_data = res_json["data"]
    assert product_data["title"] == "Interview Workbook"
    assert product_data["description"] == "Practice questions"
    # Ensure coach field is central user ID, NOT coach_profile_id
    assert product_data["coach"] == coach.id
    assert product_data["category"] == category.id
    assert product_data["category_details"]["name"] == "Business"
    assert product_data["price"] == "19.00"
    assert product_data["status"] == "published"
    assert product_data["file_type"] == "PDF"
    assert product_data["Thumbnail"] is not None
    assert "/media/coach/products/" in product_data["Thumbnail"]
    assert product_data["download_url"] is not None
    assert f"/api/v1/user/digital-product-download/{product_data['id']}/" in product_data["download_url"]

    product_id = product_data["id"]

    # 2. List Products via /Provider/products-list
    list_resp = client.get(
        "/Provider/products-list",
        headers=coach_headers,
    )
    assert list_resp.status_code == 200, list_resp.text
    list_json = list_resp.json()
    assert list_json["success"] is True
    assert list_json["status"] == 200
    assert list_json["message"] == "Products retrieved successfully."
    assert any(p["id"] == product_id for p in list_json["data"])

    # 3. List Products via /api/Provider/products-list
    list_resp2 = client.get(
        "/api/Provider/products-list?status=published",
        headers=coach_headers,
    )
    assert list_resp2.status_code == 200, list_resp2.text
    assert any(p["id"] == product_id for p in list_resp2.json()["data"])

    # 4. Get Product Detail (GET /Provider/products/{product_id})
    detail_resp = client.get(
        f"/Provider/products/{product_id}",
        headers=coach_headers,
    )
    assert detail_resp.status_code == 200, detail_resp.text
    detail_json = detail_resp.json()
    assert detail_json["data"]["id"] == product_id
    assert detail_json["data"]["title"] == "Interview Workbook"
    assert detail_json["data"]["coach"] == coach.id

    # 5. Download book file
    download_resp = client.get(
        f"/api/v1/user/digital-product-download/{product_id}/",
        headers=coach_headers,
    )
    assert download_resp.status_code == 200, download_resp.text
    assert download_resp.content == book_content

    # 6. Update Product (PATCH /Provider/products/{product_id})
    patch_data = {
        "price": "25.00",
        "description": "Updated practice questions",
    }
    patch_resp = client.patch(
        f"/Provider/products/{product_id}",
        data=patch_data,
        headers=coach_headers,
    )
    assert patch_resp.status_code == 200, patch_resp.text
    patch_json = patch_resp.json()
    assert patch_json["success"] is True
    assert patch_json["message"] == "Product updated successfully."
    assert patch_json["data"]["price"] == "25.00"
    assert patch_json["data"]["description"] == "Updated practice questions"

    # 7. Delete Product (DELETE /Provider/products/{product_id})
    del_resp = client.delete(
        f"/Provider/products/{product_id}",
        headers=coach_headers,
    )
    assert del_resp.status_code == 200, del_resp.text
    del_json = del_resp.json()
    assert del_json["success"] is True
    assert del_json["message"] == "Product deleted successfully."
    assert del_json["data"]["id"] == product_id

    # 8. Verify product is gone
    get_again = client.get(
        f"/Provider/products/{product_id}",
        headers=coach_headers,
    )
    assert get_again.status_code == 404


def test_product_creation_auto_generates_preview_and_page_counts(test_coach_and_category, coach_headers):
    coach, profile, category = test_coach_and_category
    client = TestClient(app)

    # Create a real 4-page PDF in-memory
    writer = PdfWriter()
    for _ in range(4):
        writer.add_blank_page(width=200, height=200)
    pdf_buf = io.BytesIO()
    writer.write(pdf_buf)
    pdf_bytes = pdf_buf.getvalue()

    fake_pdf = io.BytesIO(pdf_bytes)
    fake_pdf.name = "sample_book.pdf"

    create_data = {
        "title": "Auto Preview Book",
        "description": "Book with automatic preview",
        "category": str(category.id),
        "price": "35.00",
        "status": "published",
    }
    files = {
        "book_file": ("sample_book.pdf", fake_pdf, "application/pdf"),
    }

    resp = client.post(
        "/api/Provider/products/create",
        data=create_data,
        files=files,
        headers=coach_headers,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()["data"]
    assert data["page_count"] == 4
    assert data["preview_page_count"] == 2
    assert data["preview_file"] is not None

    # Check the preview file on disk actually has 2 pages
    preview_url = data["preview_file"]
    rel_preview_path = preview_url.split("/media/", 1)[-1]
    disk_path = Path("media") / rel_preview_path
    assert disk_path.exists()
    reader = PdfReader(str(disk_path))
    assert len(reader.pages) == 2

