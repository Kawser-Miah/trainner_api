from pathlib import Path
from fastapi import Request

from src.utils.uploads import resolve_media_path


def get_base_url(request: Request | None) -> str:
    """
    Generate the base URL from the incoming request.
    Respects reverse-proxy headers ('x-forwarded-proto', 'x-forwarded-host')
    with fallback to request.base_url.
    """
    if request is None:
        return ""

    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.headers.get("host"))
    if host:
        return f"{proto}://{host}".rstrip("/")

    return str(request.base_url).rstrip("/")


def build_media_url(file_path: str | None, request: Request | None = None) -> str | None:
    """
    Convert a relative media path into a fully qualified absolute URL.
    If the path is already an absolute HTTP/HTTPS URL or empty, returns it directly.
    """
    if not file_path:
        return None

    if file_path.startswith("http://") or file_path.startswith("https://"):
        return file_path

    base_url = get_base_url(request)
    if not base_url:
        return file_path

    clean_path = file_path.lstrip("/")
    return f"{base_url}/{clean_path}"


def delete_media_file(file_path: str | None) -> bool:
    """
    Safely delete an existing local media file from disk when it is replaced or removed.
    Only files inside the media roots can be removed.
    """
    target_path = resolve_media_path(file_path)
    if target_path is None:
        return False

    try:
        if target_path.is_file():
            target_path.unlink()
            return True
    except OSError:
        pass

    return False
