# Media upload system: why we fixed it and what we fixed

This documents the audit of how uploaded files are saved and served, the gaps found, and the changes made.

## Why: the problems

| # | Gap | Impact |
|---|-----|--------|
| 1 | All of `media/` was served publicly at `/media` with no auth. Paid product files were stored there. | Anyone with (or guessing) a `/media/coach/products/files/<name>` URL could download a paid product without buying it. |
| 2 | `GET /v1/user/digital-product-download/{id}` had no auth dependency. | Anyone could download any product's full file by ID. |
| 3 | No validation: any extension, any size, content never inspected, whole file read into memory. | `.html`/`.svg` uploads served from our origin (stored XSS), memory exhaustion from large uploads, junk files. |
| 4 | Profile images saved under the **original filename** (no unique suffix). | Two users uploading `photo.jpg` overwrite each other; deleting an account could delete someone else's photo. |
| 5 | The file was written before the DB commit. | A failed commit left orphan files on disk. |
| 6 | Replacing a profile photo never deleted the old one. | Files accumulated forever. |
| 7 | Paths like `Path("media")` were relative to the working directory. | Starting the server from another directory wrote/looked in the wrong place. |
| 8 | The same save logic was copy-pasted in five places. | Any fix had to be repeated five times. |
| 9 | When preview generation failed, the **full file** was copied into the public tree as the "preview". | Leaked the paid file through the public mount. |
| 10 | Download for a non-purchased user fell back to the full file if preview extraction failed. | Same leak through the API. |

## What: the changes

### New: `src/utils/uploads.py` (single upload helper)
- `save_upload(file, kind=..., subfolder=..., private=False)`:
  - **Extension allowlist per kind**: `image`, `document`, `video`, `preview`, `product_file`.
  - **Magic-byte check** against the declared extension (JPEG/PNG/GIF/WebP/PDF/MP4/MOV/WebM/ZIP/EPUB).
  - **Size caps** (configurable, see below), enforced while **streaming in 1 MB chunks**. Nothing is held fully in memory, and a partial file is deleted on any failure.
  - Always a **unique filename** (`<clean-stem>_<uuid8><ext>`).
  - Returns `SavedUpload(web_path, disk_path, size, extension, stem)`, or `None` when no file was sent, so optional form fields still work.
  - Raises `AppException` 400 (bad type or content) or 413 (too large).
- `MEDIA_ROOT` / `PRIVATE_MEDIA_ROOT` are **absolute**, anchored at the project root.
- `resolve_media_path()` maps a stored path (`/media/...`, `/private_media/...`, legacy `media/...`) to a disk path and **refuses anything outside the media roots** (blocks `..` traversal).

### Private storage for paid files
- Product book files are now saved to **`private_media/coach/products/files/`**, which is **not mounted** and never served statically.
- They are reachable only through authenticated download routes.
- Stored DB paths look like `/private_media/coach/products/files/<name>`.
- `private_media/` is added to `.gitignore`.
- Preview PDFs (public by design) go to `media/coach/products/previews/`.

### Legacy files are protected without a data migration
- `src/utils/static_files.py` adds `PublicMediaFiles`, which returns 404 for anything under `media/coach/products/files/` unless the name contains `_preview_`.
- Existing paid files (whose DB path still starts with `/media/...`) stop being public immediately, and still download correctly through the authenticated routes via `resolve_media_path()`.

### Download routes
- **Provider route** (`/v1/user/digital-product-download/{id}`): now requires an approved coach and checks they **own** the product.
- **Client route**:
  - Purchasers get the real file (streamed with `FileResponse`, so large videos aren't loaded into memory).
  - Everyone else gets only a PDF preview.
  - If a preview can't be produced, the response is **403 `PURCHASE_REQUIRED`**, never the full file.
  - PDFs keep the existing `receipt.pdf` filename so current clients don't break. Non-PDF products now get a real filename and a guessed content type.

### Preview generation
- Unparseable PDFs no longer get the full content copied into the public tree. They report 1 page and no preview.

### Profile photos (`me.py`, `delete_account.py`)
- Use the shared helper (unique names, validation).
- The old photo is deleted **after** the DB commit succeeds.
- On commit failure the new file is removed (no orphans).
- Account deletion removes only that user's own file, through the safe helper.

### Other services moved onto the helper
Coach profile (photo, intro video, thumbnail, certificate and qualification documents), blog images, and product thumbnails now all use `save_upload`. The five duplicated implementations are gone.

### Config (`src/core/config.py`, overridable via env)
`MEDIA_ROOT`, `PRIVATE_MEDIA_ROOT`, `MAX_IMAGE_UPLOAD_MB` (5), `MAX_DOCUMENT_UPLOAD_MB` (10), `MAX_VIDEO_UPLOAD_MB` (200), `MAX_PRODUCT_UPLOAD_MB` (200).

## Behavior changes to know about
- Uploads with a disallowed extension, mismatched content, or too large now return **400/413** instead of being accepted. Clients that sent files with no extension will now be rejected.
- The provider download route now requires a coach login (the existing test was updated to send the coach token).
- New paid product files are stored in `private_media/`, which must be included in your backups and deployment volumes, as `media/` is.

## Not changed (follow-ups)
- **Certificates and qualification documents** are still under the public `media/` mount, because the profile UI currently shows them by URL. Making them private needs an authenticated route for the owner and for admins, which is a product decision.
- The 29 sample/test files under `media/` are still tracked in git (`git rm -r --cached media` untracks them).
- No virus scanning and no per-user storage quota.

## Verification
- Full existing suite: **51 passed**.
- Manual checks: legacy paid file URL returns 404; legacy preview and blog images return 200; `.html` upload returns 400; a `.jpg` containing script returns 400; a 6 MB image returns 413; `/media/../src/main.py` resolves to nothing.
