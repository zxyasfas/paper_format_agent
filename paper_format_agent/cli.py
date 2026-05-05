from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

from docx import Document

from .llm import LLMConfig, generate_suggestions

from .calibration import calibrate_from_labels
from .engines import run_postprocess_engine
from .pipeline import run_pipeline
from .rules import extract_rules_from_text
from .scorer import save_reports, score_document


def read_docx_text(path: Path) -> str:
    doc = Document(path)
    out = [p.text for p in doc.paragraphs if p.text]
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                if c.text:
                    out.append(c.text)
    return "\n".join(out)


def read_format_text(path: str | Path) -> str:
    path = Path(path)
    if path.suffix.lower() == ".docx":
        return read_docx_text(path)
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td)
        try:
            subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "docx", "--outdir", str(out_dir), str(path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=90,
            )
            converted = out_dir / f"{path.stem}.docx"
            if converted.exists():
                return read_docx_text(converted)
        except Exception:
            pass
    return ""


def main():
    parser = argparse.ArgumentParser(description="Paper Format Agent V3 (type-tag first)")
    parser.add_argument("--format-file", help="格式要求文件（.doc/.docx/.txt）")
    parser.add_argument("--paper-file", help="论文文件（.docx）")
    parser.add_argument("--out-dir", required=True, help="输出目录")
    parser.add_argument(
        "--engine",
        default="auto",
        choices=["auto", "python", "word-com", "libreoffice"],
        help="排版后处理引擎",
    )
    parser.add_argument("--marker-dump", action="store_true", help="输出段落类型标注明细")
    parser.add_argument("--calibration-file", default=None, help="评分校准参数 JSON 文件")
    parser.add_argument("--strict-required-sections", action="store_true", help="严格按模板要求校验缺失章节")

    parser.add_argument("--use-llm", action="store_true", help="启用 LLM 建议（只建议，不改内容）")
    parser.add_argument("--llm-api-key", default=None)
    parser.add_argument("--llm-base-url", default="https://api.deepseek.com")
    parser.add_argument("--llm-model", default="deepseek-v4-pro")
    parser.add_argument("--llm-timeout", type=int, default=90)

    parser.add_argument("--calibrate-labels", default=None, help="校准模式：人工评分标签 JSON")
    parser.add_argument("--calibrate-out", default=None, help="校准输出 JSON（默认 out-dir/scoring_calibration.json）")

    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.calibrate_labels:
        out_file = Path(args.calibrate_out) if args.calibrate_out else (out_dir / "scoring_calibration.json")
        rules = extract_rules_from_text(read_format_text(args.format_file)) if args.format_file else extract_rules_from_text("")
        result = calibrate_from_labels(args.calibrate_labels, out_file, rules=rules)
        print(json.dumps({"calibration_file": str(out_file), **result}, ensure_ascii=False, indent=2))
        return

    if not args.format_file or not args.paper_file:
        raise ValueError("normal formatting mode requires --format-file and --paper-file")

    format_text = read_format_text(args.format_file)
    rules = extract_rules_from_text(format_text)
    (out_dir / "format_rules.json").write_text(json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")

    llm_cfg = LLMConfig(
        enabled=bool(args.use_llm),
        api_key=args.llm_api_key or os.getenv("DEEPSEEK_API_KEY"),
        base_url=args.llm_base_url,
        model=args.llm_model,
        timeout_seconds=args.llm_timeout,
    )
    llm_report = generate_suggestions(args.paper_file, format_text, llm_cfg)
    (out_dir / "llm_suggestions.json").write_text(json.dumps(llm_report, ensure_ascii=False, indent=2), encoding="utf-8")

    marker_dump = out_dir / "marker_dump.json" if args.marker_dump else None
    output_docx = out_dir / "formatted_paper_v3.docx"
    run_result = run_pipeline(args.paper_file, output_docx, rules, write_marker_dump=marker_dump)
    (out_dir / "modify_log.json").write_text(json.dumps(run_result.logs, ensure_ascii=False, indent=2), encoding="utf-8")

    engine_report = run_postprocess_engine(args.engine, output_docx)
    (out_dir / "engine_report.json").write_text(json.dumps(engine_report, ensure_ascii=False, indent=2), encoding="utf-8")

    # 排版前评分（原始论文，传入自身作为 baseline 确保评分标准一致）
    report_before = score_document(
        args.paper_file,
        rules,
        calibration_file=args.calibration_file,
        baseline_docx=args.paper_file,
        enforce_required_sections=bool(args.strict_required_sections),
    )
    
    # 排版后评分（格式化后的论文）
    report_after = score_document(
        output_docx,
        rules,
        calibration_file=args.calibration_file,
        baseline_docx=args.paper_file,
        enforce_required_sections=bool(args.strict_required_sections),
    )
    
    # 合并报告
    report = report_after.copy()
    report["score_before"] = round(report_before["score"], 1)
    report["score_after"] = round(report_after["score"], 1)
    report["score_improvement"] = round(report_after["score"] - report_before["score"], 1)
    report["chars_no_space_before"] = report_before["chars_no_space"]
    report["chars_no_space_after"] = report_after["chars_no_space"]
    report["llm_used"] = bool(llm_report.get("used"))
    report["llm_warnings"] = llm_report.get("warnings", [])
    report["engine_report"] = engine_report
    report["removed_numpr_count"] = run_result.removed_numpr_count
    report["classification_confidence"] = run_result.classification_confidence
    save_reports(report, out_dir / "format_report.json", out_dir / "format_report.html")

    print(
        json.dumps(
            {
                "output": str(output_docx),
                "score_before": report["score_before"],
                "score_after": report["score_after"],
                "score_improvement": report["score_improvement"],
                "raw_quality_score": report.get("raw_quality_score"),
                "chars_no_space_before": report["chars_no_space_before"],
                "chars_no_space_after": report["chars_no_space_after"],
                "removed_numpr_count": run_result.removed_numpr_count,
                "engine": engine_report.get("engine", args.engine),
                "engine_success": bool(engine_report.get("success")),
                "llm_used": bool(llm_report.get("used")),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
