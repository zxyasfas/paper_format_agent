from __future__ import annotations

import argparse
import json

from .workflow import run_langgraph_pipeline, run_legacy_pipeline


def main():
    parser = argparse.ArgumentParser(description="Paper Format Agent MVP")
    parser.add_argument("--format-file", required=True, help="Format requirement file (.doc/.docx/.txt)")
    parser.add_argument("--paper-file", required=True, help="Input thesis paper .docx")
    parser.add_argument("--out-dir", required=True, help="Output directory")
    parser.add_argument(
        "--author-bio-file",
        default=None,
        help="Author bio source file (.txt/.docx). If omitted, author bio body will not be auto-generated.",
    )
    parser.add_argument(
        "--strict-content-fix",
        action="store_true",
        help="Enable strict structure fixes (labels/keywords/author bio/etc.)",
    )
    parser.add_argument(
        "--no-update-fields",
        action="store_true",
        help="Do not run LibreOffice field updates for TOC/page fields",
    )
    parser.add_argument(
        "--allow-content-edit",
        action="store_true",
        help="Allow content-level edits (default is format-only).",
    )

    # Workflow engine selection
    parser.add_argument(
        "--use-langgraph",
        action="store_true",
        help="Run pipeline via LangGraph state workflow.",
    )
    parser.add_argument(
        "--auto-iterate",
        action="store_true",
        help="In LangGraph mode, iterate format->score until target score or max rounds.",
    )
    parser.add_argument(
        "--target-score",
        type=float,
        default=95.0,
        help="Target score for auto iteration (LangGraph mode).",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=3,
        help="Max iteration rounds for auto-iterate (LangGraph mode).",
    )
    parser.add_argument(
        "--auto-iterate-allow-content-edit",
        action="store_true",
        help="Allow auto-iterate to escalate into content-edit strategy in later rounds.",
    )
    parser.add_argument(
        "--strategy-config",
        default=None,
        help="Optional JSON strategy config for LangGraph auto-iteration.",
    )
    parser.add_argument(
        "--perfect-mode",
        action="store_true",
        help="One-click high-strength mode: enable LangGraph + LLM + auto-iterate with content escalation.",
    )

    # LLM enhancement (DeepSeek compatible by default).
    parser.add_argument("--use-llm", action="store_true", help="Enable LLM semantic enhancement before formatting")
    parser.add_argument("--llm-api-key", default=None, help="LLM API key (default: DEEPSEEK_API_KEY env)")
    parser.add_argument("--llm-base-url", default=None, help="LLM base URL (default: https://api.deepseek.com)")
    parser.add_argument("--llm-model", default=None, help="LLM model (default: deepseek-v4-pro)")
    parser.add_argument("--llm-timeout", type=int, default=90, help="LLM request timeout seconds")
    parser.add_argument(
        "--apply-llm-content-fixes",
        action="store_true",
        help="Allow LLM to insert missing semantic sections (英文摘要/关键词等). Default is suggestions-only.",
    )
    args = parser.parse_args()

    arg_dict = vars(args)
    arg_dict["format_only"] = not bool(args.allow_content_edit)
    if args.perfect_mode:
        arg_dict["use_langgraph"] = True
        arg_dict["use_llm"] = True
        arg_dict["auto_iterate"] = True
        # Stable-first: avoid aggressive content mutation unless user explicitly enables it.
        arg_dict["auto_iterate_allow_content_edit"] = False
        arg_dict["target_score"] = max(float(arg_dict.get("target_score", 95.0)), 95.0)
        arg_dict["max_rounds"] = max(int(arg_dict.get("max_rounds", 3)), 6)

    if args.use_langgraph:
        result = run_langgraph_pipeline(arg_dict)
    else:
        result = run_legacy_pipeline(arg_dict)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
