from pathlib import Path
import struct
from typing import Any


def format_duration(seconds: int | float | None) -> str:
    """
    Format duration in seconds into a standard display string.
    - Under 1 hour: "M:SS" (e.g. 45 -> "0:45", 75 -> "1:15")
    - 1 hour or more: "H:MM:SS" (e.g. 3665 -> "1:01:05")
    """
    if seconds is None:
        return "0:00"
    try:
        total_seconds = int(round(float(seconds)))
    except (ValueError, TypeError):
        return "0:00"

    if total_seconds <= 0:
        return "0:00"

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def get_mp4_duration_fast(filepath: str | Path) -> float | None:
    """
    Fast pure-Python ISO BMFF / MP4 / MOV container parser.
    Reads movie header ('mvhd') atom inside 'moov' to determine exact duration.
    Works with no external native binary dependencies.
    """
    path_obj = Path(filepath)
    if not path_obj.exists() or path_obj.stat().st_size < 16:
        return None

    try:
        with open(path_obj, "rb") as f:
            while True:
                header = f.read(8)
                if len(header) < 8:
                    break

                size, atom_type = struct.unpack(">I4s", header)
                if size == 1:
                    ext_size = f.read(8)
                    if len(ext_size) < 8:
                        break
                    size = struct.unpack(">Q", ext_size)[0]
                    content_size = size - 16
                elif size == 0:
                    # Extends to end of file
                    content_size = path_obj.stat().st_size - f.tell()
                else:
                    content_size = size - 8

                if content_size < 0:
                    break

                if atom_type == b"moov":
                    # Look for mvhd inside moov (usually in the first 2MB of moov)
                    read_limit = min(content_size, 5 * 1024 * 1024)
                    moov_data = f.read(read_limit)
                    idx = moov_data.find(b"mvhd")
                    if idx >= 4:
                        mvhd_start = idx - 4
                        if mvhd_start + 40 <= len(moov_data):
                            version = moov_data[mvhd_start + 8]
                            if version == 0:
                                timescale, duration = struct.unpack(
                                    ">II",
                                    moov_data[mvhd_start + 20 : mvhd_start + 28],
                                )
                            elif version == 1:
                                timescale, duration = struct.unpack(
                                    ">IQ",
                                    moov_data[mvhd_start + 28 : mvhd_start + 40],
                                )
                            else:
                                return None

                            if timescale > 0:
                                return duration / timescale
                    return None
                else:
                    if content_size > 0:
                        f.seek(content_size, 1)
                    else:
                        break
    except Exception:
        return None

    return None


def extract_video_duration(file_path: Path | str) -> int:
    """
    Extract duration in seconds from a video file.
    Tries multiple strategies:
    1. mutagen MP4 parser
    2. mutagen generic File parser
    3. Fast pure-Python MP4/MOV atom parser
    Returns integer seconds (0 if undetected).
    """
    path_obj = Path(file_path)
    if not path_obj.exists() or path_obj.stat().st_size == 0:
        return 0

    # Strategy 1: mutagen.mp4.MP4
    try:
        from mutagen.mp4 import MP4

        mp4 = MP4(str(path_obj))
        if mp4 and getattr(mp4, "info", None) is not None:
            length = getattr(mp4.info, "length", None)
            if length and length > 0:
                return max(1, int(round(length)))
    except Exception:
        pass

    # Strategy 2: Fast pure-Python ISO BMFF / MP4 atom parser
    try:
        fast_dur = get_mp4_duration_fast(path_obj)
        if fast_dur and fast_dur > 0:
            return max(1, int(round(fast_dur)))
    except Exception:
        pass

    # Strategy 3: mutagen generic File
    try:
        import mutagen

        media = mutagen.File(str(path_obj))
        if media and getattr(media, "info", None) is not None:
            length = getattr(media.info, "length", None)
            if length and length > 0:
                return max(1, int(round(length)))
    except Exception:
        pass

    return 0
