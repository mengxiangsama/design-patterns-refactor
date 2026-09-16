#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  printf '%s\n' 'Usage: bash scripts/install.sh [destination-skills-directory]' \
    'Default: ~/.agents/skills. Existing skills are never overwritten.'
  exit 0
fi
if [[ "$#" -gt 1 || ( "$#" -eq 1 && -z "$1" ) ]]; then
  printf '%s\n' 'Expected at most one non-empty destination directory.' >&2
  exit 2
fi

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$repo_dir/skills/design-patterns-refactor"
destination_root="${1:-${HOME}/.agents/skills}"
target_dir="$destination_root/design-patterns-refactor"

if [[ ! -f "$source_dir/SKILL.md" ]]; then
  printf '%s\n' 'Skill source is incomplete.' >&2
  exit 1
fi
if [[ -e "$target_dir" || -L "$target_dir" ]]; then
  printf '%s\n' "Refusing to overwrite existing skill: $target_dir" >&2
  exit 1
fi

mkdir -p -- "$destination_root"
# mkdir fails if another installation created the target meanwhile.
mkdir -- "$target_dir"
tar -C "$source_dir" --exclude=target --exclude=__pycache__ --exclude=.DS_Store -cf - . |
  tar -C "$target_dir" -xf -
printf '%s\n' "Installed: $target_dir" \
  'Use $design-patterns-refactor in Codex. Restart the client if it does not appear.'
