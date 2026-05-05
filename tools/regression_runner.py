from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_case(case: dict, output_root: Path) -> dict:
    name = case["name"]
    out_dir = output_root / name
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "paper_format_agent.cli",
        "--format-file",
        case["format_file"],
        "--paper-file",
        case["paper_file"],
        "--out-dir",
        str(out_dir),
        "--engine",
        case.get("engine", "python"),
    ]
    if case.get("strict_required_sections", False):
        cmd.append("--strict-required-sections")
    if case.get("allow_content_change", False):
        cmd.append("--allow-content-change")

    cp = subprocess.run(cmd, capture_output=True, text=True)
    result: dict = {
        "name": name,
        "ok": cp.returncode == 0,
        "returncode": cp.returncode,
        "stdout": cp.stdout[-4000:],
        "stderr": cp.stderr[-4000:],
        "out_dir": str(out_dir),
    }
    report_file = out_dir / "format_report.json"
    if not report_file.exists():
        result["ok"] = False
        result["reason"] = "missing format_report.json"
        return result

    report = json.loads(report_file.read_text(encoding="utf-8"))
    result["score_before"] = report.get("score_before")
    result["score_after"] = report.get("score_after", report.get("score"))
    result["content_changed"] = bool(report.get("content_changed", False))
    result["engine_success"] = bool(report.get("engine_report", {}).get("success", True))

    checks: list[str] = []
    min_after = case.get("min_score_after")
    if min_after is not None and float(result["score_after"]) < float(min_after):
        checks.append(f"score_after<{min_after}")

    min_impr = case.get("min_score_improvement")
    if min_impr is not None:
        before = float(result["score_before"] or 0)
        after = float(result["score_after"] or 0)
        if (after - before) < float(min_impr):
            checks.append(f"score_improvement<{min_impr}")

    if case.get("require_content_unchanged", True) and result["content_changed"]:
        checks.append("content_changed=true")
    if case.get("require_engine_success", True) and not result["engine_success"]:
        checks.append("engine_success=false")

    result["failed_checks"] = checks
    result["ok"] = result["ok"] and (len(checks) == 0)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Regression runner for Paper Format Agent")
    parser.add_argument("--manifest", required=True, help="manifest JSON path")
    parser.add_argument("--out-dir", required=True, help="regression output directory")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    cases = manifest.get("cases", [])
    if not cases:
        print(json.dumps({"error": "no cases in manifest"}, ensure_ascii=False, indent=2))
        return 2

    output_root = Path(args.out_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    results = [run_case(c, output_root) for c in cases]
    passed = sum(1 for r in results if r.get("ok"))
    summary = {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": round((passed / len(results)) * 100, 2),
        "results": results,
    }
    (output_root / "regression_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

