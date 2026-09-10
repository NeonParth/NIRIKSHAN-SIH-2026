# Risk Engine Design

## Core Philosophy
The NIRIKSHAN Risk Engine is **deterministic and explainable**. It does NOT claim to "detect fraud." Instead, it identifies "Risk Signals" that suggest a need for manual human verification.

## Scoring Mechanism
The engine calculates a total risk score by summing the contributions of various triggered signals.

### Formula
`Total Risk Score = Σ (Triggered Signal Weight)`
(Capped at 100)

### Signal Weights (Phase 1 Defaults)
| Signal Code | Weight | Description |
| :--- | :--- | :--- |
| `duplicate_proximity` | 25 | Project is located within 500m of another project. |
| `image_similarity` | 25 | Project evidence shares a perceptual hash with another project. |
| `cost_deviation` | 20 | Allocated amount exceeds benchmark by > 20%. |
| `low_bidder_competition` | 10 | Tender has fewer than 3 bidders. |
| `contractor_concentration` | 10 | Contractor holds a high share of regional awards. |
| `repeated_contractor_wins` | 10 | Contractor shows a pattern of repeated awards. |

## Risk Level Mapping
| Score Range | Level | Action Recommended |
| :--- | :--- | :--- |
| 0 - 30 | **LOW** | Routine Monitoring |
| 31 - 60 | **MEDIUM** | Targeted Review |
| 61 - 80 | **HIGH** | Priority Investigation |
| 81 - 100 | **CRITICAL** | Immediate Audit |

## Explainability
Every assessment includes:
1. **Risk Score**: The numerical value.
2. **Risk Level**: The categorical classification.
3. **Contributing Signals**: A list of every signal that triggered, including:
    - **Observed Value**: What was actually found (e.g., "2 bidders").
    - **Threshold**: What the limit was (e.g., "< 3 bidders").
    - **Explanation**: A human-readable reason why this is a risk.
4. **Evidence Links**: Direct pointers to the `ProjectEvidence` that triggered the signal.

## Implementation Details
The engine is implemented in `backend/app/services/risk_engine.py` and is decoupled from the data gathering logic in `assessment_service.py`. Weights are stored in `config/risk_weights.yaml` for easy adjustment without code changes.
