from __future__ import annotations

import argparse
import json
from pathlib import Path

from .batch import discover_paper_files, make_case_output_dir, summarize_batch
from .calibration import calibrate_from_labels
from .rules import extract_rules_from_text
from .service import format_paper, read_docx_text, read_format_text

# read_docx_text / read_format_text are re-exported for backward compatibility
# (gui.py imports read_format_text from here).
__all__ = ["read_docx_text", "read_format_text", "build_parser", "run_format_job", "run_batch", "main"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Paper Format Agent CLI")
    parser.add_argument("--format-file", help="format requirement file (.doc/.docx/.txt)")
    parser.add_argument("--paper-file", help="paper file (.docx)")
    parser.add_argument("--paper-dir", help="directory of paper .docx files for batch processing")
    parser.add_argument("--paper-glob", default="*.docx", help="batch discovery glob, default: *.docx")
    parser.add_argument("--batch-fail-fast", action="store_true", help="stop batch processing after the first failure")
    parser.add_argument("--out-dir", required=True, help="output directory")
    parser.add_argument(
        "--engine",
        default="auto",
        choices=["auto", "python", "word-com", "libreoffice"],
        help="post-process engine",
    )
    parser.add_argument("--marker-dump", action="store_true", help="write paragraph type markers to marker_dump.json")
    parser.add_argument("--calibration-file", default=None, help="scoring calibration JSON")
    parser.add_argument("--strict-required-sections", action="store_true", help="enforce required sections from format file")
    parser.add_argument(
        "--allow-content-change",
        action="store_true",
        help="allow content fingerprint changes (NOT recommended for production)",
    )

    parser.add_argument("--use-llm", action="store_true", help="enable LLM suggestions (advisory only)")
    parser.add_argument("--llm-api-key", default=None)
    parser.add_argument("--llm-base-url", default="https://api.deepseek.com")
    parser.add_argument("--llm-model", default="deepseek-v4-pro")
    parser.add_argument("--llm-timeout", type=int, default=90)

    parser.add_argument("--calibrate-labels", default=None, help="manual labels JSON for calibration")
    parser.add_argument("--calibrate-out", default=None, help="output calibration JSON path")
    return parser


def run_format_job(args: argparse.Namespace, format_text: str, rules: dict, paper_file: str | Path, out_dir: Path) -> dict:
    return format_paper(
        paper_file,
        out_dir,
        format_text=format_text,
        rules=rules,
        engine=args.engine,
        strict_required_sections=bool(args.strict_required_sections),
        allow_content_change=bool(args.allow_content_change),
        marker_dump=bool(args.marker_dump),
        calibration_file=args.calibration_file,
        use_llm=bool(args.use_llm),
        llm_api_key=args.llm_api_key,
        llm_base_url=args.llm_base_url,
        llm_model=args.llm_model,
        llm_timeout=args.llm_timeout,
    )


def run_batch(args: argparse.Namespace, format_text: str, rules: dict, out_dir: Path) -> int:
    if not args.paper_dir:
        raise ValueError("batch mode requires --paper-dir")

    paper_dir = Path(args.paper_dir)
    papers = discover_paper_files(paper_dir, args.paper_glob)
    if not papers:
        summary = summarize_batch([])
        summary["error"] = f"no .docx papers found in {paper_dir}"
        (out_dir / "batch_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 2

    results: list[dict] = []
    for paper in papers:
        case_out_dir = make_case_output_dir(out_dir, paper, paper_dir)
        try:
            result = run_format_job(args, format_text, rules, paper, case_out_dir)
            result["ok"] = not bool(result.get("content_changed")) and bool(result.get("engine_success"))
        except Exception as exc:
            result = {
                "paper_file": str(paper),
                "out_dir": str(case_out_dir),
                "ok": False,
                "error": str(exc),
            }
            if args.batch_fail_fast:
                results.append(result)
                break
        results.append(result)

    summary = summarize_batch(results)
    (out_dir / "batch_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["failed"] == 0 else 1


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.calibrate_labels:
        out_file = Path(args.calibrate_out) if args.calibrate_out else (out_dir / "scoring_calibration.json")
        rules = extract_rules_from_text(read_format_text(args.format_file)) if args.format_file else extract_rules_from_text("")
        result = calibrate_from_labels(args.calibrate_labels, out_file, rules=rules)
        print(json.dumps({"calibration_file": str(out_file), **result}, ensure_ascii=False, indent=2))
        return 0

    if args.paper_file and args.paper_dir:
        raise ValueError("use either --paper-file or --paper-dir, not both")
    if not args.format_file:
        raise ValueError("formatting mode requires --format-file")

    format_text = read_format_text(args.format_file)
    rules = extract_rules_from_text(format_text)

    if args.paper_dir:
        return run_batch(args, format_text, rules, out_dir)

    if not args.paper_file:
        raise ValueError("normal formatting mode requires --paper-file")

    result = run_format_job(args, format_text, rules, args.paper_file, out_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
