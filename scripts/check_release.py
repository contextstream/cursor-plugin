#!/usr/bin/env python3
"""Fail-closed acceptance-record check, not an execution or truth verifier.

No network or publication. Evidence must be collected in actual clients and
reviewed by a human. Unit tests intentionally use synthetic evidence.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CLIENTS = ('cursor', 'grok-bot')
SHA = re.compile(r'[a-f0-9]{40}\Z')
HASH = re.compile(r'[a-f0-9]{64}\Z')
MAX_FILE = 4 * 1024 * 1024

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_json(path):
    with path.open('rb') as f:
        raw = f.read(MAX_FILE + 1)
    if len(raw) > MAX_FILE:
        raise ValueError('JSON file exceeds size limit')
    def unique(pairs):
        obj = {}
        for key,value in pairs:
            if key in obj:
                raise ValueError('Duplicate JSON key')
            obj[key] = value
        return obj
    return json.loads(raw, object_pairs_hook=unique)

def fingerprint(root):
    files = [root/'mcp.json']
    for folder in ('.cursor-plugin', 'rules', 'skills', 'bots', 'examples', 'scripts'):
        files += [p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    h = hashlib.sha256()
    for p in sorted(files):
        if not p.resolve().is_relative_to(root.resolve()) or p.is_symlink():
            raise ValueError('Unsafe fingerprint path')
        raw = p.read_bytes()
        if len(raw) > MAX_FILE:
            raise ValueError('Package file exceeds size limit')
        h.update(p.relative_to(root).as_posix().encode()+b'\0'+hashlib.sha256(raw).digest())
    return h.hexdigest()

def catalog(root):
    value = read_json(root/'evaluation/scenarios.json')
    if not isinstance(value,dict) or (type(value.get('schema_version')) is not int or value['schema_version'] != 1) or not isinstance(value.get('cases'),list) or not value['cases']:
        raise ValueError('Invalid scenario catalog')
    ids = set()
    for c in value['cases']:
        if not isinstance(c,dict) or not isinstance(c.get('id'),str) or not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',c['id']) or c['id'] in ids:
            raise ValueError('Invalid or duplicate scenario ID')
        ids.add(c['id'])
        if type(c.get('minimum_trials')) is not int or not 1 <= c['minimum_trials'] <= 10:
            raise ValueError('Invalid scenario trial count')
        for key in ('skill','prompt','expected'):
            if not isinstance(c.get(key),str) or not c[key].strip():
                raise ValueError('Missing scenario field')
        if '/' in c['skill'] or '\\' in c['skill'] or '..' in c['skill'] or not (root/'skills'/c['skill']/'SKILL.md').is_file():
            raise ValueError('Scenario references unknown skill')
    return value['cases']

def template(root, commit):
    if not isinstance(commit,str) or not SHA.fullmatch(commit):
        raise ValueError('Expected a full lowercase commit SHA')
    cases=catalog(root)
    return {'schema_version':1, 'plugin_commit':commit, 'package_fingerprint':fingerprint(root),
            'scenario_fingerprint':digest((root/'evaluation/scenarios.json').read_bytes()),
            'clients':{client:{'build':'','server_version':'','tester':'','reviewer':'','recorded_at':'',
                              'reviewed':False,'cases':{c['id']:[{'status':'not_run','evidence':'','sha256':''}
                                                              for _ in range(c['minimum_trials'])] for c in cases}}
                       for client in CLIENTS}}

def validate_report(root, report, commit, evidence_root):
    root, evidence_root = root.resolve(), evidence_root.resolve()
    errors=[]
    expected=template(root,commit)
    if not isinstance(report,dict):
        return ['Report must be an object']
    for key in ('schema_version','plugin_commit','package_fingerprint','scenario_fingerprint'):
        if report.get(key) != expected[key] or (key == 'schema_version' and type(report.get(key)) is not int):
            errors.append('Missing or stale '+key)
    clients=report.get('clients')
    if not isinstance(clients,dict) or set(clients) != set(CLIENTS):
        return errors+['Require separate Cursor and Grok records']
    for client in CLIENTS:
        item=clients[client]
        if not isinstance(item,dict):
            errors.append(client+': invalid metadata'); continue
        for key in ('build','server_version','tester','reviewer','recorded_at'):
            if not isinstance(item.get(key),str) or not item[key].strip():
                errors.append(client+': missing '+key)
        try:
            timestamp=datetime.fromisoformat(item.get('recorded_at','').replace('Z','+00:00'))
            if timestamp.tzinfo is None:
                raise ValueError()
        except (ValueError,TypeError,AttributeError):
            errors.append(client+': timestamp must include timezone')
        if item.get('reviewed') is not True:
            errors.append(client+': human evidence review required')
        results=item.get('cases')
        expected_cases=expected['clients'][client]['cases']
        if not isinstance(results,dict) or set(results) != set(expected_cases):
            errors.append(client+': missing or unexpected cases'); continue
        for case_id, minimum in expected_cases.items():
            trials=results[case_id]
            label=client+'/'+case_id
            if not isinstance(trials,list) or not len(minimum) <= len(trials) <= 100:
                errors.append(label+': missing/invalid trial count'); continue
            seen_evidence = set()
            for trial in trials:
                if not isinstance(trial,dict) or trial.get('status') != 'pass':
                    errors.append(label+': NOT RUN, failed, or invalid trial'); continue
                try:
                    relative=trial.get('evidence')
                    if not isinstance(relative,str) or not relative or '\\' in relative or ':' in relative or PurePosixPath(relative).is_absolute() or '..' in PurePosixPath(relative).parts:
                        raise ValueError()
                    path=evidence_root/relative
                    if not path.resolve().is_relative_to(evidence_root.resolve()) or path.is_symlink() or any(p.is_symlink() for p in path.parents if p != evidence_root.parent):
                        raise ValueError()
                    if not path.is_file() or path.stat().st_size > MAX_FILE:
                        raise ValueError()
                    with path.open('rb') as f:
                        content=f.read(MAX_FILE+1)
                    if len(content)>MAX_FILE:
                        raise ValueError()
                    if not content.strip() or not isinstance(trial.get('sha256'),str) or not HASH.fullmatch(trial['sha256']) or digest(content) != trial['sha256']:
                        raise ValueError()
                    if trial['sha256'] in seen_evidence:
                        raise ValueError()
                    seen_evidence.add(trial['sha256'])
                except (ValueError,OSError):
                    errors.append(label+': missing, unsafe, empty, or mismatched evidence')
    return errors

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--expected-commit',required=True)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--template',type=Path)
    group.add_argument('--report',type=Path)
    parser.add_argument('--evidence-root',type=Path)
    args=parser.parse_args()
    try:
        if args.template:
            value=template(args.root,args.expected_commit)
            with args.template.open('x',encoding='utf-8') as f:
                f.write(json.dumps(value,indent=2)+'\n')
            print('Created NOT RUN report. No tests were executed.')
            return 0
        if args.evidence_root is None:
            parser.error('--evidence-root is required for report checking')
        errors=validate_report(args.root,read_json(args.report),args.expected_commit,args.evidence_root)
    except (OSError,ValueError,RecursionError):
        print('FAIL: invalid, unavailable, or unsafe local input',file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print('FAIL: '+error,file=sys.stderr)
        return 1
    print('PASS: supplied acceptance record is complete and matches this package.')
    print('Human evidence review remains necessary; no live test or publication was performed.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())