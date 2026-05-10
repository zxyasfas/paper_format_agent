from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

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


def local_paths() -> list[str]:
    paths: set[str] = set()
    commands = [
        ["git", "ls-files", "--others", "--exclude-standard"],
        ["git", "ls-files", "--others", "--ignored", "--exclude-standard"],
    ]
    for command in commands:
        cp = subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        paths.update(line.strip() for line in cp.stdout.splitlines() if line.strip())
    return sorted(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit tracked files before a commercial release")
    parser.add_argument("--json", action="store_true", help="write machine-readable JSON")
    parser.add_argument(
        "--include-local",
        action="store_true",
        help="also audit untracked and ignored local files before publishing",
    )
    args = parser.parse_args()

    paths = tracked_paths()
    if args.include_local:
        paths = sorted(set(paths) | set(local_paths()))

    findings = audit_release_paths(paths)
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
        if args.include_local:
            print("Tip: --include-local includes untracked and ignored workspace files.")
    else:
        print("Release audit OK")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
