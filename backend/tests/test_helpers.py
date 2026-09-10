import pytest

from app.services.cost_analyzer import deviation_ratio
from app.services.image_processor import hashes_equal, perceptual_hash_from_metadata


def test_cost_ratio():
    assert deviation_ratio(2500000, 1600000) == pytest.approx(2500000 / 1600000)
    assert deviation_ratio(None, 1) is None
    assert deviation_ratio(1, 0) is None


def test_hash_helpers():
    assert perceptual_hash_from_metadata({"perceptual_hash": "SYNTH-HASH-A1"}) == "SYNTH-HASH-A1"
    assert hashes_equal("A", "A")
    assert not hashes_equal("A", "B")
    assert not hashes_equal(None, "A")
