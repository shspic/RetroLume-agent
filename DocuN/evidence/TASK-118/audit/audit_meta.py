"""TASK-118 独立只读元数据工具，仅使用标准库，不导入或运行产品。"""
import argparse
import datetime as dt
import difflib
import hashlib
import json
from pathlib import Path
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path('D:/shspic/project_NO3_RetroLume-agent').resolve()
OUT = ROOT / 'DocuN/evidence/TASK-118/audit'
START = time.perf_counter()
UTC = dt.datetime.now(dt.timezone.utc).isoformat()
accesses = []

def pathof(value):
    p = Path(value)
    return (p if p.is_absolute() else ROOT / p).resolve()

def raw(value):
    p = pathof(value)
    b = p.read_bytes()
    accesses.append({'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()})
    if time.perf_counter() - START > 55:
        raise TimeoutError('metadata batch reached 55 seconds')
    return b

def decoded(value):
    p = pathof(value)
    if p.name.lower().startswith('task-117-result'):
        raise PermissionError('implementation result is hash-only')
    return raw(value).decode('utf-8-sig')

def jread(value):
    return json.loads(decoded(value))

def save(name, value):
    p = (OUT / name).resolve()
    if OUT not in p.parents:
        raise PermissionError('output outside audit directory')
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=['read', 'json', 'compact', 'shape', 'hash', 'freeze'])
parser.add_argument('paths', nargs='*')
parser.add_argument('--select', default='')
args = parser.parse_args()
status = 'ok'
parts = []
try:
    if args.mode == 'read':
        for spec in args.paths:
            path, sep, span = spec.partition('@')
            text = decoded(path).splitlines()
            first, last = (1, len(text)) if not sep else tuple(map(int, span.split(':')))
            parts.append('\n' + path + '\n' + '\n'.join(f'{i}: {text[i-1]}' for i in range(first, min(last, len(text))+1)))
    elif args.mode in ('json', 'compact', 'shape'):
        for path in args.paths:
            value = jread(path)
            for key in filter(None, args.select.split('/')):
                value = value[int(key)] if isinstance(value, list) else value[key]
            if args.mode == 'shape':
                if isinstance(value, dict):
                    value = {k: {'type': type(v).__name__, 'length': len(v) if hasattr(v, '__len__') else None} for k,v in value.items()}
                elif isinstance(value, list):
                    value = {'length': len(value), 'first': value[:2]}
            if args.mode == 'compact':
                def compact(v):
                    if isinstance(v, dict):
                        return {k: compact(x) for k,x in v.items()}
                    if isinstance(v, list):
                        if len(v)>12:
                            return {'count':len(v), 'first': [compact(x) for x in v[:6]], 'last': [compact(x) for x in v[-2:]]}
                        return [compact(x) for x in v]
                    if isinstance(v, str) and len(v)>1200:
                        return {'characters':len(v),'sha256_utf8':hashlib.sha256(v.encode('utf-8')).hexdigest(),'prefix':v[:200]}
                    return v
                value=compact(value)
            parts.append(path + '\n' + json.dumps(value, ensure_ascii=False, indent=2))
    elif args.mode == 'hash':
        for path in args.paths:
            raw(path)
        parts.append(json.dumps(accesses, ensure_ascii=False, indent=2))
    elif args.mode == 'freeze':
        checks = []
        seen = set()
        def check(path, expected):
            p = pathof(path)
            key = (str(p), expected.get('sha256'), expected.get('exists', True))
            if key in seen:
                return
            seen.add(key)
            b = raw(p) if p.is_file() else None
            actual = {'exists': b is not None, 'bytes': 0 if b is None else len(b), 'sha256': None if b is None else hashlib.sha256(b).hexdigest()}
            match = all(actual.get(k) == v for k,v in expected.items() if k in actual)
            checks.append({'path': str(p), 'expected': expected, 'actual': actual, 'match': match})
        def walk(value):
            if isinstance(value, dict):
                if 'path' in value and isinstance(value['path'], str):
                    if 'post' in value and isinstance(value['post'], dict):
                        check(value['path'], value['post'])
                    elif 'sha256' in value:
                        check(value['path'], value)
                if 'absolute_path' in value and 'sha256' in value:
                    check(value['absolute_path'], value)
                for k,v in value.items():
                    if k not in ('pre', 'post'):
                        walk(v)
            elif isinstance(value, list):
                for v in value:
                    walk(v)
        for path in args.paths:
            walk(jread(path))
        result = {'at': UTC, 'checks': checks, 'count': len(checks), 'mismatches': [v for v in checks if not v['match']]}
        save('freeze-initial.json', result)
        parts.append(json.dumps({'count': len(checks), 'mismatches': result['mismatches']}, ensure_ascii=False, indent=2))
except BaseException as exc:
    status = 'error'
    parts.append(type(exc).__name__ + ': ' + str(exc))
    raise
finally:
    elapsed = time.perf_counter() - START
    record = {'at': UTC, 'argv': sys.argv[1:], 'status': status, 'elapsed_seconds': elapsed, 'accesses': accesses}
    with (OUT / 'metadata-commands.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + '\n')
    output = '\n'.join(parts)
    transcript = OUT / ('read-' + str(time.time_ns()) + '.txt')
    transcript.write_text(output, encoding='utf-8')
    print(output)
    print('\nmetadata_seconds=' + str(elapsed))
