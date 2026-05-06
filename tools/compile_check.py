from __future__ import annotations

import py_compile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = (ROOT / "paper_format_agent", ROOT / "tools")


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for source_dir in SOURCE_DIRS:
        for path in sorted(source_dir.rglob("*.py")):
            if "__pycache__" not in path.parts:
                files.append(path)
    return files


def compile_sources() -> None:
    with tempfile.TemporaryDirectory(prefix="paper-format-compile-") as temp_dir:
        temp_path = Path(temp_dir)
        for source in iter_python_files():
            rel = source.relative_to(ROOT)
            target = temp_path / rel.with_suffix(".pyc")
            target.parent.mkdir(parents=True, exist_ok=True)
            py_compile.compile(str(source), cfile=str(target), doraise=True)


if __name__ == "__main__":
    compile_sources()
    print("Compile check OK")
