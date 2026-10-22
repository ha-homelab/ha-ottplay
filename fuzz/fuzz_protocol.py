"""Check production URL and number admission, without a server or HA runtime."""

import json
import math
import sys
from pathlib import Path
from urllib.parse import urlsplit

import atheris

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components/ottplay"))
with atheris.instrument_imports():
    import protocol


def test_one_input(data):
    text = data.decode("utf-8", errors="replace")
    try:
        normalized = protocol.normalize_url(text)
    except ValueError:
        pass
    else:
        parsed = urlsplit(normalized)
        assert parsed.scheme in ("http", "https") and parsed.hostname
        assert parsed.username is None and parsed.password is None
        assert not parsed.query and not parsed.fragment
        assert "%" not in normalized and "\\" not in normalized
        assert all(part not in (".", "..") for part in parsed.path.split("/"))
        assert protocol.normalize_url(normalized) == normalized
    try:
        value = json.loads(data)
    except (ValueError, UnicodeError, RecursionError):
        pass
    else:
        accepted = protocol.valid_number(value, 0, 100)
        if accepted:
            assert type(value) in (int, float) and 0 <= value <= 100
    provider = atheris.FuzzedDataProvider(data)
    number = provider.ConsumeFloat()
    accepted = protocol.valid_number(number, 0, 100)
    assert accepted == (math.isfinite(number) and 0 <= number <= 100)
    for invalid in (True, False, None, "0", math.nan, math.inf, -1, 101):
        assert not protocol.valid_number(invalid, 0, 100)


if __name__ == "__main__":
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()
