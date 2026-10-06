# Coach Hub Backend — System Architecture & Project Context

> **Quick AI Context Reference:**  
> This file is the primary context manual for AI agents and developers working on the **Coach Hub** backend. Read this file at the start of any conversation to understand the application domain, architecture, current implementation status, database schema, API contracts, known issues, and future roadmap.

---

## 1. Project Overview & Domain

**Coach Hub** is a backend API service designed to power a community-driven coaching platform (primary client: **Flutter mobile application**).  
The platform connects clients with specialized coaches across multiple disciplines (fitness, sports, life coaching, career, personal development).

### Key Core Features of the Platform:
- **Client & Coach Onboarding:** Multi-role user accounts (`USER`, `COACH`, `ADMIN`).
- **Authentication & Security:** OTP email verification, secure session management with JWT (access + refresh tokens), password reset, and profile management with media uploads.
- **Coach Discovery & Booking (Upcoming):** Coach profiles, hourly rates, slot scheduling, booking events/sessions.
- **Reviews & Feedback (Upcoming):** Rating and review system for coaches.

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
| **File Uploads** | `python-multipart` | Multipart form uploads for profile pictures |
| **Static Storage** | `FastAPI.staticfiles.StaticFiles` | Serving media assets stored under `/media` |
| **HTTP Client** | `httpx` | Async client for third-party integrations |
| **Testing** | `pytest`, `pytest-asyncio` | Unit & integration testing |

---

## 3. Architecture & Codebase Structure

The project follows a **Layered Clean Architecture** pattern ensuring separation of concerns:

```
D:\backend\coach/
├── alembic/                      # Database migration scripts
│   ├── versions/                 # Revision scripts (user, otp tables)
│   └── env.py                    # Alembic migration runner
├── media/                        # Static uploaded media files
│   └── profile_images/           # User profile picture storage
├── src/
│   ├── api/                      # Presentation Layer
│   │   ├── router.py             # Main API router aggregating feature routes
│   │   └── routes/
│   │       └── auth/             # Authentication & user profile endpoints
│   ├── core/                     # Infrastructure & Cross-Cutting Concerns
│   │   ├── config.py             # App settings (Pydantic BaseSettings from .env)
│   │   ├── database.py           # DB Engine, SessionLocal, Base, get_db dependency
│   │   ├── dependencies.py       # Auth dependencies (get_current_user, token parsing)
│   │   ├── exceptions.py         # Custom application exceptions (AppException subclasses)
│   │   └── common_responses.py   # Standardized API response models (CommonResponse, ErrorResponse)
│   ├── data/                     # In-memory mock/fallback data (legacy)
│   │   └── users.py
│   ├── models/                   # SQLAlchemy ORM Domain Models
│   │   └── accounts/
│   │       ├── user.py           # User model
│   │       └── otp.py            # OTPVerification model
│   ├── repository/               # Data Access Layer (SQLAlchemy queries)
│   │   └── auth/
│   │       ├── user_repository.py# User DB queries & mutations
│   │       └── otp_repository.py # OTP DB queries & mutations
│   ├── schemas/                  # Pydantic DTOs & Validation Schemas
│   │   └── auth/                 # Request & Response schemas
│   ├── service/                  # Business Logic Layer
│   │   └── auth/                 # Auth services (sign in, register, OTP, profile, etc.)
│   └── utils/                    # Shared Helper Functions
│       ├── jwt.py                # Token generation (access, refresh, password reset)
│       ├── otp_generation.py     # 6-digit numeric OTP generator & expiry
│       └── security.py           # Password hashing & verification with pwdlib
├── .env                          # Local environment variables
├── .gitignore                    # Git ignore file
├── alembic.ini                   # Alembic configuration
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

---

## 5. API Reference & Authentication Specification

All API routes are served under prefix: **`/api/auth`**

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
| Method | Endpoint | Auth Required | Description | Request Payload / Params |
|---|---|:---:|---|---|
| `POST` | `/api/auth/register/` | No | Register new user & dispatch OTP | `RegisterAccountRequest` (`full_name`, `email`, `role`, `phone`, `address`, `password`, `confirm_password`) |
| `POST` | `/api/auth/verify-email/` | No | Verify email OTP & issue JWT tokens | `VerifyEmailRequest` (`user_id`, `code`) |
| `POST` | `/api/auth/resend-verification-code/` | No | Resend OTP if previous is expired | `ResendOTPRequest` (`user_id`) |
| `POST` | `/api/auth/signin/` | No | Login with email & password | `SignInRequest` (`email`, `password`) |
| `POST` | `/api/auth/forgot-password/` | No | Send password reset OTP | `ForgotPasswordRequest` (`email`) |
| `POST` | `/api/auth/verify-reset-code/` | No | Verify reset OTP & get secret key | `VerifyResetCodeRequest` (`user_id`, `code`) |
| `POST` | `/api/auth/reset-password/` | No | Reset password using `secret_key` | `ResetPasswordRequest` (`secret_key`, `new_password`, `confirm_password`) |
| `PATCH`| `/api/auth/change-password/` | Yes (Bearer) | Change password for logged-in user | `ChangePasswordRequest` (`old_password`, `new_password`, `re_new_password` / `confirm_password`) |
| `GET` | `/api/auth/me` | Yes (Bearer) | Get authenticated user's profile | None |
| `PATCH`| `/api/auth/me` | Yes (Bearer) | Update profile data & upload avatar | Form fields: `full_name`, `phone_number` / `phone`, `address`, file: `image` / `photo` |
| `POST` | `/api/auth/refresh-token/` | No | Generate new access token | `RefreshTokenRequest` (`refresh_token`) |
| `POST` | `/api/auth/logout` | Yes (Bearer) | Log out authenticated user by validating refresh token | `LogoutRequest` (`refresh`) |
| `GET` | `/health` | No | Health check | None |
| `GET` | `/` | No | Root metadata & docs pointers | None |

---

## 6. Authentication & Security Flow

### 1. Registration & Email Verification
1. User calls `POST /api/auth/register/`.
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
2. **Verify Code:** `POST /api/auth/verify-reset-code/` with `user_id` + `code` -> Returns a dedicated, short-lived (5 min) `password_reset` JWT token (`secret_key`).
3. **Reset:** `POST /api/auth/reset-password/` with `secret_key` + `new_password` + `confirm_password` -> Verifies token type is `password_reset` and updates user password hash.

### 4. Token Headers & Dependency
`get_current_user` extracts tokens from:
- Standard `Authorization: Bearer <token>`
- Or fallback headers: `token: <token>` or `x-access-token: <token>`.
- Checks `user.is_active`.

---

## 7. Known Issues & Technical Debt (Immediate Fixes Needed)

When starting a new conversation or working on the backend, keep these specific known items in mind:

1. **`refresh_token.py` Uses In-Memory Mock List:**
   - **Issue:** `src/service/auth/refresh_token.py` imports `from src.data.users import users` (an empty list) instead of querying the database via `user_repository.get_user_by_id(db, user_id)`.
   - **Fix:** Pass `db: Session` from route to service and query the `User` model.

2. **`register.py` Ignores `address`:**
   - **Issue:** `RegisterAccountRequest` schema requires `address: str`, and `users` table has an `address` column, but `create_user` in `src/repository/auth/user_repository.py` and `register_user` in `src/service/auth/register.py` do not pass or save the address.
   - **Fix:** Update `create_user()` to accept and persist `address`.

3. **Hardcoded JWT Secret:**
   - **Issue:** `SECRET_KEY` in `src/utils/jwt.py` is hardcoded as a fallback string instead of loading from `settings` / `.env`.
   - **Fix:** Move `secret_key` into `Settings` in `src/core/config.py` and read from `.env`.

4. **Stubbed Email Delivery:**
   - **Issue:** `src/service/auth/email_service.py` prints the OTP to stdout console only.
   - **Fix:** Integrate real SMTP / transactional email provider (Resend, SendGrid, Mailgun, or AWS SES).

5. **Legacy Template Artifacts:**
   - **Issue:** `src/main.py` and `src/core/config.py` contain commented-out remnants from an earlier template (crop disease, irrigation, fertilizer ML models).
   - **Fix:** Clean up unused commented lines to maintain clean codebase standards.

---

## 8. Planned Roadmap & Upcoming Modules

1. **Coach Domain & Profiles:**
   - Coach specialized profile schema: categories, biography, years of experience, hourly rate, certificates/credentials, location, languages spoken.
   - Coach verification / approval workflow (`coach_status`: `PENDING`, `APPROVED`, `REJECTED`).
2. **Availability & Scheduling:**
   - Coach calendar availability slots (day of week, start time, end time, recurring vs one-off).
3. **Bookings & Sessions:**
   - Booking requests, accept/decline flows, session cancellation and rescheduling.
   - Status tracking (`PENDING`, `CONFIRMED`, `COMPLETED`, `CANCELLED`).
4. **Reviews & Ratings:**
   - Clients leaving star ratings and textual reviews after completed sessions.
   - Aggregated coach rating scores and review listings.
5. **Real-Time Notifications & Chat:**
   - WebSockets or push notifications for session updates and in-app messaging between coach and client.

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

### 4. Interactive API Docs
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
