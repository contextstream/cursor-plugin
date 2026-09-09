#!/usr/bin/env python3
"""Offline package checks, not a full Cursor schema or runtime security audit.

Frontmatter uses JSON-quoted strings/booleans (a deliberate YAML subset).
No network, credentials, package installs, or executable hooks are required.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote, urlsplit
from check_release import catalog

ENDPOINT = 'https://mcp.contextstream.io/mcp'
SKILLS = ('context-check','project-brief','decision-check','project-resume',
          'change-impact','project-handoff','memory-review')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
VERSION = re.compile(r'(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z')
LINK = re.compile(r'\[[^\]\n]*\]\(([^)\s]+)\)')
MAX_TEXT = 128 * 1024
MAX_SKILL = 6000

def local_path(root, value, parent=None):
    if not isinstance(value,str) or not value or '\\' in value:
        raise ValueError('expected a nonempty POSIX path')
    if urlsplit(value).scheme or PurePosixPath(value).is_absolute():
        raise ValueError('expected a repository-relative path')
    try:
        target=((parent or root)/value).resolve()
    except (RuntimeError,OSError):
        raise ValueError('unsafe or cyclic path') from None
    if not target.is_relative_to(root.resolve()):
        raise ValueError('path escapes the repository')
    return target

def read_text(root, value):
    with local_path(root,value).open('rb') as f:
        raw=f.read(MAX_TEXT+1)
    if len(raw)>MAX_TEXT:
        raise ValueError('text file exceeds size limit')
    return raw.decode('utf-8')

def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('duplicate JSON field')
        result[key]=value
    return result

def frontmatter(text):
    lines=text.splitlines()
    if not lines or lines[0]!='---':
        raise ValueError('missing opening frontmatter delimiter')
    try:
        end=lines.index('---',1)
    except ValueError as exc:
        raise ValueError('missing closing frontmatter delimiter') from exc
    result={}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key,sep,raw=line.partition(':')
        if not sep or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*',key):
            raise ValueError('frontmatter keys must be simple scalar fields')
        if key in result:
            raise ValueError('duplicate frontmatter field')
        value=json.loads(raw.strip())
        if not isinstance(value,(str,bool)):
            raise ValueError('frontmatter supports only quoted strings and booleans')
        result[key]=value
    body='\n'.join(lines[end+1:]).strip()
    if not body:
        raise ValueError('empty Markdown body')
    return result,body

def validate(root):
    root=root.resolve(); errors=[]
    def check(condition,message):
        if not condition:
            errors.append(message)
    def load_json(name):
        try:
            return json.loads(read_text(root,name),object_pairs_hook=unique_object)
        except (OSError,ValueError,RecursionError):
            errors.append(name+': invalid or missing JSON')
            return None
    m=load_json('.cursor-plugin/plugin.json')
    if not isinstance(m,dict):
        errors.append('plugin manifest must be an object')
    else:
        check(m.get('name')=='contextstream','plugin identity must remain contextstream')
        check(isinstance(m.get('version'),str) and bool(VERSION.fullmatch(m['version'])),'version must be stable semver')
        check(isinstance(m.get('description'),str) and bool(m['description'].strip()),'description is required')
        check(isinstance(m.get('author'),dict) and m['author'].get('name')=='ContextStream','author must identify ContextStream')
        check(m.get('repository')=='https://github.com/contextstream/cursor-plugin','unexpected repository URL')
        check(m.get('homepage')=='https://contextstream.io','unexpected homepage')
        check(m.get('license')=='MIT','package license must remain MIT')
        keys=m.get('keywords')
        check(isinstance(keys,list) and bool(keys) and all(isinstance(k,str) and k.strip() for k in keys),'keywords must be nonempty strings')
        for field,expected in [('rules','./rules/'),('skills','./skills/'),('mcpServers','mcp.json')]:
            check(m.get(field)==expected,field+' must use '+expected)
        logo=m.get('logo')
        if isinstance(logo,str) and logo.startswith('https://'):
            check(logo=='https://contextstream.io/logo-hex.png','unexpected external logo URL')
        else:
            try:
                check(local_path(root,logo).is_file(),'local logo does not exist')
            except (TypeError,ValueError,OSError):
                errors.append('logo must be the existing HTTPS asset or a repository-local file')
        for field in ('hooks','agents','commands','variables'):
            check(field not in m,'unexpected executable or unreviewed component: '+field)
    check(load_json('mcp.json')=={'mcpServers':{'contextstream':{'url':ENDPOINT}}},
          'MCP must contain only the hosted ContextStream URL; no credentials, commands, or extra servers')
    expected={f'skills/{name}/SKILL.md' for name in SKILLS}
    discovered={p.relative_to(root).as_posix() for p in (root/'skills').rglob('SKILL.md')}
    check(discovered==expected,'expected exactly the seven documented skill directories')
    for relative in sorted(expected):
        try:
            text=read_text(root,relative); metadata,body=frontmatter(text)
            name=metadata.get('name')
            check(isinstance(name,str) and bool(SLUG.fullmatch(name)) and name==Path(relative).parent.name,relative+': name must match its directory')
            check(isinstance(metadata.get('description'),str) and bool(metadata['description'].strip()),relative+': description is required')
            check(set(metadata)=={'name','description'},relative+': unreviewed frontmatter field')
            check(len(text.encode())<=MAX_SKILL,relative+': skill exceeds progressive-disclosure size budget')
            for phrase in ('## Scope and data handling','## Evidence and permissions','explicit approval','transcript','untrusted','## Efficiency and recovery'):
                check(phrase in body,relative+': missing documented contract: '+phrase)
        except (OSError,ValueError) as exc:
            errors.append(relative+': '+str(exc))
    try:
        metadata,body=frontmatter(read_text(root,'rules/contextstream.mdc'))
        check(metadata.get('alwaysApply') is True,'Cursor rule must retain alwaysApply: true')
        check(isinstance(metadata.get('description'),str) and bool(metadata['description'].strip()),'Cursor rule needs a description')
        check(len(body.encode())<=3000,'Always-on rule exceeds size budget')
    except (OSError,ValueError) as exc:
        errors.append('rules/contextstream.mdc: '+str(exc))
    for required in ('README.md','LICENSE','bots/project-brief-handoff.md','docs/grok-bot.md','docs/data-handling.md',
                     'docs/manual-validation.md','docs/marketplace-launch.md','docs/first-run.md','docs/capability-map.md',
                     'docs/evaluation.md','docs/protocol-probe.md','examples/harbor-export/README.md'):
        try:
            check(bool(read_text(root,required).strip()),required+': empty file')
        except (OSError,ValueError) as exc:
            errors.append(required+': '+str(exc))
    try:
        cases=catalog(root)
        check({c['skill'] for c in cases}==set(SKILLS),'all skills need acceptance scenarios')
    except (OSError,ValueError,RecursionError):
        errors.append('invalid or missing acceptance scenario catalog')
    for path in sorted(root.rglob('*.md')):
        if any(part in ('.git','.venv','__pycache__','.local-evidence') for part in path.relative_to(root).parts):
            continue
        relative=path.relative_to(root).as_posix()
        try:
            for target in LINK.findall(read_text(root,relative)):
                parsed=urlsplit(target)
                if parsed.scheme in ('https','http','mailto') or (not parsed.path and not parsed.scheme):
                    continue
                candidate=local_path(root,unquote(parsed.path) if not parsed.scheme else target,path.parent)
                check(candidate.exists(),relative+': broken local link: '+target)
        except (OSError,ValueError) as exc:
            errors.append(relative+': '+str(exc))
    return errors

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    errors=validate(parser.parse_args().root)
    if errors:
        for error in errors:
            print('ERROR: '+error,file=sys.stderr)
        return 1
    print('PASS: package, credential-free MCP, seven skills, scenario coverage, and local links')
    print('Not checked: live clients, OAuth, runtime authorization, external links, or marketplace approval')
    return 0

if __name__=='__main__':
    raise SystemExit(main())