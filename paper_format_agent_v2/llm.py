from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request

from docx import Document


@dataclass
class LLMConfig:
    enabled: bool = False
    api_key: str | None = None
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-v4-pro"
    timeout_seconds: int = 90


def _extract_sample_text(docx_path: str | Path) -> str:
    doc = Document(str(docx_path))
    parts = []
    for p in doc.paragraphs:
        t = (p.text or "").strip()
        if t:
            parts.append(t)
        if len("\n".join(parts)) > 5000:
            break
    return "\n".join(parts)


def _call_openai_compatible(cfg: LLMConfig, prompt: str) -> dict[str, Any]:
    body = {
        "model": cfg.model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "Output strict JSON only."},
            {"role": "user", "content": prompt},
        ],
    }
    req = request.Request(
        cfg.base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg.api_key}",
        },
    )
    with request.urlopen(req, timeout=cfg.timeout_seconds) as resp:
        raw = resp.read().decode("utf-8")
    payload = json.loads(raw)
    content = payload["choices"][0]["message"]["content"]
    if isinstance(content, list):
        text = "".join(x.get("text", "") for x in content if isinstance(x, dict))
    else:
        text = str(content)
    return json.loads(text)


def generate_suggestions(paper_file: str | Path, format_text: str, cfg: LLMConfig) -> dict[str, Any]:
    report: dict[str, Any] = {
        "enabled": cfg.enabled,
        "used": False,
        "model": cfg.model,
        "base_url": cfg.base_url,
        "warnings": [],
        "suggestions": {},
    }
    if not cfg.enabled:
        return report
    if not cfg.api_key:
        report["warnings"].append("LLM API key missing.")
        return report

    sample = _extract_sample_text(paper_file)
    prompt = (
        "给出论文格式修复建议，返回 JSON: "
        '{"missing_sections":[string], "ordering_advice":[string], "style_risks":[string], "keyword_suggestions":[string]}'
        "\n不要改写正文，不要输出 markdown。\n"
        f"\n格式要求节选:\n{(format_text or '')[:3500]}\n"
        f"\n论文内容节选:\n{sample[:5000]}"
    )
    try:
        result = _call_openai_compatible(cfg, prompt)
        report["used"] = True
        report["suggestions"] = result
    except error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        report["warnings"].append(f"HTTP {e.code}: {detail[:300]}")
    except Exception as e:
        report["warnings"].append(str(e))
    return report

