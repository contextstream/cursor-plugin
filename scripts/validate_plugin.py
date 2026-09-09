#!/usr/bin/env python3
"""Offline checks for this package, not a full Cursor schema or runtime audit.

Frontmatter deliberately uses only JSON-quoted strings and booleans (a YAML
subset). No network access, third-party dependencies, or credentials required.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote, urlsplit

ENDPOINT = "https://mcp.contextstream.io/mcp"
SKILLS = ("project-brief", "decision-check", "project-handoff")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")
LINK = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)")


def local_path(root: Path, value: str, parent: Path | None = None) -> Path:
    """Resolve a repository-local path, rejecting external and escaped targets."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("expected a nonempty POSIX path")
    if urlsplit(value).scheme or PurePosixPath(value).is_absolute():
        raise ValueError("expected a repository-relative path")
    target = ((parent or root) / value).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError("path escapes the repository")
    return target


def read_text(root: Path, value: str) -> str:
    return local_path(root, value).read_text(encoding="utf-8")


def frontmatter(text: str) -> tuple[dict[str, object], str]:
    """Parse this repository's explicitly restricted YAML-frontmatter subset."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing frontmatter delimiter") from exc
    result: dict[str, object] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, separator, raw = line.partition(":")
        if not separator or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", key):
            raise ValueError("frontmatter keys must be simple scalar fields")
        if key in result:
            raise ValueError(f"duplicate frontmatter field: {key}")
        value = json.loads(raw.strip())
        if not isinstance(value, (str, bool)):
            raise ValueError("frontmatter supports only quoted strings and booleans")
        result[key] = value
    body = "\n".join(lines[end + 1:]).strip()
    if not body:
        raise ValueError("empty Markdown body")
    return result, body


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    def load_json(name: str) -> object | None:
        try:
            return json.loads(read_text(root, name))
        except (OSError, ValueError) as exc:
            errors.append(f"{name}: invalid or missing JSON ({type(exc).__name__})")
            return None

    manifest = load_json(".cursor-plugin/plugin.json")
    if not isinstance(manifest, dict):
        errors.append("plugin manifest must be an object")
    else:
        check(manifest.get("name") == "contextstream", "plugin identity must remain contextstream")
        version = manifest.get("version")
        check(isinstance(version, str) and bool(VERSION.fullmatch(version)), "version must be stable semver")
        check(isinstance(manifest.get("description"), str) and bool(manifest["description"].strip()), "description is required")
        author = manifest.get("author")
        check(isinstance(author, dict) and author.get("name") == "ContextStream", "author must identify ContextStream")
        check(manifest.get("repository") == "https://github.com/contextstream/cursor-plugin", "unexpected repository URL")
        check(manifest.get("homepage") == "https://contextstream.io", "unexpected homepage")
        check(manifest.get("license") == "MIT", "package license must remain MIT")
        keywords = manifest.get("keywords")
        check(isinstance(keywords, list) and bool(keywords) and all(isinstance(k, str) and k.strip() for k in keywords), "keywords must be nonempty strings")
        for field, expected in (("rules", "./rules/"), ("skills", "./skills/"), ("mcpServers", "mcp.json")):
            check(manifest.get(field) == expected, f"{field} must use {expected}")
        logo = manifest.get("logo")
        if isinstance(logo, str) and logo.startswith("https://"):
            check(logo == "https://contextstream.io/logo-hex.png", "unexpected external logo URL")
        else:
            try:
                check(local_path(root, logo).is_file(), "local logo does not exist")
            except (TypeError, ValueError, OSError):
                errors.append("logo must be the existing HTTPS asset or a repository-local file")

    mcp = load_json("mcp.json")
    # Pin this package's intentionally credential-free transport contract. Extra
    # headers, env, commands, or alternate servers need a deliberate review.
    check(mcp == {"mcpServers": {"contextstream": {"url": ENDPOINT}}},
          "MCP must contain only the hosted ContextStream URL; no credentials, commands, or extra servers")

    expected = {f"skills/{name}/SKILL.md" for name in SKILLS}
    discovered = {p.relative_to(root).as_posix() for p in (root / "skills").glob("*/SKILL.md")}
    check(discovered == expected, "expected exactly the three documented skill directories")
    for relative in sorted(expected):
        try:
            metadata, body = frontmatter(read_text(root, relative))
            name = metadata.get("name")
            check(isinstance(name, str) and bool(SLUG.fullmatch(name)) and name == Path(relative).parent.name,
                  f"{relative}: name must match its directory")
            check(isinstance(metadata.get("description"), str) and bool(metadata["description"].strip()),
                  f"{relative}: description is required")
            # Documentation regression checks only; these do not prove that an
            # agent follows the policy or that the backend enforces permissions.
            for phrase in ("## Scope and data handling", "## Evidence and permissions", "explicit approval", "transcript", "untrusted"):
                check(phrase in body, f"{relative}: missing documented contract: {phrase}")
        except (OSError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")

    try:
        metadata, _ = frontmatter(read_text(root, "rules/contextstream.mdc"))
        check(metadata.get("alwaysApply") is True, "Cursor rule must retain alwaysApply: true")
        check(isinstance(metadata.get("description"), str) and bool(metadata["description"].strip()), "Cursor rule needs a description")
    except (OSError, ValueError) as exc:
        errors.append(f"rules/contextstream.mdc: {exc}")

    for required in ("README.md", "LICENSE", "bots/project-brief-handoff.md", "docs/grok-bot.md", "docs/data-handling.md",
                     "docs/manual-validation.md", "docs/marketplace-launch.md", "examples/harbor-export/README.md"):
        try:
            check(bool(read_text(root, required).strip()), f"{required}: empty file")
        except (OSError, ValueError) as exc:
            errors.append(f"{required}: {exc}")

    # Check simple inline links used by this repository. Remote destinations and
    # anchors are not fetched/validated. Ignore generated and version-control dirs.
    for path in sorted(root.rglob("*.md")):
        if any(part in (".git", ".venv", "__pycache__") for part in path.relative_to(root).parts):
            continue
        relative = path.relative_to(root).as_posix()
        try:
            text = read_text(root, relative)
            for target in LINK.findall(text):
                parsed = urlsplit(target)
                if parsed.scheme in ("https", "http", "mailto") or not parsed.path:
                    continue
                candidate = local_path(root, unquote(parsed.path), path.parent)
                check(candidate.exists(), f"{relative}: broken local link: {target}")
        except (OSError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("PASS: plugin package, MCP configuration, three skills, rule, and local documentation links")
    print("Not checked: live clients, OAuth, authorization, external links, or marketplace approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
