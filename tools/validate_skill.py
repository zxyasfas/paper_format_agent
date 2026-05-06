from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise AssertionError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise AssertionError("SKILL.md frontmatter must end with ---")
    block = text[4:end]
    data: dict[str, str] = {}
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise AssertionError(f"Invalid frontmatter line: {raw_line}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def validate_skill() -> None:
    skill_path = ROOT / "SKILL.md"
    agent_meta_path = ROOT / "agents" / "openai.yaml"

    if not skill_path.exists():
        raise AssertionError("Missing top-level SKILL.md")
    if not agent_meta_path.exists():
        raise AssertionError("Missing agents/openai.yaml")

    skill = _read(skill_path)
    frontmatter = _frontmatter(skill)
    if frontmatter.get("name") != "paper-format-agent":
        raise AssertionError("SKILL.md name must be paper-format-agent")
    description = frontmatter.get("description", "")
    for phrase in ("inspect", "repair", "DOCX"):
        if phrase not in description:
            raise AssertionError(f"SKILL.md description should mention {phrase!r}")

    body = skill.split("\n---\n", 2)[-1]
    for required in ("Standard Workflow", "Validation", "content_changed", "Contribution-Friendly Tasks"):
        if required not in body:
            raise AssertionError(f"SKILL.md body is missing {required!r}")

    agent_meta = _read(agent_meta_path)
    for required in ("display_name:", "short_description:", "default_prompt:"):
        if required not in agent_meta:
            raise AssertionError(f"agents/openai.yaml is missing {required}")


if __name__ == "__main__":
    validate_skill()
    print("Skill metadata OK")
