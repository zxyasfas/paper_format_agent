from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_format_agent.release_audit import audit_release_paths  # noqa: E402


def tracked_paths() -> list[str]:
    cp = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in cp.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit tracked files before a commercial release")
    parser.add_argument("--json", action="store_true", help="write machine-readable JSON")
    args = parser.parse_args()

    findings = audit_release_paths(tracked_paths())
    payload = {
        "ok": not findings,
        "finding_count": len(findings),
        "findings": findings,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif findings:
        print("Release audit failed:")
        for item in findings:
            print(f"- {item['path']}: {item['message']}")
    else:
        print("Release audit OK")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
