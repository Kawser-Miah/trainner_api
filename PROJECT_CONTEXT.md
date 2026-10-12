# Coach Hub Backend — System Architecture & Project Context

> **Quick AI Context Reference:**  
> This file is the primary context manual for AI agents and developers working on the **Coach Hub** backend. Read this file at the start of any conversation to understand the application domain, architecture, current implementation status, database schema, API contracts, known issues, and future roadmap.

---

## 1. Project Overview & Domain

**Coach Hub** is a backend API service designed to power a community-driven coaching platform (primary client: **Flutter mobile application**).  
The platform connects clients with specialized coaches across multiple disciplines (fitness, sports, life coaching, career, personal development, business coaching).

### Key Core Features of the Platform:
- **Client & Coach Onboarding:** Multi-role user accounts (`USER`, `COACH`, `ADMIN` / `Provider`).
- **Authentication & Security:** OTP email verification, secure session management with JWT (access + refresh tokens), password reset, and profile management with media uploads.
- **Coach Discovery & Profile:** Comprehensive coach profiles, video introductions (with auto-calculated duration and thumbnails), availability scheduling, and ratings/reviews.
- **Coach Services:** 1-on-1 and group coaching service offerings with flexible pricing, benefits, and session management.
- **Coach Blogs:** Rich coaching articles/blog posts with featured images, category categorization, and draft/published status filtering.
- **Coach Digital Products:** Downloadable digital books/workbooks (e.g. PDFs) with cover thumbnails, automated file type detection, and secure download URLs.

---

## 2. Technology Stack & Key Dependencies

| Component | Technology / Library | Purpose |
|---|---|---|
| **Language** | Python 3.12+ / 3.14 | Core backend language |
| **Framework** | FastAPI (`fastapi`) | Async RESTful API framework |
| **ASGI Server** | Uvicorn (`uvicorn[standard]`) | High-performance ASGI server |
| **Database ORM** | SQLAlchemy 2.0+ (`sqlalchemy`) | Typed ORM models (`Mapped`, `mapped_column`) |
| **Database Driver** | PostgreSQL (`psycopg2-binary`) | Postgres database adapter |
| **Migrations** | Alembic (`alembic`) | Database schema version control |
| **Validation / Settings** | Pydantic v2 & `pydantic-settings` | Request/Response schema validation & `.env` configuration |
| **Security & JWT** | `python-jose[cryptography]`, `pwdlib[bcrypt]`, `bcrypt` | JWT token issuing/verifying & password hashing |
| **File Uploads** | `python-multipart` | Multipart form uploads for profile pictures, videos, blog images, and product files |
| **Static Storage** | `FastAPI.staticfiles.StaticFiles` | Serving media assets stored under `/media` |
| **HTTP Client** | `httpx` | Async client for integrations and testing |
| **Testing** | `pytest`, `pytest-asyncio` | Unit & integration testing with Starlette TestClient |

---

## 3. Architecture & Codebase Structure

The project follows a **Layered Clean Architecture** pattern ensuring separation of concerns:

```
D:\backend\coach/
├── alembic/                      # Database migration scripts
│   ├── versions/                 # Revision scripts (users, coach_profiles, services, blogs, products)
│   └── env.py                    # Alembic migration runner
├── media/                        # Static uploaded media files
│   ├── profile_images/           # User profile picture storage
│   └── coach/                    # Coach assets
│       ├── profile/              # Coach profile pictures
│       ├── videos/thumbnails/    # Extracted video cover frames
│       ├── certificates/         # Coach certificates documents
│       ├── qualifications/       # Coach qualification documents
│       ├── blogs/                # Coach blog post featured images
│       └── products/             # Digital product covers & files
│           └── files/            # Uploaded PDF/workbook download files
├── src/
│   ├── api/                      # Presentation Layer
│   │   ├── router.py             # Main API router aggregating feature routes
│   │   └── routes/
│   │       ├── auth/             # Authentication & user profile endpoints
│   │       └── provider/         # Provider coaching endpoints
│   │           ├── coach_profile/# Profile onboarding & updates
│   │           ├── service/      # Coach services CRUD
│   │           ├── blog/         # Coach blogs CRUD
│   │           └── product/      # Coach digital products CRUD & download
│   ├── core/                     # Infrastructure & Cross-Cutting Concerns
│   │   ├── config.py             # App settings (Pydantic BaseSettings from .env)
│   │   ├── database.py           # DB Engine, SessionLocal, Base, get_db dependency
│   │   ├── dependencies.py       # Auth dependencies (get_current_user, require_approved_coach)
│   │   ├── exceptions.py         # Custom application exceptions (AppException subclasses)
│   │   └── common_responses.py   # Standardized API response models (CommonResponse, ErrorResponse)
│   ├── models/                   # SQLAlchemy ORM Domain Models
│   │   ├── accounts/             # User, OTPVerification models
│   │   └── provider/             # Provider domain models
│   │       ├── category.py       # Category model
│   │       ├── coach_profile/    # CoachProfile, Certifications, Qualifications, Availability, Reviews
│   │       ├── service/          # CoachService, CoachServiceBenefit
│   │       ├── blog/             # CoachBlog
│   │       └── product/          # CoachProduct
│   ├── repository/               # Data Access Layer (SQLAlchemy queries)
│   │   ├── auth/                 # User & OTP queries
│   │   └── provider/             # Provider domain repositories
│   │       ├── category_repository.py
│   │       ├── coach_profile/    # Profile, availability, reviews repositories
│   │       ├── service/          # Coach service repository
│   │       ├── blog/             # Coach blog repository
│   │       └── product/          # Coach product repository
│   ├── schemas/                  # Pydantic DTOs & Validation Schemas
│   │   ├── auth/                 # Auth DTOs (sign in, register, OTP, passwords)
│   │   └── provider/             # Coach DTOs
│   │       ├── coach_profile/    # Profile, availability, reviews schemas
│   │       ├── service/          # Services request & response schemas
│   │       ├── blog/             # Blogs request & response schemas
│   │       └── product/          # Products request & response schemas
│   ├── service/                  # Business Logic Layer
│   │   ├── auth/                 # Auth services (sign in, register, OTP, profile, etc.)
│   │   └── provider/             # Provider services
│   │       ├── coach_profile/    # Coach profile, video processing, availability, reviews
│   │       ├── service/          # Service creation, update, filtering
│   │       ├── blog/             # Blog creation, image storage, filtering
│   │       └── product/          # Product creation, file storage, download handling
│   └── utils/                    # Shared Helper Functions
│       ├── jwt.py                # Token generation (access, refresh, password reset)
│       ├── media.py              # Centralized base URL & media URL generator
│       ├── otp_generation.py     # 6-digit numeric OTP generator & expiry
│       └── security.py           # Password hashing & verification with pwdlib
├── tests/                        # Comprehensive pytest test suite
│   ├── test_access_control.py
│   ├── test_blogs_api.py
│   ├── test_provider_availability.py
│   ├── test_provider_blogs.py
│   ├── test_provider_products.py
│   ├── test_provider_profile.py
│   ├── test_provider_reviews.py
│   └── test_provider_services.py
├── .env                          # Local environment variables
├── .gitignore                    # Git ignore file
├── alembic.ini                   # Alembic configuration
├── generate_postman_collection.py# Generator script for Postman collection
├── Personal_Project.postman_collection.json # 1:1 API Postman collection
├── requirements.txt              # Project dependencies
├── run.py                        # Entry point CLI runner
└── PROJECT_CONTEXT.md            # This project context document
```

---

## 4. Database Models & Schema

### 4.1. `users` Table
| Column | Type | Constraints / Defaults | Description |
|---|---|---|---|
| `id` | `Integer` | PK, autoincrement | Unique user identifier |
| `full_name` | `String(100)` | NOT NULL | User's full display name |
| `email` | `String(255)` | NOT NULL, UNIQUE, Indexed | User login email |
| `phone` | `String(20)` | Nullable | User phone number |
| `photo_url` | `String(500)` | Nullable | URL path to uploaded profile image |
| `address` | `String(150)` | Nullable | Physical location / address |
| `password_hash`| `String(255)` | NOT NULL | Hashed password |
| `role` | `String(20)` | NOT NULL, Default: `'USER'` | Account role: `USER`, `COACH`, `ADMIN` |
| `coach_status` | `String(20)` | NOT NULL, Default: `'pending'` | Coach verification status: `pending`, `approved`, `rejected` |
| `is_email_verified`| `Boolean` | NOT NULL, Default: `False` | True once OTP is confirmed |
| `is_completed`| `Boolean` | NOT NULL, Default: `False` | Indicates if profile onboarding is complete |
| `is_active` | `Boolean` | NOT NULL, Default: `True` | Account active status |
| `created_at` | `DateTime(tz)`| NOT NULL, Default: UTC now | Account creation timestamp |
| `updated_at` | `DateTime(tz)`| NOT NULL, Default: UTC now | Last update timestamp |

### 4.2. `otp_verifications` Table
| Column | Type | Constraints / Defaults | Description |
|---|---|---|---|
| `id` | `Integer` | PK, autoincrement | OTP record ID |
| `user_id` | `Integer` | FK (`users.id`, ondelete `CASCADE`), UNIQUE | One active OTP record per user |
| `otp_code` | `String(6)` | NOT NULL | 6-digit verification code |
| `expires_at` | `DateTime(tz)`| NOT NULL | Expiry timestamp (typically 2 minutes) |

### 4.3. Profile & Service Tables
- **`categories`**: `id` (PK), `name` (unique, indexed), `description`, `is_active`, `image`, timestamps.
- **`coach_profiles`**: `id` (PK), `user_id` (FK `users.id`, UNIQUE), `headline`, `about`, `introduction_video`, `introduction_video_duration`, `introduction_video_thumbnail`, `linkedin_url`, `affiliate_commission_percent`, `auto_approve_affiliates`, `expertises` (JSON), `languages` (JSON), `is_completed`, `status` ('pending', 'approved'), `rejection_reason`, `avg_rating`, `total_reviews`, `completed_sessions_count`, `success_rate`, timestamps.
- **`coach_profile_categories`**: `id` (PK), `coach_profile_id` (FK), `category_id` (FK).
- **`coach_certifications`**: `id` (PK), `coach_profile_id` (FK), `name`, `document`, `created_at`.
- **`coach_qualifications`**: `id` (PK), `coach_profile_id` (FK), `name`, `document`, `created_at`.
- **`coach_availabilities`**: `id` (PK), `coach_profile_id` (FK), `day_of_week` (0-6), `start_time`, `end_time`, `is_active`, timestamps.
- **`coach_reviews`**: `id` (PK), `coach_profile_id` (FK), `user_id` (FK `users.id`), `rating`, `review_text`, timestamps.
- **`coach_services`**: `id` (PK), `coach_profile_id` (FK), `category_id` (FK), `title`, `description`, `service_type`, `session_format`, `session_duration`, `currency`, `price`, `booking_type`, `who_is_this_service_for`, `preparation_instructions`, `cancellation_policy`, `session_url`, `status`, `bookings_count`, `revenue`, `created_at`, `updated_at`.
- **`coach_service_benefits`**: `id` (PK), `service_id` (FK `coach_services.id`, CASCADE), `outcome`, `created_at`.

### 4.4. `coach_blogs` Table
| Column | Type | Constraints / Defaults | Description |
|---|---|---|---|
| `id` | `Integer` | PK, autoincrement | Blog post ID |
| `coach_profile_id` | `Integer` | FK (`coach_profiles.id`, CASCADE), Indexed | Associated coach profile |
| `category_id` | `Integer` | FK (`categories.id`, RESTRICT), Indexed | Blog category |
| `title` | `String(255)` | NOT NULL | Article title |
| `content` | `Text` | NOT NULL | Full article body text |
| `image` | `String(500)` | Nullable | Featured image media path |
| `status` | `String(50)` | NOT NULL, Default: `'published'` | Post status (`published`, `draft`) |
| `created_at` | `DateTime(tz)`| NOT NULL, Default: UTC now | Creation timestamp |
| `updated_at` | `DateTime(tz)`| NOT NULL, Default: UTC now | Last update timestamp |

### 4.5. `coach_products` Table
| Column | Type | Constraints / Defaults | Description |
|---|---|---|---|
| `id` | `Integer` | PK, autoincrement | Product ID |
| `coach_profile_id` | `Integer` | FK (`coach_profiles.id`, CASCADE), Indexed | Associated coach profile |
| `category_id` | `Integer` | FK (`categories.id`, RESTRICT), Indexed | Product category |
| `title` | `String(255)` | NOT NULL | Product title |
| `description` | `Text` | Nullable | Product description |
| `thumbnail` | `String(500)` | Nullable | Cover thumbnail image path |
| `book_file` | `String(500)` | Nullable | Uploaded digital document path |
| `preview_file` | `String(500)` | Nullable | Optional preview file path |
| `page_count` | `Integer` | Nullable | Total page count |
| `preview_page_count` | `Integer` | Nullable | Preview page count |
| `file_type` | `String(50)` | Nullable | Detected file format (e.g. `'PDF'`) |
| `price` | `String(50)` | NOT NULL, Default: `'0.00'` | Formatted price string (e.g. `'19.00'`) |
| `status` | `String(50)` | NOT NULL, Default: `'published'` | Status (`published`, `draft`) |
| `sales_count` | `Integer` | NOT NULL, Default: `0` | Total sales count |
| `revenue` | `String(50)` | NOT NULL, Default: `'0.00'` | Accumulated revenue |
| `created_at` | `DateTime(tz)`| NOT NULL, Default: UTC now | Creation timestamp |
| `updated_at` | `DateTime(tz)`| NOT NULL, Default: UTC now | Last update timestamp |

---

## 5. API Reference & Authentication Specification

All API routes are served under prefix: **`/api/auth`** and **`/Provider`** (both `/Provider` and `/api/Provider` are supported).

### Standard Identity Rule
> **Important Identity Architectural Rule:**  
> In all provider responses (Services, Blogs, Products), the `coach` field must return the **central user ID** (`user.id`), not the internal `coach_profile_id`. The user identity across the application is strictly `user.id`.

### Standard Response Envelope
All endpoints return standard envelopes:
```json
// Success Response (CommonResponse)
{
  "success": true,
  "code": 200,
  "status": 200,
  "message": "Operation description",
  "data": { ... }
}

// Error Response (ErrorResponse)
{
  "success": false,
  "code": 400,
  "status": 400,
  "message": "Human readable error description",
  "error": "ERROR_CODE_STRING"
}
```

### Endpoints Matrix

#### 1. Authentication (`/api/auth`)
| Method | Endpoint | Auth Required | Role Required | Description | Request Payload / Params |
|---|---|:---:|:---:|---|---|
| `POST` | `/api/auth/register/` | No | Any | Register new user & dispatch OTP | `RegisterAccountRequest` (`full_name`, `email`, `role`, `phone`, `address`, `password`, `confirm_password` / `re_password`) |
| `POST` | `/api/auth/verify-email/` | No | Any | Verify email OTP & issue JWT tokens | `VerifyEmailRequest` (`user_id`, `code`) |
| `POST` | `/api/auth/resend-verification-code/` | No | Any | Resend OTP if previous is expired | `ResendOTPRequest` (`user_id`) |
| `POST` | `/api/auth/signin/` | No | Any | Login with email & password | `SignInRequest` (`email`, `password`) |
| `POST` | `/api/auth/forgot-password/` | No | Any | Send password reset OTP | `ForgotPasswordRequest` (`email`) |
| `POST` | `/api/auth/verify-reset-code/` | No | Any | Verify reset OTP & get secret key | `VerifyResetCodeRequest` (`user_id`, `code`) |
| `POST` | `/api/auth/reset-password/` | No | Any | Reset password using `secret_key` | `ResetPasswordRequest` (`secret_key`, `new_password`, `confirm_password`) |
| `PATCH`| `/api/auth/change-password/` | Yes (Bearer) | Any | Change password for logged-in user | `ChangePasswordRequest` (`old_password`, `new_password`, `re_new_password` / `confirm_password`) |
| `GET` | `/api/auth/me` | Yes (Bearer) | Any | Get authenticated user's profile | None |
| `PATCH`| `/api/auth/me` | Yes (Bearer) | Any | Update profile data & upload avatar | Form fields: `full_name`, `phone_number` / `phone`, `address`, file: `image` / `photo` |
| `POST` | `/api/auth/refresh-token/` | No | Any | Generate new access token | `RefreshTokenRequest` (`refresh_token`) |
| `POST` | `/api/auth/logout` | Yes (Bearer) | Any | Log out authenticated user | `LogoutRequest` (`refresh`) |
| `DELETE`| `/api/auth/delete-account`| Yes (Bearer) | Any | Delete user account | None |

#### 2. Provider Profile & Management (`/Provider` / `/api/Provider`)
| Method | Endpoint | Auth Required | Role Required | Description | Request Payload / Params |
|---|---|:---:|:---:|---|---|
| `GET` | `/Provider/coach-profile` | Yes (Bearer) | Any Authenticated | Retrieve authenticated coach's profile directly from DB | None |
| `POST` | `/Provider/coach-profile` | Yes (Bearer) | Any Authenticated | Create coach profile with multipart data (video duration auto-extracted) | Multipart form fields: file `introvideo`, profile fields |
| `PATCH`| `/Provider/coach-profile` | Yes (Bearer) | Any Authenticated | Update coach profile | Multipart form fields & files |
| `GET` | `/Provider/coach-availability` | Yes (Bearer) | Approved Coach | Retrieve coach availability schedule | None |
| `PUT` | `/Provider/coach-availability` | Yes (Bearer) | Approved Coach | Update coach availability schedule | `UpdateCoachAvailabilityRequest` |
| `GET` | `/Provider/reviews` | Yes (Bearer) | Approved Coach | Retrieve coach reviews and ratings | None |
| `GET` | `/Provider/categories-list/` | No | Any | Retrieve list of coaching categories | Query param: optional `is_active` |

#### 3. Coach - Services (`/Provider/services`)
| Method | Endpoint | Auth Required | Role Required | Description | Request Payload / Params |
|---|---|:---:|:---:|---|---|
| `POST` | `/Provider/services/create` | Yes (Bearer) | Approved Coach | Create coach service offering | `CreateCoachServiceRequest` (`title`, `category`, `description`, `price`, `benefits`, etc.) |
| `GET` | `/Provider/services/list` | Yes (Bearer) | Approved Coach | List coach services | Query param: `status` |
| `GET` | `/Provider/services/{id}` | Yes (Bearer) | Approved Coach | Retrieve details of specific service | Path param: `service_id` |
| `PATCH`| `/Provider/services/{id}` | Yes (Bearer) | Approved Coach | Update a specific service | `UpdateCoachServiceRequest` |
| `DELETE`| `/Provider/services/{id}` | Yes (Bearer) | Approved Coach | Delete a specific service | Path param: `service_id` |

#### 4. Coach - Blogs (`/Provider/blogs`)
| Method | Endpoint | Auth Required | Role Required | Description | Request Payload / Params |
|---|---|:---:|:---:|---|---|
| `POST` | `/Provider/blogs/create` | Yes (Bearer) | Approved Coach | Create blog post (multipart/form-data) | Form fields: `title`, `category`, `content`, `status`, file: `image` |
| `GET` | `/Provider/blogs/list` | Yes (Bearer) | Approved Coach | List coach blogs | Query param: `status` (aliases: `/Provider/blogs`, `/Provider/blogs/create`) |
| `GET` | `/Provider/blogs/{id}` | Yes (Bearer) | Approved Coach | Retrieve blog post detail | Path param: `blog_id` |
| `PATCH`| `/Provider/blogs/{id}` | Yes (Bearer) | Approved Coach | Update blog post | Form fields: `title`, `category`, `content`, `status`, file: `image` |
| `DELETE`| `/Provider/blogs/{id}` | Yes (Bearer) | Approved Coach | Delete blog post | Path param: `blog_id` |

#### 5. Coach - Products (`/Provider/products` & `/Provider/products-list`)
| Method | Endpoint | Auth Required | Role Required | Description | Request Payload / Params |
|---|---|:---:|:---:|---|---|
| `POST` | `/Provider/products/create` | Yes (Bearer) | Approved Coach | Create digital product (multipart/form-data) | Form fields: `title`, `description`, `category`, `price`, `status`, files: `Thumbnail`, `book_file`, optional `preview_file` |
| `GET` | `/Provider/products-list` | Yes (Bearer) | Approved Coach | List digital products (alias `/Provider/products`) | Query param: `status` |
| `GET` | `/Provider/products/{id}` | Yes (Bearer) | Approved Coach | Retrieve product detail | Path param: `product_id` |
| `PATCH`| `/Provider/products/{id}` | Yes (Bearer) | Approved Coach | Update digital product | Form fields: `title`, `description`, `category`, `price`, `status`, files: `Thumbnail`, `book_file` |
| `DELETE`| `/Provider/products/{id}` | Yes (Bearer) | Approved Coach | Delete digital product | Path param: `product_id` |
| `GET` | `/api/v1/user/digital-product-download/{id}/` | No | Any | Download digital book file | Path param: `product_id` |

#### 6. Client - Browse (`/user`)
| Method | Endpoint | Auth Required | Role Required | Description | Request Payload / Params |
|---|---|:---:|:---:|---|---|
| `GET` | `/user/user-category-list` | Yes (Bearer) | Client (`USER`) | List active categories for clients | None |
| `GET` | `/user/coach-profile-list` | Yes (Bearer) | Client (`USER`) | List approved coaches | Query: `search`, `category`, `ordering` |
| `GET` | `/user/recommended-coach-profile-list` | Yes (Bearer) | Client (`USER`) | List recommended coaches | None |
| `GET` | `/user/coach-profile/{coach_profile_id}` | Yes (Bearer) | Client (`USER`) | Get coach profile details with services, products, blogs | Path: `coach_profile_id` |
| `GET` | `/user/coaches/{coach_profile_id}/availability` | Yes (Bearer) | Client (`USER`) | Get coach time slots by date or available dates by month | Query: `date` or `month`, `service_id` |
| `GET` | `/user/coaches/{coach_profile_id}/reviews` | Yes (Bearer) | Client (`USER`) | Get coach reviews and breakdown | Path: `coach_profile_id` |
| `GET` | `/user/user-service-list` | Yes (Bearer) | Client (`USER`) | List published coach services | Query: `search`, `coach_profile`, `category` |
| `GET` | `/user/user-service-detail/{service_id}` | Yes (Bearer) | Client (`USER`) | Get service detail and other coach sessions | Path: `service_id` |

---

## 6. Authentication & Security Flow

### 1. Registration & Email Verification
1. User calls `POST /api/auth/register/` (supports `role: "Provider"` or `"COACH"`, saves `address`, `phone`, etc.).
2. Validates password confirmation and verifies email uniqueness.
3. Generates 6-digit OTP (expires in 2 minutes) and saves to `otp_verifications` with upsert logic (`create_or_update_otp`).
4. Logs/sends OTP to user email.
5. User calls `POST /api/auth/verify-email/` with `user_id` and `code`.
6. On success: `is_email_verified` is set to `True`, OTP record is removed, and JWT tokens (`access_token`, `refresh_token`) are returned.

### 2. Sign In
1. User sends `email` + `password`.
2. Verifies password hash using `pwdlib`.
3. Verifies `is_email_verified` is `True` and `is_active` is `True`.
4. Returns access token (valid 30 minutes) and refresh token (valid 15 days).

### 3. Password Reset Flow (3 Steps)
1. **Initiate:** `POST /api/auth/forgot-password/` with `email` -> OTP generated and sent.
2. **Verify Code:** `POST /api/auth/verify-reset-code/` with `user_id` + `code` -> Returns dedicated, short-lived (5 min) `password_reset` JWT token (`secret_key`).
3. **Reset:** `POST /api/auth/reset-password/` with `secret_key` + `new_password` + `confirm_password` -> Verifies token type is `password_reset` and updates user password hash.

### 4. Token Headers & Dependency
`get_current_user` extracts tokens from:
- Standard `Authorization: Bearer <token>`
- Or fallback headers: `token: <token>` or `x-access-token: <token>`.
- Checks `user.is_active`.
- `require_approved_coach` ensures `user.role in ["COACH", "Provider"]` and `user.coach_status == "approved"`.

---

## 7. Postman Collection Architecture

The Postman collection is maintained via [generate_postman_collection.py](file:///d:/backend/coach/generate_postman_collection.py) and exported as [Personal_Project.postman_collection.json](file:///d:/backend/coach/Personal_Project.postman_collection.json).

It is structured into distinct top-level folders:
1. **Authentication:** Register, Verify Email, Resend OTP, Sign In, Refresh Token, Me, Change Password, Forgot Password, Verify Reset Code, Reset Password, Logout, Delete Account.
2. **Provider Profile:** Coach Profile (GET, POST, PATCH), Availability (GET, PUT), Reviews (GET).
3. **Coach - Services:** Create Service, List Services, Service Detail, Update Service, Delete Service.
4. **Coach - Blogs:** Create Blog, List Blogs, Blog Detail, Update Blog, Delete Blog.
5. **Coach - Products:** Create Product, List Products, Product Detail, Update Product, Delete Product.

Variables configured:
- `base_url`: `http://localhost:8000`
- `access_token`, `refresh_token`, `user_id`, `secret_key`
- `category_id`, `service_id`, `service_to_delete_id`
- `blog_id`, `blog_to_delete_id`
- `product_id`, `product_to_delete_id`

---

## 8. Known Issues & Technical Debt

1. **`refresh_token.py` In-Memory Mock:**
   - `src/service/auth/refresh_token.py` imports `from src.data.users import users` instead of querying the database via `user_repository.get_user_by_id(db, user_id)`.
2. **Hardcoded JWT Secret Fallback:**
   - `SECRET_KEY` in `src/utils/jwt.py` has a hardcoded default fallback string instead of strictly requiring it from `settings` / `.env`.
3. **Stubbed Email Delivery:**
   - `src/service/auth/email_service.py` prints the OTP to console. Integrate real SMTP / transactional email provider for production.

---

## 9. Developer Quickstart & Common Commands

### 1. Environment & Dependencies
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 2. Database Migrations
```powershell
# Run pending migrations
alembic upgrade head

# Generate a new migration
alembic revision --autogenerate -m "describe migration"
```

### 3. Running the Server
```powershell
# Run with auto-reload (development mode)
python run.py --reload

# Or directly with uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Running Tests
```powershell
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/test_provider_products.py
```

### 5. Interactive API Docs
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
