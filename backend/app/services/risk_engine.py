from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional

import yaml

from app.database.models.enums import RiskLevel

SIGNAL_LABELS = {
    "duplicate_proximity": "Similar project nearby",
    "image_similarity": "Image similarity",
    "cost_deviation": "Cost deviation",
    "low_bidder_competition": "Low competition",
    "contractor_concentration": "Contractor concentration",
    "repeated_contractor_wins": "Repeated contractor wins",
    "vendor_nexus_detected": "Suspicious vendor nexus",
    "corporate_collusion": "Corporate relationship collusion",
}


@dataclass(frozen=True)
class SignalContribution:
    signal_code: str
    contribution: float
    observed_value: Optional[str] = None
    threshold: Optional[str] = None
    explanation: str = ""
    source_reference: Optional[str] = None
    source_module: str = "unspecified"


@dataclass
class RiskResult:
    risk_score: int
    risk_level: RiskLevel
    contributing_signals: list[SignalContribution]
    explanation: str
    source_module: str
    weights: dict[str, float] = field(default_factory=dict)


class RiskEngineError(ValueError):
    pass


def load_weight_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or "signals" not in data:
        raise RiskEngineError("Risk weight configuration must contain a 'signals' mapping")
    return data


def classify_risk_level(score: int, levels: Optional[Mapping[str, Mapping[str, int]]] = None) -> RiskLevel:
    if score < 0 or score > 100:
        raise RiskEngineError("risk_score must be between 0 and 100")
    if not levels:
        if score <= 30:
            return RiskLevel.LOW
        if score <= 60:
            return RiskLevel.MEDIUM
        if score <= 80:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL
    for name, bounds in levels.items():
        if bounds["min"] <= score <= bounds["max"]:
            return RiskLevel(name)
    raise RiskEngineError(f"No risk level range contains score {score}")


def calculate_assessment(
    active_signals: Mapping[str, SignalContribution] | list[SignalContribution],
    weights: Mapping[str, float],
    *,
    source_module: str = "rule_based_risk_engine",
    levels: Optional[Mapping[str, Mapping[str, int]]] = None,
) -> RiskResult:
    if not weights:
        raise RiskEngineError("Signal weights must not be empty")
    for code, weight in weights.items():
        if weight < 0:
            raise RiskEngineError(f"Weight for {code} must be >= 0")

    if isinstance(active_signals, Mapping):
        contributions = list(active_signals.values())
    else:
        contributions = list(active_signals)

    known = set(weights)
    total = 0.0
    included: list[SignalContribution] = []
    for item in contributions:
        if item.signal_code not in known:
            raise RiskEngineError(f"Unknown signal_code: {item.signal_code}")
        if item.contribution < 0:
            raise RiskEngineError(f"Contribution for {item.signal_code} must be >= 0")
        max_weight = float(weights[item.signal_code])
        if item.contribution > max_weight:
            raise RiskEngineError(
                f"Contribution for {item.signal_code} ({item.contribution}) exceeds configured weight {max_weight}"
            )
        if item.contribution == 0:
            continue
        included.append(item)
        total += float(item.contribution)

    score = int(round(min(total, 100)))
    level = classify_risk_level(score, levels)
    if included:
        parts = [
            f"+{int(item.contribution)} {SIGNAL_LABELS.get(item.signal_code, item.signal_code)}"
            for item in included
        ]
        explanation = (
            f"Explainable rule-based assessment. Score {score}/100 ({level.value}). "
            f"Contributing signals: {', '.join(parts)}. "
            "This identifies potential anomalies and risk signals for verification; "
            "it does not establish fraud or wrongdoing."
        )
    else:
        explanation = (
            f"Explainable rule-based assessment. Score {score}/100 ({level.value}). "
            "No configured risk signals were triggered. Manual review is still available."
        )
    return RiskResult(
        risk_score=score,
        risk_level=level,
        contributing_signals=included,
        explanation=explanation,
        source_module=source_module,
        weights=dict(weights),
    )


def contribution_from_weight(
    signal_code: str,
    *,
    weights: Mapping[str, float],
    observed_value: Optional[str],
    threshold: Optional[str],
    explanation: str,
    source_reference: Optional[str],
    source_module: str,
) -> SignalContribution:
    return SignalContribution(
        signal_code=signal_code,
        contribution=float(weights[signal_code]),
        observed_value=observed_value,
        threshold=threshold,
        explanation=explanation,
        source_reference=source_reference,
        source_module=source_module,
    )
