from __future__ import annotations

from typing import Optional, Any
from sqlalchemy.orm import Session

from app.database.models import Project

def deviation_ratio(allocated: Optional[float], benchmark: Optional[float]) -> Optional[float]:
    if allocated is None or benchmark is None:
        return None
    allocated_f = float(allocated)
    benchmark_f = float(benchmark)
    if benchmark_f <= 0:
        return None
    return allocated_f / benchmark_f

def get_cost_signal(project: Project, threshold_ratio: float = 1.2) -> Optional[dict[str, Any]]:
    if project.allocated_amount is None or project.benchmark_amount is None:
        return None

    ratio = deviation_ratio(project.allocated_amount, project.benchmark_amount)
    if ratio is None or ratio <= threshold_ratio:
        return None

    return {
        "signal_code": "cost_deviation",
        "observed_value": f"{ratio:.2f}x",
        "threshold": f"<{threshold_ratio}x",
        "explanation": f"Allocated amount is {((ratio-1)*100):.1f}% above benchmark",
        "source_reference": "Market Benchmarks",
        "source_module": "cost_analyzer"
    }
