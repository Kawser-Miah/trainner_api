import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.config import settings
from src.core.exceptions import AppException

# Anchored at the project root so uploads never depend on the process working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MEDIA_ROOT = (PROJECT_ROOT / settings.media_root).resolve()
PRIVATE_MEDIA_ROOT = (PROJECT_ROOT / settings.private_media_root).resolve()

PUBLIC_URL_PREFIX = "/media"
PRIVATE_URL_PREFIX = "/private_media"

CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class UploadRule:
    extensions: frozenset[str]
    max_bytes: int
    label: str


@dataclass(frozen=True)
class SavedUpload:
    web_path: str
    disk_path: Path
    size: int
    extension: str
    stem: str


def _mb(value: int) -> int:
    return value * 1024 * 1024


UPLOAD_RULES: dict[str, UploadRule] = {
    "image": UploadRule(
        frozenset({".jpg", ".jpeg", ".png", ".gif", ".webp"}),
        _mb(settings.max_image_upload_mb),
        "image",
    ),
    "document": UploadRule(
        frozenset({".pdf", ".jpg", ".jpeg", ".png"}),
        _mb(settings.max_document_upload_mb),
        "document",
    ),
    "video": UploadRule(
        frozenset({".mp4", ".mov", ".webm"}),
        _mb(settings.max_video_upload_mb),
        "video",
    ),
    "preview": UploadRule(
        frozenset({".pdf"}),
        _mb(settings.max_document_upload_mb),
        "PDF",
    ),
    "product_file": UploadRule(
        frozenset({".pdf", ".epub", ".zip", ".mp3", ".mp4", ".mov", ".webm"}),
        _mb(settings.max_product_upload_mb),
        "product file",
    ),
}


def _matches_signature(extension: str, head: bytes) -> bool:
    """Check the leading bytes against the declared extension.

    Extensions without a known signature (e.g. .mp3 with ID3-less streams) are
    accepted; the allowlist above is still enforced for them.
    """
    if extension in (".jpg", ".jpeg"):
        return head.startswith(b"\xff\xd8\xff")
    if extension == ".png":
        return head.startswith(b"\x89PNG\r\n\x1a\n")
    if extension == ".gif":
        return head.startswith((b"GIF87a", b"GIF89a"))
    if extension == ".webp":
        return head[:4] == b"RIFF" and head[8:12] == b"WEBP"
    if extension == ".pdf":
        return head.lstrip().startswith(b"%PDF-")
    if extension in (".mp4", ".mov"):
        return head[4:8] == b"ftyp"
    if extension == ".webm":
        return head.startswith(b"\x1a\x45\xdf\xa3")
    if extension in (".zip", ".epub"):
        return head.startswith(b"PK")
    return True


def _invalid(message: str, status: int = 400, error: str = "INVALID_UPLOAD") -> AppException:
    return AppException(message=message, status=status, error=error)


async def save_upload(
    file: Any,
    *,
    kind: str,
    subfolder: str,
    private: bool = False,
) -> SavedUpload | None:
    """Validate and stream an uploaded file to disk.

    Returns None when no file was sent (or it was empty) so optional form fields keep
    working; raises AppException for a disallowed type, wrong content or oversized file.
    """
    if file is None or not hasattr(file, "read") or not getattr(file, "filename", None):
        return None

    rule = UPLOAD_RULES[kind]
    original = Path(file.filename)
    extension = original.suffix.lower()
    if extension not in rule.extensions:
        allowed = ", ".join(sorted(rule.extensions))
        raise _invalid(f"Unsupported {rule.label} type '{extension or 'none'}'. Allowed: {allowed}.")

    stem = re.sub(r"[^\w\-]", "_", original.stem) or "file"
    root = PRIVATE_MEDIA_ROOT if private else MEDIA_ROOT
    prefix = PRIVATE_URL_PREFIX if private else PUBLIC_URL_PREFIX
    dest_dir = root / subfolder
    dest_dir.mkdir(parents=True, exist_ok=True)

    unique_name = f"{stem}_{uuid.uuid4().hex[:8]}{extension}"
    dest_path = dest_dir / unique_name

    size = 0
    try:
        with open(dest_path, "wb") as out:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                if size == 0 and not _matches_signature(extension, chunk[:32]):
                    raise _invalid(f"The uploaded file content does not match its '{extension}' type.")
                size += len(chunk)
                if size > rule.max_bytes:
                    raise _invalid(
                        f"The {rule.label} is too large. Maximum size is {rule.max_bytes // (1024 * 1024)} MB.",
                        status=413,
                        error="UPLOAD_TOO_LARGE",
                    )
                out.write(chunk)
    except BaseException:
        dest_path.unlink(missing_ok=True)
        raise

    if size == 0:
        dest_path.unlink(missing_ok=True)
        return None

    return SavedUpload(
        web_path=f"{prefix}/{subfolder}/{unique_name}",
        disk_path=dest_path,
        size=size,
        extension=extension,
        stem=stem,
    )


def resolve_media_path(file_path: str | None) -> Path | None:
    """Map a stored media path to an absolute path, refusing anything outside the media roots."""
    if not file_path or file_path.startswith(("http://", "https://")):
        return None

    clean = file_path.replace("\\", "/").lstrip("/")
    for url_prefix, root in (
        (PRIVATE_URL_PREFIX.lstrip("/"), PRIVATE_MEDIA_ROOT),
        (PUBLIC_URL_PREFIX.lstrip("/"), MEDIA_ROOT),
    ):
        if clean == url_prefix or clean.startswith(f"{url_prefix}/"):
            target = (root / clean[len(url_prefix):].lstrip("/")).resolve()
            if target == root or root in target.parents:
                return target
            return None
    return None
