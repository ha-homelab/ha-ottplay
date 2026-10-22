"""Pure protocol boundaries shared by the live client and offline fuzz targets."""

import math
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit


def normalize_url(value: str) -> str:
    """Validate an explicit HTTP(S) base without credential or redirect tricks."""
    if not isinstance(value, str) or re.search(r"[\s\\\x00-\x1f\x7f]", value):
        raise ValueError("Invalid control server URL")
    try:
        parsed = urlsplit(value)
        if (
            parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or "%" in parsed.netloc
        ):
            raise ValueError
        _ = parsed.port
        path = parsed.path.rstrip("/")
        if "%" in path or "//" in path or any(p in (".", "..") for p in path.split("/")):
            raise ValueError
        return urlunsplit((parsed.scheme, parsed.netloc.lower(), path, "", ""))
    except ValueError:
        raise ValueError("Invalid control server URL") from None


def valid_number(value: Any, minimum: float = 0, maximum: float = 315576000) -> bool:
    return (
        isinstance(value, (float, int))
        and not isinstance(value, bool)
        and minimum <= value <= maximum
        and math.isfinite(value)
    )
