"""Structural/negative-case tests; no claims about live agent behavior."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import validate_plugin as validator

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'package'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('.git','__pycache__','.venv','.local-evidence'))
    def edit_json(self,path,mutate):
        p=self.root/path; value=json.loads(p.read_text(encoding='utf-8')); mutate(value)
        p.write_text(json.dumps(value),encoding='utf-8')
    def fails_with(self,fragment):
        self.assertTrue(any(fragment in e for e in validator.validate(self.root)),fragment)
    def test_valid_package(self):
        self.assertEqual(validator.validate(self.root),[])
    def test_missing_manifest(self):
        (self.root/'.cursor-plugin/plugin.json').unlink(); self.fails_with('invalid or missing JSON')
    def test_invalid_json(self):
        (self.root/'mcp.json').write_text('{',encoding='utf-8'); self.fails_with('invalid or missing JSON')
    def test_non_object_manifest(self):
        (self.root/'.cursor-plugin/plugin.json').write_text('[]',encoding='utf-8'); self.fails_with('manifest must be an object')
    def test_identity_not_renamed(self):
        self.edit_json('.cursor-plugin/plugin.json',lambda m:m.update(name='unrelated')); self.fails_with('identity')
    def test_semver(self):
        self.edit_json('.cursor-plugin/plugin.json',lambda m:m.update(version='next')); self.fails_with('semver')
    def test_missing_component_path(self):
        self.edit_json('.cursor-plugin/plugin.json',lambda m:m.pop('skills')); self.fails_with('skills must use')
    def test_unexpected_mcp_host(self):
        self.edit_json('mcp.json',lambda m:m['mcpServers']['contextstream'].update(url='https://example.invalid/mcp')); self.fails_with('MCP must contain only')
    def test_mcp_credentials_rejected(self):
        self.edit_json('mcp.json',lambda m:m['mcpServers']['contextstream'].update(headers={'Authorization':'synthetic-test-value'})); self.fails_with('no credentials')
    def test_executable_transport_rejected(self):
        self.edit_json('mcp.json',lambda m:m['mcpServers']['contextstream'].update(command='example-only')); self.fails_with('no credentials, commands')
    def test_missing_skill(self):
        (self.root/'skills/project-brief/SKILL.md').unlink(); self.fails_with('seven documented skill directories')
    def test_skill_name_matches_folder(self):
        p=self.root/'skills/project-brief/SKILL.md'; p.write_text(p.read_text(encoding='utf-8').replace('name: "project-brief"','name: "wrong-name"'),encoding='utf-8'); self.fails_with('name must match')
    def test_missing_frontmatter(self):
        (self.root/'skills/decision-check/SKILL.md').write_text('# Missing metadata\n',encoding='utf-8'); self.fails_with('opening frontmatter')
    def test_prompt_contract_is_documented(self):
        p=self.root/'skills/project-handoff/SKILL.md'; p.write_text(p.read_text(encoding='utf-8').replace('explicit approval','approval'),encoding='utf-8'); self.fails_with('missing documented contract')
    def test_missing_bot_profile(self):
        (self.root/'bots/project-brief-handoff.md').unlink(); self.fails_with('bots/project-brief-handoff.md')
    def test_broken_relative_link(self):
        p=self.root/'README.md'; p.write_text(p.read_text(encoding='utf-8')+'\n[broken](docs/missing.md)\n',encoding='utf-8'); self.fails_with('broken local link')
    def test_escaping_link(self):
        p=self.root/'README.md'; p.write_text(p.read_text(encoding='utf-8')+'\n[escape](../outside.md)\n',encoding='utf-8'); self.fails_with('escapes the repository')
    def test_remote_logo_unexpected_host(self):
        self.edit_json('.cursor-plugin/plugin.json',lambda m:m.update(logo='https://example.invalid/logo.png')); self.fails_with('unexpected external logo')
    def test_local_logo_path_escape(self):
        self.edit_json('.cursor-plugin/plugin.json',lambda m:m.update(logo='../logo.svg')); self.fails_with('logo must be')
    def test_local_logo_symlink_escape(self):
        outside=Path(self.temp.name)/'outside.svg'; outside.write_text('<svg/>',encoding='utf-8')
        try: (self.root/'logo.svg').symlink_to(outside)
        except OSError: self.skipTest('OS does not permit creating symlinks')
        self.edit_json('.cursor-plugin/plugin.json',lambda m:m.update(logo='logo.svg')); self.fails_with('logo must be')
    def test_rule_boolean_not_string(self):
        p=self.root/'rules/contextstream.mdc'; p.write_text(p.read_text(encoding='utf-8').replace('alwaysApply: true','alwaysApply: "true"'),encoding='utf-8'); self.fails_with('alwaysApply: true')
    def test_cli_failure_exit_code(self):
        (self.root/'mcp.json').write_text('null',encoding='utf-8')
        run=subprocess.run([sys.executable,str(ROOT/'scripts/validate_plugin.py'),'--root',str(self.root)],capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,1); self.assertIn('ERROR:',run.stderr)
    def test_duplicate_json_rejected(self):
        p=self.root/'.cursor-plugin/plugin.json'; p.write_text('{"name":"contextstream","name":"contextstream"}',encoding='utf-8'); self.fails_with('invalid or missing JSON')
    def test_new_executable_components_need_review(self):
        self.edit_json('.cursor-plugin/plugin.json',lambda m:m.update(hooks='hooks.json')); self.fails_with('unreviewed component')
    def test_nested_skill_not_silently_ignored(self):
        p=self.root/'skills/extra/nested/SKILL.md'; p.parent.mkdir(parents=True); p.write_text('extra',encoding='utf-8'); self.fails_with('seven documented')
    def test_skill_size_budget(self):
        p=self.root/'skills/project-brief/SKILL.md'; p.write_text(p.read_text(encoding='utf-8')+'x'*7000,encoding='utf-8'); self.fails_with('size budget')
    def test_missing_scenario_catalog(self):
        (self.root/'evaluation/scenarios.json').unlink(); self.fails_with('scenario catalog')
    def test_missing_skill_evaluation(self):
        self.edit_json('evaluation/scenarios.json',lambda m:m.update(cases=[c for c in m['cases'] if c['skill']!='memory-review'])); self.fails_with('all skills need')
    def test_invalid_metadata_types(self):
        self.edit_json('.cursor-plugin/plugin.json',lambda m:m.update(description=[],keywords=[{}],author=[],version=[])); self.fails_with('description is required')
    def test_unsupported_link_scheme(self):
        p=self.root/'README.md'; p.write_text(p.read_text(encoding='utf-8')+'\n[bad](javascript:alert)\n',encoding='utf-8'); self.fails_with('repository-relative')

class FrontmatterTests(unittest.TestCase):
    def test_quoted_colon(self):
        m,body=validator.frontmatter('---\nname: "test"\ndescription: "Includes: a colon"\n---\nBody')
        self.assertEqual(m['description'],'Includes: a colon'); self.assertEqual(body,'Body')
    def test_duplicate_key_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate'): validator.frontmatter('---\nname: "a"\nname: "b"\n---\nBody')
    def test_missing_close_rejected(self):
        with self.assertRaisesRegex(ValueError,'closing'): validator.frontmatter('---\nname: "a"\nBody')
    def test_complex_yaml_rejected(self):
        with self.assertRaises(ValueError): validator.frontmatter('---\nname: ["a"]\n---\nBody')
    def test_empty_body_rejected(self):
        with self.assertRaisesRegex(ValueError,'empty'): validator.frontmatter('---\nname: "a"\n---\n')

if __name__=='__main__': unittest.main()