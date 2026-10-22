"""The live client retains exactly the pure protocol boundary."""

from custom_components.ottplay import api, protocol


def test_client_uses_shared_protocol_boundaries():
    assert api.normalize_url is protocol.normalize_url
    assert api._number is protocol.valid_number


def test_oversized_integer_is_rejected_without_float_overflow():
    assert not protocol.valid_number(10**400, 0, 100)
    assert not protocol.valid_number(-(10**400), 0, 100)
