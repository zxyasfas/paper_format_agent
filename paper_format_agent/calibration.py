from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .rules import DEFAULT_RULES
from .scorer import score_document


def fit_linear(xs: list[float], ys: list[float]) -> tuple[float, float]:
    n = len(xs)
    if n == 0:
        return 1.0, 0.0
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    var_x = sum((x - mean_x) ** 2 for x in xs)
    if var_x == 0:
        return 1.0, mean_y - mean_x
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    a = cov / var_x
    b = mean_y - a * mean_x
    return a, b


def mae(pred: list[float], truth: list[float]) -> float:
    if not pred:
        return 0.0
    return sum(abs(p - t) for p, t in zip(pred, truth)) / len(pred)


def calibrate_from_labels(labels_file: str | Path, output_file: str | Path, rules: dict | None = None) -> dict[str, Any]:
    rules = rules or DEFAULT_RULES
    labels_path = Path(labels_file)
    data = json.loads(labels_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("labels file must be a JSON array")

    xs: list[float] = []
    ys: list[float] = []
    rows: list[dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        docx = item.get("docx")
        human = item.get("human_score")
        if not docx or human is None:
            continue
        report = score_document(docx, rules)
        raw = float(report["raw_quality_score"])
        xs.append(raw)
        ys.append(float(human))
        rows.append({"docx": docx, "human_score": float(human), "raw_quality_score": raw})

    a, b = fit_linear(xs, ys)
    pred_raw = xs[:]
    pred_cal = [max(0.0, min(100.0, a * x + b)) for x in xs]
    out = {
        "scale": a,
        "offset": b,
        "samples": rows,
        "mae_raw": mae(pred_raw, ys),
        "mae_calibrated": mae(pred_cal, ys),
        "target_gap_5_passed": mae(pred_cal, ys) <= 5.0,
    }
    Path(output_file).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out

