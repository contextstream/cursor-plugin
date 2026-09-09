"""Tests of the evidence gate. Passing fixtures are fabricated unit-test data."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import check_release as gate

class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'package'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('.git','__pycache__','.local-evidence'))
        self.evidence=Path(self.tmp.name)/'evidence'; self.evidence.mkdir()
        self.commit='a'*40
        self.report=gate.template(self.root,self.commit)
    def complete_synthetic(self):
        report=copy.deepcopy(self.report)
        for client,entry in report['clients'].items():
            entry.update(build='unit-test-only',server_version='unit-test-only',tester='synthetic',reviewer='synthetic-reviewer',recorded_at='2026-09-09T00:00:00Z',reviewed=True)
            for case,trials in entry['cases'].items():
                for i,trial in enumerate(trials):
                    name=f'{client}-{case}-{i}.txt'; content=f'SYNTHETIC UNIT TEST ONLY: {name}\n'.encode()
                    (self.evidence/name).write_bytes(content)
                    trial.update(status='pass',evidence=name,sha256=gate.digest(content))
        return report
    def check(self,report): return gate.validate_report(self.root,report,self.commit,self.evidence)
    def one_trial(self,report): return report['clients']['grok-bot']['cases']['first-brief'][0]
    def test_template_cannot_pass(self): self.assertTrue(self.check(self.report))
    def test_complete_synthetic_record_validates_structure_only(self): self.assertEqual(self.check(self.complete_synthetic()),[])
    def test_cursor_is_not_grok(self):
        report=self.complete_synthetic(); del report['clients']['grok-bot']; self.assertTrue(self.check(report))
    def test_stale_commit(self):
        report=self.complete_synthetic(); report['plugin_commit']='b'*40; self.assertTrue(self.check(report))
    def test_changed_skill_invalidates_fingerprint(self):
        report=self.complete_synthetic(); p=self.root/'skills/project-brief/SKILL.md'; p.write_text(p.read_text(encoding='utf-8')+'\nChanged\n',encoding='utf-8'); self.assertTrue(self.check(report))
    def test_changed_scenarios_invalidates_fingerprint(self):
        report=self.complete_synthetic(); p=self.root/'evaluation/scenarios.json'; p.write_text(p.read_text(encoding='utf-8')+'\n',encoding='utf-8'); self.assertTrue(self.check(report))
    def test_missing_case(self):
        report=self.complete_synthetic(); del report['clients']['grok-bot']['cases']['revoked-access']; self.assertTrue(self.check(report))
    def test_failed_trial_blocks(self):
        report=self.complete_synthetic(); self.one_trial(report)['status']='fail'; self.assertTrue(self.check(report))
    def test_insufficient_repeats(self):
        report=self.complete_synthetic(); report['clients']['grok-bot']['cases']['first-brief']=[]; self.assertTrue(self.check(report))
    def test_human_review_required(self):
        report=self.complete_synthetic(); report['clients']['grok-bot']['reviewed']='true'; self.assertTrue(self.check(report))
    def test_timestamp_timezone_required(self):
        report=self.complete_synthetic(); report['clients']['grok-bot']['recorded_at']='2026-09-09'; self.assertTrue(self.check(report))
    def test_evidence_hash_mismatch(self):
        report=self.complete_synthetic(); self.one_trial(report)['sha256']='0'*64; self.assertTrue(self.check(report))
    def test_missing_evidence(self):
        report=self.complete_synthetic(); self.one_trial(report)['evidence']='missing.txt'; self.assertTrue(self.check(report))
    def test_unsafe_paths(self):
        for path in ['../outside.txt','/etc/passwd','https://example.invalid','C:\\secret.txt']:
            with self.subTest(path=path):
                report=self.complete_synthetic(); self.one_trial(report)['evidence']=path; self.assertTrue(self.check(report))
    def test_evidence_symlink(self):
        report=self.complete_synthetic(); p=self.evidence/self.one_trial(report)['evidence']; p.unlink()
        outside=Path(self.tmp.name)/'outside'; outside.write_bytes(b'synthetic')
        try: p.symlink_to(outside)
        except OSError: self.skipTest('OS does not permit symlinks')
        self.assertTrue(self.check(report))
    def test_bad_report_types(self):
        for report in [None,[],{}, {'clients':[]}]: self.assertTrue(self.check(report))
    def test_duplicate_cases_rejected(self):
        p=self.root/'evaluation/scenarios.json'; value=json.loads(p.read_text(encoding='utf-8')); value['cases'].append(value['cases'][0]); p.write_text(json.dumps(value),encoding='utf-8')
        with self.assertRaises(ValueError): gate.catalog(self.root)
    def test_template_cli_never_overwrites(self):
        p=Path(self.tmp.name)/'report.json'; p.write_text('important',encoding='utf-8')
        run=subprocess.run([sys.executable,str(ROOT/'scripts/check_release.py'),'--root',str(self.root),'--expected-commit',self.commit,'--template',str(p)],capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,1); self.assertEqual(p.read_text(encoding='utf-8'),'important')
    def test_duplicate_evidence_does_not_count_as_fresh_trials(self):
        report=self.complete_synthetic(); trials=report['clients']['grok-bot']['cases']['first-brief']; trials[1]=copy.deepcopy(trials[0]); self.assertTrue(self.check(report))
    def test_empty_evidence_rejected(self):
        report=self.complete_synthetic(); trial=self.one_trial(report); (self.evidence/trial['evidence']).write_bytes(b''); trial['sha256']=gate.digest(b''); self.assertTrue(self.check(report))
    def test_not_run_cli_fails(self):
        p=Path(self.tmp.name)/'report.json'; p.write_text(json.dumps(self.report),encoding='utf-8')
        run=subprocess.run([sys.executable,str(ROOT/'scripts/check_release.py'),'--root',str(self.root),'--expected-commit',self.commit,'--report',str(p),'--evidence-root',str(self.evidence)],capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,1); self.assertIn('NOT RUN',run.stderr)

if __name__=='__main__': unittest.main()