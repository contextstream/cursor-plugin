"""Structural and negative-case tests; no claims about live agent behavior."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "scripts/validate_plugin.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "package"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv"))

    def edit_json(self, path, mutate):
        file = self.root / path
        value = json.loads(file.read_text(encoding="utf-8"))
        mutate(value)
        file.write_text(json.dumps(value), encoding="utf-8")

    def fails_with(self, fragment):
        self.assertTrue(any(fragment in item for item in validator.validate(self.root)), fragment)

    def test_valid_package(self):
        self.assertEqual(validator.validate(self.root), [])

    def test_missing_manifest(self):
        (self.root / ".cursor-plugin/plugin.json").unlink()
        self.fails_with("invalid or missing JSON")

    def test_invalid_json(self):
        (self.root / "mcp.json").write_text("{", encoding="utf-8")
        self.fails_with("invalid or missing JSON")

    def test_non_object_manifest(self):
        (self.root / ".cursor-plugin/plugin.json").write_text("[]", encoding="utf-8")
        self.fails_with("manifest must be an object")

    def test_identity_not_renamed(self):
        self.edit_json(".cursor-plugin/plugin.json", lambda m: m.update(name="unrelated-plugin"))
        self.fails_with("identity")

    def test_semver(self):
        self.edit_json(".cursor-plugin/plugin.json", lambda m: m.update(version="next"))
        self.fails_with("semver")

    def test_missing_component_path(self):
        self.edit_json(".cursor-plugin/plugin.json", lambda m: m.pop("skills"))
        self.fails_with("skills must use")

    def test_unexpected_mcp_host(self):
        self.edit_json("mcp.json", lambda m: m["mcpServers"]["contextstream"].update(url="https://example.invalid/mcp"))
        self.fails_with("MCP must contain only")

    def test_mcp_credentials_rejected(self):
        self.edit_json("mcp.json", lambda m: m["mcpServers"]["contextstream"].update(headers={"Authorization": "synthetic-test-value"}))
        self.fails_with("no credentials")

    def test_executable_transport_rejected(self):
        self.edit_json("mcp.json", lambda m: m["mcpServers"]["contextstream"].update(command="example-only"))
        self.fails_with("no credentials, commands")

    def test_missing_skill(self):
        (self.root / "skills/project-brief/SKILL.md").unlink()
        self.fails_with("three documented skill directories")

    def test_skill_name_matches_folder(self):
        p = self.root / "skills/project-brief/SKILL.md"
        p.write_text(p.read_text().replace('name: "project-brief"', 'name: "wrong-name"'), encoding="utf-8")
        self.fails_with("name must match")

    def test_missing_frontmatter(self):
        (self.root / "skills/decision-check/SKILL.md").write_text("# Missing metadata\n", encoding="utf-8")
        self.fails_with("opening frontmatter")

    def test_prompt_contract_is_documented(self):
        p = self.root / "skills/project-handoff/SKILL.md"
        p.write_text(p.read_text().replace("explicit approval", "approval"), encoding="utf-8")
        self.fails_with("missing documented contract")

    def test_missing_bot_profile(self):
        (self.root / "bots/project-brief-handoff.md").unlink()
        self.fails_with("bots/project-brief-handoff.md")

    def test_broken_relative_link(self):
        p = self.root / "README.md"
        p.write_text(p.read_text() + "\n[broken](docs/missing.md)\n", encoding="utf-8")
        self.fails_with("broken local link")

    def test_escaping_link(self):
        p = self.root / "README.md"
        p.write_text(p.read_text() + "\n[escape](../outside.md)\n", encoding="utf-8")
        self.fails_with("escapes the repository")

    def test_remote_logo_unexpected_host(self):
        self.edit_json(".cursor-plugin/plugin.json", lambda m: m.update(logo="https://example.invalid/logo.png"))
        self.fails_with("unexpected external logo")

    def test_local_logo_path_escape(self):
        self.edit_json(".cursor-plugin/plugin.json", lambda m: m.update(logo="../logo.svg"))
        self.fails_with("logo must be")

    def test_local_logo_symlink_escape(self):
        outside = Path(self.temp.name) / "outside.svg"
        outside.write_text("<svg/>", encoding="utf-8")
        (self.root / "logo.svg").symlink_to(outside)
        self.edit_json(".cursor-plugin/plugin.json", lambda m: m.update(logo="logo.svg"))
        self.fails_with("logo must be")

    def test_rule_boolean_not_string(self):
        p = self.root / "rules/contextstream.mdc"
        p.write_text(p.read_text().replace("alwaysApply: true", 'alwaysApply: "true"'), encoding="utf-8")
        self.fails_with("alwaysApply: true")

    def test_cli_failure_exit_code(self):
        (self.root / "mcp.json").write_text("null", encoding="utf-8")
        run = subprocess.run([sys.executable, str(ROOT / "scripts/validate_plugin.py"), "--root", str(self.root)], capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 1)
        self.assertIn("ERROR:", run.stderr)


class FrontmatterTests(unittest.TestCase):
    def test_quoted_colon(self):
        metadata, body = validator.frontmatter('---\nname: "test"\ndescription: "Includes: a colon"\n---\nBody')
        self.assertEqual(metadata["description"], "Includes: a colon")
        self.assertEqual(body, "Body")

    def test_duplicate_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validator.frontmatter('---\nname: "a"\nname: "b"\n---\nBody')

    def test_missing_close_rejected(self):
        with self.assertRaisesRegex(ValueError, "closing"):
            validator.frontmatter('---\nname: "a"\nBody')

    def test_complex_yaml_rejected(self):
        with self.assertRaises(ValueError):
            validator.frontmatter('---\nname: ["a"]\n---\nBody')

    def test_empty_body_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            validator.frontmatter('---\nname: "a"\n---\n')


if __name__ == "__main__":
    unittest.main()
