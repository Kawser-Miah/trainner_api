from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any
import uuid

from fastapi import Request, UploadFile
from sqlalchemy.orm import Session

from src.core.exceptions import AppException, CoachProfileNotFoundException
from src.models.accounts.user import User
from src.models.provider.coach_profile import CoachProfile
from src.repository.provider.category_repository import (
    get_categories_by_ids,
    get_or_create_default_categories,
)
from src.repository.provider.coach_profile_repository import (
    create_coach_profile,
    get_coach_profile_by_user_id,
    replace_certifications,
    replace_qualifications,
    set_coach_categories,
)
from src.schemas.provider.coach_profile import (
    CoachCategoryResponse,
    CoachCertificationResponse,
    CoachProfileDataResponse,
    CoachQualificationResponse,
    CoachUserSummaryResponse,
)
from src.utils.media import build_media_url


def format_duration(seconds: int | None) -> str:
    if not seconds or seconds <= 0:
        return "0:00"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_dt(dt: datetime | None) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


async def save_uploaded_file(file: Any, subfolder: str) -> str | None:
    if file is None:
        return None
    if not hasattr(file, "filename") or not hasattr(file, "read"):
        return None
    if not getattr(file, "filename", None):
        return None

    content = await file.read()
    if not content or len(content) == 0:
        return None

    ext = Path(file.filename).suffix or ".bin"
    clean_stem = re.sub(r"[^\w\-]", "_", Path(file.filename).stem)
    unique_name = f"{clean_stem}_{uuid.uuid4().hex[:8]}{ext}"

    dest_dir = Path("media") / "coach" / subfolder
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / unique_name

    with open(dest_path, "wb") as f:
        f.write(content)

    return f"/media/coach/{subfolder}/{unique_name}"


def parse_category_ids(raw_val: Any) -> list[int]:
    if not raw_val:
        return []
    if isinstance(raw_val, list):
        ids = []
        for x in raw_val:
            ids.extend(parse_category_ids(x))
        return ids

    str_val = str(raw_val).strip()
    if str_val.startswith("[") and str_val.endswith("]"):
        try:
            parsed = json.loads(str_val)
            if isinstance(parsed, list):
                return [int(x) for x in parsed if str(x).isdigit()]
        except Exception:
            pass

    return [int(x.strip()) for x in str_val.split(",") if x.strip().isdigit()]


def parse_list_of_strings(raw_val: Any) -> list[str]:
    if not raw_val:
        return []
    if isinstance(raw_val, list):
        return [str(x).strip() for x in raw_val if str(x).strip()]

    str_val = str(raw_val).strip()
    if str_val.startswith("[") and str_val.endswith("]"):
        try:
            parsed = json.loads(str_val)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except Exception:
            pass

    return [x.strip() for x in str_val.split(",") if x.strip()]


def to_profile_data_response(
    profile: CoachProfile,
    user: User,
    request: Request | None = None,
) -> CoachProfileDataResponse:
    categories_resp = [
        CoachCategoryResponse(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            is_active=cat.is_active,
            image=build_media_url(cat.image, request),
        )
        for cat in (profile.categories or [])
    ]

    certifications_resp = [
        CoachCertificationResponse(
            id=cert.id,
            name=cert.name,
            document=build_media_url(cert.document, request),
            created_at=format_dt(cert.created_at),
        )
        for cert in (profile.certifications or [])
    ]

    qualifications_resp = [
        CoachQualificationResponse(
            id=qual.id,
            name=qual.name,
            document=build_media_url(qual.document, request),
            created_at=format_dt(qual.created_at),
        )
        for qual in (profile.qualifications or [])
    ]

    user_summary = CoachUserSummaryResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone or "",
        address=getattr(user, "address", None),
    )

    duration = profile.introduction_video_duration or 0

    return CoachProfileDataResponse(
        id=profile.id,
        user=user_summary,
        profile_photo=build_media_url(profile.profile_photo, request),
        headline=profile.headline,
        about=profile.about,
        categories=categories_resp,
        certifications=certifications_resp,
        qualifications=qualifications_resp,
        introduction_video=build_media_url(profile.introduction_video, request),
        introduction_video_duration=duration,
        introduction_video_duration_display=format_duration(duration),
        introduction_video_thumbnail=build_media_url(
            profile.introduction_video_thumbnail, request
        ),
        linkedin_url=profile.linkedin_url,
        affiliate_commission_percent=profile.affiliate_commission_percent or "20.00",
        auto_approve_affiliates=profile.auto_approve_affiliates,
        expertises=profile.expertises or [],
        languages=profile.languages or [],
        is_completed=profile.is_completed,
        status=profile.status or "pending",
        rejection_reason=profile.rejection_reason or "",
        avg_rating=profile.avg_rating or 0.0,
        total_reviews=profile.total_reviews or 0,
        completed_sessions_count=profile.completed_sessions_count or 0,
        success_rate=profile.success_rate,
        created_at=format_dt(profile.created_at),
        updated_at=format_dt(profile.updated_at),
    )


async def parse_coach_form_data(request: Request) -> dict[str, Any]:
    form = await request.form()

    # Extract single text fields
    about = form.get("about")
    headline = form.get("headline")
    linkedin_url = form.get("linkedin_url")

    # Duration parsing
    duration_raw = form.get("introduction_video_duration")
    duration = None
    if duration_raw is not None and str(duration_raw).strip().isdigit():
        duration = int(str(duration_raw).strip())

    # File uploads
    profile_photo_file = form.get("profile_photo")
    intro_video_file = form.get("introduction_video")
    intro_thumb_file = form.get("introduction_video_thumbnail")

    # Arrays
    category_ids = parse_category_ids(form.get("category_ids"))
    expertises = parse_list_of_strings(form.get("expertises"))
    languages = parse_list_of_strings(form.get("languages"))

    # Indexed bracket form structures
    cert_map: dict[int, dict[str, Any]] = {}
    qual_map: dict[int, dict[str, Any]] = {}

    for key, value in form.multi_items():
        m_cert = re.match(r"^certifications\[(\d+)\]\[(\w+)\]$", key)
        if m_cert:
            idx = int(m_cert.group(1))
            field = m_cert.group(2)
            cert_map.setdefault(idx, {})[field] = value
            continue

        m_qual = re.match(r"^qualifications\[(\d+)\]\[(\w+)\]$", key)
        if m_qual:
            idx = int(m_qual.group(1))
            field = m_qual.group(2)
            qual_map.setdefault(idx, {})[field] = value
            continue

    # Process certification files
    cert_items: list[dict[str, Any]] = []
    for idx in sorted(cert_map.keys()):
        item = cert_map[idx]
        name = str(item.get("name", "")).strip()
        doc_file = item.get("document")
        doc_path = await save_uploaded_file(doc_file, "certificates")
        if name:
            cert_items.append({"name": name, "document": doc_path})

    # Process qualification files
    qual_items: list[dict[str, Any]] = []
    for idx in sorted(qual_map.keys()):
        item = qual_map[idx]
        name = str(item.get("name", "")).strip()
        doc_file = item.get("document")
        doc_path = await save_uploaded_file(doc_file, "qualifications")
        if name:
            qual_items.append({"name": name, "document": doc_path})

    # Save top-level media files
    profile_photo_path = await save_uploaded_file(profile_photo_file, "profile")
    intro_video_path = await save_uploaded_file(intro_video_file, "videos")
    intro_thumb_path = await save_uploaded_file(intro_thumb_file, "videos/thumbnails")

    return {
        "about": str(about) if about is not None else None,
        "headline": str(headline) if headline is not None else None,
        "linkedin_url": str(linkedin_url) if linkedin_url is not None else None,
        "introduction_video_duration": duration,
        "profile_photo_path": profile_photo_path,
        "intro_video_path": intro_video_path,
        "intro_thumb_path": intro_thumb_path,
        "category_ids": category_ids,
        "expertises": expertises,
        "languages": languages,
        "certifications": cert_items,
        "qualifications": qual_items,
        "raw_form": form,
    }


async def get_provider_coach_profile(
    db: Session,
    user: User,
    request: Request | None = None,
) -> CoachProfileDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    return to_profile_data_response(profile, user, request)


async def create_provider_coach_profile(
    db: Session,
    user: User,
    request: Request,
) -> CoachProfileDataResponse:
    existing_profile = get_coach_profile_by_user_id(db, user.id)
    if existing_profile is not None:
        # If profile already exists, route to update for graceful onboarding
        return await update_provider_coach_profile(db=db, user=user, request=request)

    parsed = await parse_coach_form_data(request)

    # Resolve categories
    categories = []
    if parsed["category_ids"]:
        categories = get_categories_by_ids(db, parsed["category_ids"])
    if not categories:
        categories = get_or_create_default_categories(db)[:1]

    profile = create_coach_profile(
        db=db,
        user_id=user.id,
        headline=parsed["headline"] or "Career Coach",
        about=parsed["about"] or "",
        profile_photo=parsed["profile_photo_path"],
        introduction_video=parsed["intro_video_path"],
        introduction_video_duration=parsed["introduction_video_duration"] or 0,
        introduction_video_thumbnail=parsed["intro_thumb_path"],
        linkedin_url=parsed["linkedin_url"],
        expertises=parsed["expertises"],
        languages=parsed["languages"],
        status="pending",
        is_completed=True,
    )

    set_coach_categories(db, coach_profile=profile, categories=categories)

    if parsed["certifications"]:
        replace_certifications(
            db, coach_profile=profile, certifications_data=parsed["certifications"]
        )

    if parsed["qualifications"]:
        replace_qualifications(
            db, coach_profile=profile, qualifications_data=parsed["qualifications"]
        )

    # Sync user flags
    user.is_completed = True
    if user.role.upper() != "PROVIDER" and user.role.upper() != "COACH":
        user.role = "COACH"

    db.commit()
    db.refresh(profile)

    return to_profile_data_response(profile, user, request)


async def update_provider_coach_profile(
    db: Session,
    user: User,
    request: Request,
) -> CoachProfileDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    parsed = await parse_coach_form_data(request)

    if parsed["about"] is not None:
        profile.about = parsed["about"]

    if parsed["headline"] is not None:
        profile.headline = parsed["headline"]

    if parsed["linkedin_url"] is not None:
        profile.linkedin_url = parsed["linkedin_url"]

    if parsed["introduction_video_duration"] is not None:
        profile.introduction_video_duration = parsed["introduction_video_duration"]

    if parsed["profile_photo_path"] is not None:
        profile.profile_photo = parsed["profile_photo_path"]

    if parsed["intro_video_path"] is not None:
        profile.introduction_video = parsed["intro_video_path"]

    if parsed["intro_thumb_path"] is not None:
        profile.introduction_video_thumbnail = parsed["intro_thumb_path"]

    if parsed["expertises"]:
        profile.expertises = parsed["expertises"]

    if parsed["languages"]:
        profile.languages = parsed["languages"]

    if parsed["category_ids"]:
        categories = get_categories_by_ids(db, parsed["category_ids"])
        if categories:
            set_coach_categories(db, coach_profile=profile, categories=categories)

    if parsed["certifications"]:
        replace_certifications(
            db, coach_profile=profile, certifications_data=parsed["certifications"]
        )

    if parsed["qualifications"]:
        replace_qualifications(
            db, coach_profile=profile, qualifications_data=parsed["qualifications"]
        )

    user.is_completed = True
    db.commit()
    db.refresh(profile)

    return to_profile_data_response(profile, user, request)

