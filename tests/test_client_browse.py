from datetime import datetime, timedelta, timezone
import pytest
from starlette.testclient import TestClient
from sqlalchemy import select

from io import BytesIO
from pathlib import Path
from pypdf import PdfWriter, PdfReader
from pypdf.generic import DecodedStreamObject, NameObject, DictionaryObject
from src.main import app
from src.core.database import SessionLocal
from src.models.accounts.user import User
from src.models.client.product_purchase import ProductPurchase
from src.models.client.service_order import ServiceOrder
from src.models.provider.category import Category
from src.models.provider.coach_profile import CoachProfile
from src.models.provider.coach_profile.coach_availability import CoachAvailability
from src.models.provider.coach_profile.coach_review import CoachReview
from src.models.provider.blog.coach_blog import CoachBlog
from src.models.provider.product.coach_product import CoachProduct
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
    res1 = client.get("/user/user-category-list")
    assert res1.status_code in [400, 401, 403]
    res2 = client.get("/user/digital-product-list")
    assert res2.status_code in [400, 401, 403]
    res3 = client.get("/user/digital-product-detail/1")
    assert res3.status_code in [400, 401, 403]
    res4 = client.get("/user/digital-product-download/1")
    assert res4.status_code in [400, 401, 403]
    res5 = client.get("/user/blog-list")
    assert res5.status_code in [400, 401, 403]
    res6 = client.get("/user/blog-detail/1")
    assert res6.status_code in [400, 401, 403]
    res7 = client.get("/user/app-rating")
    assert res7.status_code in [400, 401, 403]
    res8 = client.post("/user/app-rating", json={"rating": 5, "review": "test"})
    assert res8.status_code in [400, 401, 403]
    res9 = client.get("/user/app-ratings-list")
    assert res9.status_code in [400, 401, 403]



def generate_sample_rich_pdf(file_path: Path):
    writer = PdfWriter()
    pages_data = [
        ("Interview Workbook - Page 1", ["Executive Preparation Guide", "Author: Sarah Chen", "Category: Business Coaching", "Preview Page 1 of 2"]),
        ("Interview Workbook - Page 2", ["Chapter 1: Strategy Frameworks", "STAR-L Method and Leadership Principles", "End of Preview - Purchase full book for Chapters 2-4"]),
        ("Interview Workbook - Page 3", ["Chapter 2: Strategic System Design", "Full Version Unlocked Content"]),
        ("Interview Workbook - Page 4", ["Chapter 3: Final Assessment", "Full Version Unlocked Content"]),
    ]
    for title, lines in pages_data:
        page = writer.add_blank_page(width=612, height=792)
        stream_cmds = ["BT", "/F1 20 Tf", "50 720 Td", f"({title}) Tj"]
        y = 670
        for line in lines:
            safe_line = line.replace("(", "[").replace(")", "]")
            stream_cmds.extend(["/F1 12 Tf", f"50 {y} Td", f"({safe_line}) Tj"])
            y -= 30
        stream_cmds.append("ET")

        content_stream = " ".join(stream_cmds).encode("latin1")
        stream_obj = DecodedStreamObject()
        stream_obj.set_data(content_stream)
        stream_ref = writer._add_object(stream_obj)
        page[NameObject("/Contents")] = stream_ref

        font_dict = DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        })
        font_ref = writer._add_object(font_dict)
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({
                NameObject("/F1"): font_ref
            })
        })
    with open(file_path, "wb") as f:
        writer.write(f)


@pytest.fixture
def seed_digital_product_data(db_session, seed_coach_data):
    profile = seed_coach_data["profile"]
    cat = profile.categories[0] if profile.categories else None

    # Generate a rich 4-page PDF file with actual text
    pdf_dir = Path("media/test_files")
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = pdf_dir / "test_4page_book.pdf"
    preview_path = pdf_dir / "test_4page_preview.pdf"

    generate_sample_rich_pdf(pdf_path)

    # Generate 2-page preview with real text
    reader = PdfReader(str(pdf_path))
    writer_prev = PdfWriter()
    writer_prev.add_page(reader.pages[0])
    writer_prev.add_page(reader.pages[1])
    with open(preview_path, "wb") as f:
        writer_prev.write(f)

    # Main product
    prod = db_session.execute(
        select(CoachProduct).where(
            CoachProduct.title == "Interview Workbook",
            CoachProduct.coach_profile_id == profile.id,
        )
    ).scalars().first()
    if not prod:
        prod = CoachProduct(
            coach_profile_id=profile.id,
            category_id=cat.id if cat else None,
            title="Interview Workbook",
            description="Practice questions",
            price="19.99",
            book_file=str(pdf_path).replace("\\", "/"),
            preview_file=str(preview_path).replace("\\", "/"),
            page_count=4,
            preview_page_count=2,
            status="published",
        )
        db_session.add(prod)
        db_session.commit()
        db_session.refresh(prod)
    else:
        prod.book_file = str(pdf_path).replace("\\", "/")
        prod.preview_file = str(preview_path).replace("\\", "/")
        prod.page_count = 4
        prod.preview_page_count = 2
        prod.status = "published"
        db_session.commit()
        db_session.refresh(prod)

    # Other product from same coach
    other_prod = db_session.execute(
        select(CoachProduct).where(
            CoachProduct.title == "Leadership Roadmap",
            CoachProduct.coach_profile_id == profile.id,
        )
    ).scalars().first()
    if not other_prod:
        other_prod = CoachProduct(
            coach_profile_id=profile.id,
            category_id=cat.id if cat else None,
            title="Leadership Roadmap",
            description="Step-by-step guide",
            price="29.99",
            status="published",
        )
        db_session.add(other_prod)
        db_session.commit()
        db_session.refresh(other_prod)
    else:
        other_prod.coach_profile_id = profile.id
        other_prod.status = "published"
        db_session.commit()
        db_session.refresh(other_prod)

    return {"product": prod, "other_product": other_prod, "pdf_path": pdf_path}


def test_digital_product_list(client, client_headers, seed_digital_product_data):
    prod = seed_digital_product_data["product"]
    res = client.get("/user/digital-product-list", headers=client_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["message"] == "Digital products retrieved successfully."
    assert len(data["data"]) > 0
    item = next(p for p in data["data"] if p["id"] == prod.id)
    assert item["title"] == "Interview Workbook"
    assert item["is_purchased"] is False
    assert item["book_file"] is None
    assert "coach" in item
    assert "category_details" in item


def test_digital_product_detail(client, client_headers, seed_digital_product_data):
    prod = seed_digital_product_data["product"]
    res = client.get(f"/user/digital-product-detail/{prod.id}", headers=client_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["message"] == "Digital product details retrieved successfully."
    assert data["data"]["id"] == prod.id
    assert data["data"]["is_purchased"] is False
    assert data["data"]["book_file"] is None
    assert "other_products" in data["data"]
    assert any(op["title"] == "Leadership Roadmap" for op in data["data"]["other_products"])


def test_digital_product_download_preview_and_purchased(
    client, client_user, client_headers, db_session, seed_digital_product_data
):
    prod = seed_digital_product_data["product"]

    # Ensure no existing purchase for client_user
    db_session.query(ProductPurchase).filter(
        ProductPurchase.user_id == client_user.id,
        ProductPurchase.product_id == prod.id,
    ).delete()
    db_session.commit()

    # 1. Unpurchased user -> 2-page preview
    res_preview = client.get(f"/user/digital-product-download/{prod.id}", headers=client_headers)
    assert res_preview.status_code == 200
    assert "receipt.pdf" in res_preview.headers.get("content-disposition", "")
    assert res_preview.headers.get("content-type") == "application/pdf"

    # Check page count of preview is min(2, total_pages) = 2
    reader_preview = PdfReader(BytesIO(res_preview.content))
    assert len(reader_preview.pages) == 2
    assert "Interview Workbook - Page 1" in reader_preview.pages[0].extract_text()
    assert "Interview Workbook - Page 2" in reader_preview.pages[1].extract_text()

    # 2. Add purchase record for client_user
    purchase = ProductPurchase(user_id=client_user.id, product_id=prod.id)
    db_session.add(purchase)
    db_session.commit()

    # 3. Purchased user -> full 4 pages
    res_full = client.get(f"/user/digital-product-download/{prod.id}", headers=client_headers)
    assert res_full.status_code == 200
    assert "receipt.pdf" in res_full.headers.get("content-disposition", "")
    reader_full = PdfReader(BytesIO(res_full.content))
    assert len(reader_full.pages) == 4
    assert "Interview Workbook - Page 1" in reader_full.pages[0].extract_text()
    assert "Interview Workbook - Page 4" in reader_full.pages[3].extract_text()

    # 4. Detail should now show is_purchased=True and book_file download link
    res_detail = client.get(f"/user/digital-product-detail/{prod.id}", headers=client_headers)
    assert res_detail.status_code == 200
    detail_data = res_detail.json()
    assert detail_data["data"]["is_purchased"] is True
    assert detail_data["data"]["book_file"] is not None

    # Clean up purchase
    db_session.delete(purchase)
    db_session.commit()


@pytest.fixture
def seed_blog_data(db_session, seed_coach_data):
    profile = seed_coach_data["profile"]
    cat = profile.categories[0] if profile.categories else None

    blog = db_session.execute(
        select(CoachBlog).where(
            CoachBlog.title == "Five habits of great founders",
            CoachBlog.coach_profile_id == profile.id,
        )
    ).scalars().first()
    if not blog:
        blog = CoachBlog(
            coach_profile_id=profile.id,
            category_id=cat.id if cat else None,
            title="Five habits of great founders",
            content="Long article text about the habits of great founders...",
            image="/media/coach/blogs/photo.gif",
            status="published",
        )
        db_session.add(blog)
        db_session.commit()
        db_session.refresh(blog)
    return {"blog": blog, "category": cat}


def test_user_blog_list(client, client_headers, seed_blog_data):
    blog = seed_blog_data["blog"]
    cat = seed_blog_data["category"]

    # 1. Without category filter
    res = client.get("/user/blog-list", headers=client_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["message"] == "Blogs retrieved successfully."
    assert isinstance(data["data"], list)
    item = next(b for b in data["data"] if b["id"] == blog.id)
    assert item["title"] == "Five habits of great founders"
    assert "coach" in item
    assert item["coach"]["headline"] == "Executive & Startup Coach"
    assert item["category_details"]["name"] == "Business"
    assert item["read_time_minutes"] >= 1
    assert item["status"] == "published"

    # 2. With category query param
    res_cat = client.get(f"/user/blog-list?category={cat.id}", headers=client_headers)
    assert res_cat.status_code == 200
    cat_data = res_cat.json()
    assert any(b["id"] == blog.id for b in cat_data["data"])
    assert all(b["category"] == cat.id for b in cat_data["data"])


def test_user_blog_detail(client, client_headers, seed_blog_data):
    blog = seed_blog_data["blog"]

    # 1. Successful detail retrieval
    res = client.get(f"/user/blog-detail/{blog.id}", headers=client_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["status"] == 200
    assert data["message"] == "Blog details retrieved successfully."
    blog_data = data["data"]
    assert blog_data["id"] == blog.id
    assert blog_data["title"] == blog.title
    assert blog_data["content"] == blog.content
    assert blog_data["status"] == "published"
    assert blog_data["read_time_minutes"] >= 1
    assert "coach" in blog_data
    assert blog_data["coach"]["headline"] == "Executive & Startup Coach"
    assert "category_details" in blog_data
    assert blog_data["category_details"]["name"] == "Business"

    # 2. Non-existent blog -> 404
    res_404 = client.get("/user/blog-detail/999999", headers=client_headers)
    assert res_404.status_code == 404


def test_app_ratings_flow(client, client_user, client_headers, db_session):
    from src.models.client.app_rating import AppRating

    # 1. Clean up any existing rating for client_user
    db_session.query(AppRating).filter(AppRating.user_id == client_user.id).delete()
    db_session.commit()

    # 2. Get initial stats -> has_rated=False, user_rating=None
    res_stats_init = client.get("/user/app-rating", headers=client_headers)
    assert res_stats_init.status_code == 200
    init_data = res_stats_init.json()
    assert init_data["success"] is True
    assert init_data["status"] == 200
    assert init_data["message"] == "App rating stats retrieved successfully."
    assert init_data["data"]["has_rated"] is False
    assert init_data["data"]["user_rating"] is None

    # 3. Submit app rating (POST)
    res_post = client.post(
        "/user/app-rating",
        json={"rating": 5, "review": "Great app!"},
        headers=client_headers,
    )
    assert res_post.status_code == 201
    post_data = res_post.json()
    assert post_data["success"] is True
    assert post_data["status"] == 201
    assert post_data["message"] == "App rating submitted successfully."
    rating_item = post_data["data"]
    assert rating_item["user"] == client_user.id
    assert rating_item["user_name"] == client_user.full_name
    assert rating_item["rating"] == 5
    assert rating_item["review"] == "Great app!"
    assert "created_at" in rating_item
    assert "updated_at" in rating_item

    # 4. Get stats after rating -> has_rated=True, user_rating=5, total_ratings >= 1
    res_stats_after = client.get("/user/app-rating", headers=client_headers)
    assert res_stats_after.status_code == 200
    after_data = res_stats_after.json()
    assert after_data["data"]["has_rated"] is True
    assert after_data["data"]["user_rating"] == 5
    assert after_data["data"]["total_ratings"] >= 1
    assert after_data["data"]["average_rating"] > 0

    # 5. Get ratings list -> contains this rating
    res_list = client.get("/user/app-ratings-list", headers=client_headers)
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert list_data["success"] is True
    assert list_data["status"] == 200
    assert list_data["message"] == "App ratings retrieved successfully."
    assert isinstance(list_data["data"], list)
    user_item = next(r for r in list_data["data"] if r["id"] == rating_item["id"])
    assert user_item["user"] == client_user.id
    assert user_item["user_name"] == client_user.full_name
    assert user_item["rating"] == 5
    assert user_item["review"] == "Great app!"
    assert "image" in user_item

    # 6. Update rating by posting again
    res_update = client.post(
        "/user/app-rating",
        json={"rating": 4, "review": "Updated review text"},
        headers=client_headers,
    )
    assert res_update.status_code == 201
    update_data = res_update.json()
    assert update_data["data"]["id"] == rating_item["id"]
    assert update_data["data"]["rating"] == 4
    assert update_data["data"]["review"] == "Updated review text"

    # Clean up
    db_session.query(AppRating).filter(AppRating.user_id == client_user.id).delete()
    db_session.commit()


def test_coach_availability_date_reflects_booked_and_past_slots(client, client_headers, client_user, seed_coach_data, db_session):
    prof_id = seed_coach_data["profile"].id
    coach_user_id = seed_coach_data["profile"].user_id

    # Compute a future Monday (seed coach is scheduled on weekday 0 = Monday)
    future_dt = datetime.now() + timedelta(days=7)
    while future_dt.weekday() != 0:
        future_dt += timedelta(days=1)
    future_date_str = future_dt.strftime("%Y-%m-%d")

    # Clean existing orders for this test profile
    db_session.query(ServiceOrder).filter(ServiceOrder.coach_profile_id == prof_id).delete()
    db_session.commit()

    # 1. Initially, future 14:00 (02:00 PM) slot should be available
    res1 = client.get(
        f"/user/coaches/{prof_id}/availability?date={future_date_str}",
        headers=client_headers,
    )
    assert res1.status_code == 200
    slots1 = res1.json()["data"]["slots"]
    slot_14 = next(s for s in slots1 if s["time"] == "14:00")
    assert slot_14["available"] is True

    # 2. Book an order at 02:00 PM (14:00) with a 60-min service
    order = ServiceOrder(
        user_id=client_user.id,
        coach_id=coach_user_id,
        coach_profile_id=prof_id,
        service_id=seed_coach_data["service"].id,
        order_type="service",
        booking_date=future_date_str,
        booking_time="02:00 PM",
        amount="160.00",
        total_amount="164.80",
        currency="USD",
        status="pending",
        payment_status="pending",
        payment_due_at=datetime.now(timezone.utc) + timedelta(minutes=15),
    )
    db_session.add(order)
    db_session.commit()

    # 3. Query availability again: 14:00 should now be unavailable (available=False)
    res2 = client.get(
        f"/user/coaches/{prof_id}/availability?date={future_date_str}",
        headers=client_headers,
    )
    assert res2.status_code == 200
    slots2 = res2.json()["data"]["slots"]
    slot_14_after = next(s for s in slots2 if s["time"] == "14:00")
    assert slot_14_after["available"] is False

    # 4. Simulate payment timeout by setting payment_due_at to the past
    order.payment_due_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    db_session.add(order)
    db_session.commit()

    # 5. Query availability again: slot should now be released (available=True)
    res3 = client.get(
        f"/user/coaches/{prof_id}/availability?date={future_date_str}",
        headers=client_headers,
    )
    assert res3.status_code == 200
    slots3 = res3.json()["data"]["slots"]
    slot_14_released = next(s for s in slots3 if s["time"] == "14:00")
    assert slot_14_released["available"] is True

    # Clean up
    db_session.query(ServiceOrder).filter(ServiceOrder.coach_profile_id == prof_id).delete()
    db_session.commit()


def test_coach_availability_month_reflects_past_and_fully_booked_days(
    client, client_headers, client_user, seed_coach_data, db_session
):
    prof_id = seed_coach_data["profile"].id
    coach_user_id = seed_coach_data["profile"].user_id
    today = datetime.now().date()
    month_str = today.strftime("%Y-%m")

    # Clean existing orders for this coach profile
    db_session.query(ServiceOrder).filter(ServiceOrder.coach_profile_id == prof_id).delete()
    db_session.commit()

    # 1. Query current month
    res = client.get(
        f"/user/coaches/{prof_id}/availability?month={month_str}",
        headers=client_headers,
    )
    assert res.status_code == 200
    avail_dates = res.json()["data"]["available_dates"]

    # All dates in available_dates must be >= today (no past dates)
    for d_str in avail_dates:
        d_val = datetime.strptime(d_str, "%Y-%m-%d").date()
        assert d_val >= today

    # 2. Pick a future date that is currently available in this month (e.g. next available Monday)
    future_avail_dates = [d for d in avail_dates if datetime.strptime(d, "%Y-%m-%d").date() > today]
    if future_avail_dates:
        target_date_str = future_avail_dates[0]

        # Query all slots on that target date
        res_date = client.get(
            f"/user/coaches/{prof_id}/availability?date={target_date_str}",
            headers=client_headers,
        )
        assert res_date.status_code == 200
        slots = res_date.json()["data"]["slots"]
        assert len(slots) > 0

        # Book ALL slots for that target date
        orders = []
        for slot in slots:
            time_obj = datetime.strptime(slot["time"], "%H:%M")
            time_ampm = time_obj.strftime("%I:%M %p")
            orders.append(
                ServiceOrder(
                    user_id=client_user.id,
                    coach_id=coach_user_id,
                    coach_profile_id=prof_id,
                    service_id=seed_coach_data["service"].id,
                    order_type="service",
                    booking_date=target_date_str,
                    booking_time=time_ampm,
                    amount="160.00",
                    total_amount="164.80",
                    currency="USD",
                    status="pending",
                    payment_status="pending",
                    payment_due_at=datetime.now(timezone.utc) + timedelta(minutes=15),
                )
            )
        db_session.add_all(orders)
        db_session.commit()

        # 3. Query month again: target_date_str must NOT be present in available_dates
        res2 = client.get(
            f"/user/coaches/{prof_id}/availability?month={month_str}",
            headers=client_headers,
        )
        assert res2.status_code == 200
        avail_dates_after = res2.json()["data"]["available_dates"]
        assert target_date_str not in avail_dates_after

        # 4. Clean up orders
        db_session.query(ServiceOrder).filter(ServiceOrder.coach_profile_id == prof_id).delete()
        db_session.commit()



