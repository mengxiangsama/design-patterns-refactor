#!/usr/bin/env python3
"""Validate skill metadata and local Markdown links; not a model-quality eval."""
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]


def validate(root):
    root = root.resolve()
    skill = root / "skills" / "design-patterns-refactor"
    errors = []
    entry = skill / "SKILL.md"
    if not entry.is_file():
        return ["Missing SKILL.md"]
    text = entry.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        return ["Missing YAML frontmatter"]
    metadata = yaml.safe_load(match.group(1))
    if not isinstance(metadata, dict):
        return ["Frontmatter must be a mapping"]
    if metadata.get("name") != skill.name:
        errors.append("Skill name must match directory")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        errors.append("Invalid description")
    interface = yaml.safe_load((skill / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    interface = interface.get("interface", {})
    if "$design-patterns-refactor" not in interface.get("default_prompt", ""):
        errors.append("default_prompt must invoke this skill")
    if not 25 <= len(interface.get("short_description", "")) <= 64:
        errors.append("short_description must be 25-64 characters")
    for file in root.rglob("*.md"):
        if any(part in {".git", ".venv", "target"} for part in file.parts):
            continue
        content = file.read_text(encoding="utf-8")
        if "[TODO:" in content:
            errors.append(f"Unfinished scaffold: {file.relative_to(root)}")
        for link in re.findall(r"\]\(([^)]+)\)", content):
            link = link.strip("<>")
            parsed = urlparse(link)
            if parsed.scheme or not parsed.path:
                continue
            target = (file.parent / unquote(parsed.path)).resolve()
            # Installed skills must not depend on files outside their package.
            boundary = skill.resolve() if skill in file.parents else root
            if not target.is_relative_to(boundary) or not target.exists():
                errors.append(f"Broken or non-portable link in {file.relative_to(root)}: {link}")
    return errors


if __name__ == "__main__":
    try:
        problems = validate(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        sys.exit(1)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(1)
    print("Skill metadata and local links valid.")
