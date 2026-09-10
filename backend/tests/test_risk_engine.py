from pathlib import Path

import pytest

from app.database.models.enums import RiskLevel
from app.services.risk_engine import (
    RiskEngineError,
    SignalContribution,
    calculate_assessment,
    classify_risk_level,
    load_weight_config,
)

WEIGHTS = {
    "duplicate_proximity": 25,
    "image_similarity": 25,
    "cost_deviation": 20,
    "low_bidder_competition": 10,
    "contractor_concentration": 10,
    "repeated_contractor_wins": 10,
}


def _signal(code: str, contribution: float) -> SignalContribution:
    return SignalContribution(signal_code=code, contribution=contribution, explanation="test", source_module="test")


def test_example_score_from_spec():
    result = calculate_assessment(
        [
            _signal("duplicate_proximity", 25),
            _signal("cost_deviation", 20),
            _signal("low_bidder_competition", 10),
        ],
        WEIGHTS,
    )
    assert result.risk_score == 55
    assert result.risk_level == RiskLevel.MEDIUM
    assert [item.signal_code for item in result.contributing_signals] == [
        "duplicate_proximity",
        "cost_deviation",
        "low_bidder_competition",
    ]
    assert "does not establish fraud" in result.explanation


def test_maximum_score():
    signals = [_signal(code, weight) for code, weight in WEIGHTS.items()]
    result = calculate_assessment(signals, WEIGHTS)
    assert result.risk_score == 100
    assert result.risk_level == RiskLevel.CRITICAL


def test_zero_signal_case():
    result = calculate_assessment([], WEIGHTS)
    assert result.risk_score == 0
    assert result.risk_level == RiskLevel.LOW
    assert result.contributing_signals == []


def test_missing_signals_are_zero():
    result = calculate_assessment([_signal("cost_deviation", 20)], WEIGHTS)
    assert result.risk_score == 20
    assert result.risk_level == RiskLevel.LOW


def test_risk_level_boundaries():
    assert classify_risk_level(0) == RiskLevel.LOW
    assert classify_risk_level(30) == RiskLevel.LOW
    assert classify_risk_level(31) == RiskLevel.MEDIUM
    assert classify_risk_level(60) == RiskLevel.MEDIUM
    assert classify_risk_level(61) == RiskLevel.HIGH
    assert classify_risk_level(80) == RiskLevel.HIGH
    assert classify_risk_level(81) == RiskLevel.CRITICAL
    assert classify_risk_level(100) == RiskLevel.CRITICAL


def test_configurable_weights():
    custom = {"duplicate_proximity": 40, "cost_deviation": 10}
    result = calculate_assessment(
        [_signal("duplicate_proximity", 40), _signal("cost_deviation", 10)],
        custom,
    )
    assert result.risk_score == 50
    assert result.weights == custom


def test_unknown_signal_rejected():
    with pytest.raises(RiskEngineError, match="Unknown signal_code"):
        calculate_assessment([_signal("not_a_signal", 1)], WEIGHTS)


def test_negative_contribution_rejected():
    with pytest.raises(RiskEngineError, match="must be >= 0"):
        calculate_assessment([_signal("cost_deviation", -1)], WEIGHTS)


def test_contribution_cannot_exceed_weight():
    with pytest.raises(RiskEngineError, match="exceeds configured weight"):
        calculate_assessment([_signal("cost_deviation", 21)], WEIGHTS)


def test_empty_weights_rejected():
    with pytest.raises(RiskEngineError, match="must not be empty"):
        calculate_assessment([], {})


def test_invalid_score_range():
    with pytest.raises(RiskEngineError):
        classify_risk_level(-1)
    with pytest.raises(RiskEngineError):
        classify_risk_level(101)


def test_zero_contribution_omitted_from_output():
    result = calculate_assessment([_signal("cost_deviation", 0)], WEIGHTS)
    assert result.risk_score == 0
    assert result.contributing_signals == []


def test_yaml_weights_load():
    path = Path(__file__).resolve().parents[2] / "config" / "risk_weights.yaml"
    config = load_weight_config(path)
    assert sum(config["signals"].values()) == 100
    assert config["signals"]["duplicate_proximity"] == 25
    assert "vendor_nexus_detected" not in config["signals"]
    assert "corporate_collusion" not in config["signals"]
