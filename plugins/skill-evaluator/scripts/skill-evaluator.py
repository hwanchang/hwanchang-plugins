#!/usr/bin/env python3
"""
Forced Eval Hook for Claude Code Skills
Forces explicit skill evaluation before implementation

Scans:
- User global skills (~/.claude/skills/)
- Installed plugins' skills (~/.claude/plugins/...)

Guarantees:
- Always outputs SKILL-ACTIVATION-PROTOCOL or exits with error
- Handles missing directories, files, malformed YAML
"""

import json
import sys
from pathlib import Path


def get_user_skills_dir() -> Path:
    """Get user global skills directory (~/.claude/skills/)."""
    return Path.home() / ".claude" / "skills"


def get_installed_plugins() -> list[tuple[str, Path]]:
    """Get all installed plugins from ~/.claude/plugins/installed_plugins.json.

    Returns list of (plugin_name, install_path) tuples.
    """
    plugins_file = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    if not plugins_file.exists():
        return []

    try:
        data = json.loads(plugins_file.read_text(encoding="utf-8"))
        plugins = data.get("plugins", {})

        result = []
        for plugin_key, installs in plugins.items():
            # plugin_key format: "plugin-name@marketplace"
            plugin_name = plugin_key.split("@")[0]

            # Get the first (usually only) installation
            if installs and isinstance(installs, list) and len(installs) > 0:
                install_path = installs[0].get("installPath")
                if install_path:
                    result.append((plugin_name, Path(install_path)))

        return result
    except Exception:
        return []


def extract_skill_info(skill_file: Path) -> tuple[str, str] | None:
    """Extract name and description from SKILL.md frontmatter."""
    try:
        content = skill_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        name = None
        description = None
        in_frontmatter = False

        for line in lines:
            stripped = line.strip()
            if stripped == "---":
                if in_frontmatter:
                    break  # End of frontmatter
                in_frontmatter = True
                continue

            if in_frontmatter:
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip().strip("'\"")
                elif line.startswith("description:"):
                    description = line.split(":", 1)[1].strip().strip("'\"")
                    # Truncate long descriptions
                    if len(description) > 100:
                        description = description[:97] + "..."

        if name:
            return (name, description or "")
    except Exception:
        pass
    return None


def get_all_skills(skills_dir: Path) -> list[tuple[str, str]]:
    """Get all skill (name, description) tuples from skills directory."""
    skills = []

    if not skills_dir.exists() or not skills_dir.is_dir():
        return skills

    for item in sorted(skills_dir.iterdir()):
        if not item.is_dir():
            continue

        skill_file = item / "SKILL.md"
        if not skill_file.exists():
            continue

        info = extract_skill_info(skill_file)
        if info:
            skills.append(info)

    return skills


def format_skill_section(title: str, skills: list[tuple[str, str]]) -> str:
    """Format a section of skills with title."""
    if not skills:
        return ""

    skill_lines = []
    for name, desc in skills:
        if desc:
            skill_lines.append(f"- **{name}**: {desc}")
        else:
            skill_lines.append(f"- **{name}**")

    return f"## {title}\n" + "\n".join(skill_lines)


def main() -> int:
    """Main entry point. Returns exit code."""
    # Collect skills from multiple sources

    # 1. User global skills (~/.claude/skills/)
    user_skills = get_all_skills(get_user_skills_dir())

    # 2. Installed plugins' skills (~/.claude/plugins/cache/...)
    installed_plugin_skills: dict[str, list[tuple[str, str]]] = {}
    for plugin_name, install_path in get_installed_plugins():
        skills_dir = install_path / "skills"
        skills = get_all_skills(skills_dir)
        if skills:
            installed_plugin_skills[plugin_name] = skills

    total_skills = len(user_skills) + sum(len(s) for s in installed_plugin_skills.values())

    if total_skills == 0:
        print("[ERROR] skill-forced-eval: No skills found", file=sys.stderr)
        return 1

    # Build sections
    sections = []
    if user_skills:
        sections.append(format_skill_section("Available Skills (user global)", user_skills))
    for plugin_name, skills in sorted(installed_plugin_skills.items()):
        sections.append(format_skill_section(f"Available Skills ({plugin_name})", skills))

    skills_output = "\n\n".join(sections)

    print(f"""<SKILL-ACTIVATION-PROTOCOL>

{skills_output}

## MANDATORY 3-Step Evaluation

**Step 1 - EVALUATE**: List each skill → YES/NO (brief reason)
**Step 2 - ACTIVATE**: IF any YES → Skill("[name]") for each. IF all NO → "No skills needed"
**Step 3 - IMPLEMENT**: Only after Step 2 complete.

⚠️ CRITICAL: Evaluation without activation is WORTHLESS.

</SKILL-ACTIVATION-PROTOCOL>""")

    return 0


if __name__ == "__main__":
    sys.exit(main())
