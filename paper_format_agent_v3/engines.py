from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def run_word_com_postprocess(docx_path: str | Path, timeout_ms: int = 180000) -> dict[str, Any]:
    """
    Use Word COM as a post-render engine:
    - remove paragraph list numbers/bullets metadata
    - update fields and TOC
    """
    docx_path = Path(docx_path).resolve()
    ps = rf"""
$ErrorActionPreference = "Stop"
$path = "{str(docx_path)}"
$word = $null
$doc = $null
try {{
  $word = New-Object -ComObject Word.Application
  $word.Visible = $false
  $word.DisplayAlerts = 0
  $doc = $word.Documents.Open($path, $false, $false)
  foreach ($p in $doc.Paragraphs) {{
    try {{ $p.Range.ListFormat.RemoveNumbers() | Out-Null }} catch {{ }}
  }}
  try {{ $doc.Fields.Update() | Out-Null }} catch {{ }}
  try {{
    foreach ($toc in $doc.TablesOfContents) {{
      try {{ $toc.Update() | Out-Null }} catch {{ }}
    }}
  }} catch {{ }}
  $doc.Save()
  $doc.Close()
  $word.Quit()
  Write-Output "PFA3_SUCCESS"
}} catch {{
  if ($doc -ne $null) {{ try {{ $doc.Close() }} catch {{ }} }}
  if ($word -ne $null) {{ try {{ $word.Quit() }} catch {{ }} }}
  $msg = $_.Exception.Message
  Write-Output ("PFA3_ERROR:" + $msg)
}}
"""
    cp = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
        capture_output=True,
        text=True,
        timeout=max(10, int(timeout_ms / 1000)),
    )
    out = (cp.stdout or "").strip()
    err = (cp.stderr or "").strip()
    last = out.splitlines()[-1] if out else ""
    if last == "PFA3_SUCCESS" and cp.returncode == 0:
        return {"success": True}
    if last.startswith("PFA3_ERROR:"):
        return {"success": False, "error": last[len("PFA3_ERROR:") :].strip()}
    return {"success": False, "error": err or out or "powershell failed"}


def run_libreoffice_postprocess(docx_path: str | Path, timeout_ms: int = 240000) -> dict[str, Any]:
    """
    Use LibreOffice as an alternate post-render engine.
    Round-trips DOCX -> DOCX to normalize list metadata/layout from another engine.
    """
    docx_path = Path(docx_path).resolve()
    binary = shutil.which("soffice") or shutil.which("libreoffice")
    if not binary:
        return {"success": False, "error": "libreoffice/soffice not found in PATH"}

    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td)
        cp = subprocess.run(
            [binary, "--headless", "--convert-to", "docx", "--outdir", str(out_dir), str(docx_path)],
            capture_output=True,
            text=True,
            timeout=max(10, int(timeout_ms / 1000)),
        )
        converted = out_dir / docx_path.name
        if not converted.exists():
            docx_files = sorted(out_dir.glob("*.docx"))
            if docx_files:
                converted = docx_files[0]
        if cp.returncode != 0 or not converted.exists():
            return {
                "success": False,
                "error": (cp.stderr or cp.stdout or "libreoffice conversion failed").strip(),
            }
        shutil.copy2(converted, docx_path)
    return {"success": True, "binary": binary}


def run_postprocess_engine(engine: str, docx_path: str | Path) -> dict[str, Any]:
    if engine == "python":
        return {"success": True, "engine": "python"}
    if engine == "word-com":
        r = run_word_com_postprocess(docx_path)
        return {"engine": "word-com", **r}
    if engine == "libreoffice":
        r = run_libreoffice_postprocess(docx_path)
        return {"engine": "libreoffice", **r}
    if engine == "auto":
        r_word = run_word_com_postprocess(docx_path)
        if r_word.get("success"):
            return {"engine": "word-com", "success": True, "auto_chain": ["word-com"], **r_word}
        r_lo = run_libreoffice_postprocess(docx_path)
        if r_lo.get("success"):
            return {
                "engine": "libreoffice",
                "success": True,
                "auto_chain": ["word-com", "libreoffice"],
                "fallback_from": "word-com",
                "fallback_error": r_word.get("error"),
                **r_lo,
            }
        return {
            "engine": "python",
            "success": True,
            "auto_chain": ["word-com", "libreoffice", "python"],
            "fallback_errors": {"word-com": r_word.get("error"), "libreoffice": r_lo.get("error")},
        }
    return {"success": False, "engine": engine, "error": f"unsupported engine: {engine}"}
