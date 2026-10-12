from fastapi import Request
from sqlalchemy.orm import Session

from src.core.exceptions import AppException
from src.repository.client.browse.client_browse_repository import get_browse_coach_profile_detail
from src.schemas.client.browse.coach_schemas import (
    ClientCoachCertificationResponse,
    ClientCoachQualificationResponse,
    ClientCoachUserResponse,
    CoachProfileDetailResponse,
    MissedMeetingsResponse,
)
from src.service.client.browse.helpers import (
    calculate_starting_price,
    format_duration_display,
    format_iso_datetime,
    get_coach_provider_details,
)
from src.utils.media import build_media_url


async def get_coach_profile_detail_service(
    coach_profile_id: int,
    db: Session,
    request: Request | None = None,
) -> CoachProfileDetailResponse:
    profile = get_browse_coach_profile_detail(db=db, coach_profile_id=coach_profile_id)
    if not profile:
        raise AppException(
            message="Coach profile not found.",
            status=404,
            error="COACH_PROFILE_NOT_FOUND",
        )

    user = profile.user
    provider_details = get_coach_provider_details(profile, request)

    user_resp = ClientCoachUserResponse(
        id=user.id if user else profile.user_id,
        full_name=user.full_name if user else "",
        email=user.email if user else "",
        phone_number=user.phone or "" if user else "",
        address=user.address if user else None,
        image=build_media_url(user.photo_url, request) if user and user.photo_url else None,
    )

    certifications = [
        ClientCoachCertificationResponse(
            id=c.id,
            name=c.name,
            document=build_media_url(c.document, request) if c.document else None,
            created_at=format_iso_datetime(c.created_at),
        )
        for c in (profile.certifications or [])
    ]

    qualifications = [
        ClientCoachQualificationResponse(
            id=q.id,
            name=q.name,
            document=build_media_url(q.document, request) if q.document else None,
            created_at=format_iso_datetime(q.created_at),
        )
        for q in (profile.qualifications or [])
    ]

    # Map Services
    services_list = []
    for s in profile.services or []:
        if s.status == "published":
            cat_dict = (
                {"id": s.category.id, "name": s.category.name, "description": s.category.description}
                if s.category
                else None
            )
            benefits_list = [b.outcome for b in (s.benefits or [])]
            services_list.append({
                "id": s.id,
                "coach_id": user.id if user else profile.user_id,
                "coach_profile_id": profile.id,
                "provider_details": provider_details,
                "title": s.title,
                "description": s.description or "",
                "service_type": s.service_type,
                "service_type_display": "One Time Session" if s.service_type == "one_time" else s.service_type.title(),
                "session_format": s.session_format,
                "session_format_display": "Video Call" if s.session_format == "video" else s.session_format.title(),
                "session_duration": s.session_duration,
                "currency": s.currency,
                "price": s.price,
                "booking_type": s.booking_type,
                "booking_type_display": "Instant Booking" if s.booking_type == "instant" else "Coach Approval Required",
                "who_is_this_service_for": s.who_is_this_service_for or "",
                "preparation_instructions": s.preparation_instructions or "",
                "cancellation_policy": s.cancellation_policy,
                "cancellation_policy_display": s.cancellation_policy.title(),
                "session_url": s.session_url,
                "status": s.status,
                "category": cat_dict,
                "benefits": benefits_list,
                "created_at": format_iso_datetime(s.created_at),
                "updated_at": format_iso_datetime(s.updated_at),
                "category_name": s.category.name if s.category else "",
            })

    # Map Products
    products_list = []
    for p in profile.products or []:
        if p.status == "published":
            cat_dict = (
                {"id": p.category.id, "name": p.category.name, "description": p.category.description}
                if p.category
                else None
            )
            download_url = (
                f"{str(request.base_url).rstrip('/')}/api/v1/user/digital-product-download/{p.id}/"
                if request and p.book_file
                else None
            )
            products_list.append({
                "id": p.id,
                "coach": provider_details,
                "category": p.category_id,
                "category_details": cat_dict,
                "title": p.title,
                "description": p.description or "",
                "Thumbnail": build_media_url(p.thumbnail, request) if p.thumbnail else None,
                "book_file": download_url,
                "preview_file": build_media_url(p.preview_file, request) if p.preview_file else None,
                "page_count": p.page_count,
                "preview_page_count": p.preview_page_count,
                "file_type": p.file_type or "PDF",
                "is_purchased": False,
                "price": p.price,
                "status": p.status,
                "created_at": format_iso_datetime(p.created_at),
                "updated_at": format_iso_datetime(p.updated_at),
            })

    # Map Blogs
    blogs_list = []
    for b in profile.blogs or []:
        if b.status == "published":
            cat_dict = (
                {"id": b.category.id, "name": b.category.name, "description": b.category.description}
                if b.category
                else None
            )
            words = len(b.content.split()) if b.content else 0
            read_time = max(1, words // 200)
            blogs_list.append({
                "id": b.id,
                "coach": provider_details,
                "category": b.category_id,
                "category_details": cat_dict,
                "title": b.title,
                "content": b.content,
                "image": build_media_url(b.image, request) if b.image else None,
                "status": b.status,
                "read_time_minutes": read_time,
                "created_at": format_iso_datetime(b.created_at),
                "updated_at": format_iso_datetime(b.updated_at),
            })

    # Map Reviews and breakdown
    reviews_list = []
    rating_breakdown = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    for r in profile.reviews or []:
        star_k = str(r.rating)
        if star_k in rating_breakdown:
            rating_breakdown[star_k] += 1
        u_name = r.user.full_name if r.user else "Anonymous"
        u_photo = build_media_url(r.user.photo_url, request) if r.user and r.user.photo_url else None
        reviews_list.append({
            "id": r.id,
            "user_name": u_name,
            "user_image": u_photo,
            "rating": r.rating,
            "review": r.review,
            "created_at": format_iso_datetime(r.created_at),
        })

    takes_on_call = profile.availability.on_call_enabled if profile.availability else False
    starting_price = calculate_starting_price(profile.services)
    total_sess = int(profile.completed_sessions_count or 0)

    missed_obj = MissedMeetingsResponse(
        missed=0,
        total=total_sess,
        ratio=f"0/{total_sess}",
        percent=0.0,
    )

    return CoachProfileDetailResponse(
        id=profile.id,
        user=user_resp,
        profile_photo=provider_details["profile_photo"],
        introduction_video=build_media_url(profile.introduction_video, request) if profile.introduction_video else None,
        introduction_video_duration=profile.introduction_video_duration,
        introduction_video_duration_display=format_duration_display(profile.introduction_video_duration),
        introduction_video_thumbnail=(
            build_media_url(profile.introduction_video_thumbnail, request)
            if profile.introduction_video_thumbnail
            else None
        ),
        linkedin_url=profile.linkedin_url or "",
        affiliate_status=None,
        affiliate_code=None,
        affiliate_commission_percent=profile.affiliate_commission_percent or "20.00",
        headline=profile.headline or "",
        about=profile.about or "",
        expertises=profile.expertises or [],
        languages=profile.languages or [],
        is_completed=profile.is_completed,
        status=profile.status,
        categories=[c.name for c in (profile.categories or [])],
        certifications=certifications,
        qualifications=qualifications,
        services=services_list,
        products=products_list,
        blogs=blogs_list,
        avg_rating=float(profile.avg_rating or 0.0),
        review_count=int(profile.total_reviews or len(profile.reviews or [])),
        completed_sessions_count=total_sess,
        success_rate=profile.success_rate if profile.success_rate is not None else 100,
        missed_meetings=missed_obj,
        takes_on_call=takes_on_call,
        starting_price=starting_price,
        is_favorited=False,
        reviews=reviews_list,
        rating_breakdown=rating_breakdown,
        created_at=format_iso_datetime(profile.created_at),
        updated_at=format_iso_datetime(profile.updated_at),
    )
