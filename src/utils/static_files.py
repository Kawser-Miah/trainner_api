from pathlib import PurePosixPath

from fastapi import HTTPException
from starlette.staticfiles import StaticFiles

# Paid product files created before they moved to the private media root still live here.
LEGACY_PAID_FILES_DIR = "coach/products/files/"


class PublicMediaFiles(StaticFiles):
    """Static media server that never exposes legacy paid product files.

    Previews that were generated into the same folder (``*_preview_*``) stay public;
    the full files are only reachable through the authenticated download routes.
    """

    async def get_response(self, path: str, scope):
        normalized = path.replace("\\", "/").lstrip("/")
        if normalized.startswith(LEGACY_PAID_FILES_DIR) and "_preview_" not in PurePosixPath(normalized).name:
            raise HTTPException(status_code=404)
        return await super().get_response(path, scope)
