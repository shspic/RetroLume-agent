"""纯文件/有限AST读取与身份记录；不import或执行产品，不读取私配。"""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('map', 'range', 'function'))
    parser.add_argument('path')
    parser.add_argument('--start', type=int, default=1); parser.add_argument('--end', type=int)
    parser.add_argument('--match', default='.*'); parser.add_argument('--purpose', required=True)
    args = parser.parse_args()
    path = ROOT / args.path
    relative = path.resolve().relative_to(ROOT).as_posix()
    if '.local.' in relative or any(part in ('private', '.git') for part in path.parts):
        raise ValueError('本卡不读取私配或Git内部文件')
    raw = path.read_bytes(); source = raw.decode('utf-8-sig'); lines = source.splitlines()
    ranges = []
    if args.mode == 'range': ranges.append((args.start, args.end or len(lines)))
    else:
        tree = ast.parse(source)
        def walk(nodes, parent=''):
            for node in nodes:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    name = parent + node.name
                    if re.search(args.match, name):
                        if args.mode == 'map':
                            print(json.dumps({'name': name, 'line': node.lineno, 'end': node.end_lineno,
                                              'signature': ast.unparse(node.args), 'decorators': [ast.unparse(d) for d in node.decorator_list]}, ensure_ascii=False))
                        else: ranges.append((min([node.lineno] + [d.lineno for d in node.decorator_list]), node.end_lineno))
                elif isinstance(node, ast.ClassDef): walk(node.body, parent + node.name + '.')
        walk(tree.body)
    for start, end in ranges:
        print('\n'.join(f'{number}: {lines[number-1]}' for number in range(start, min(end, len(lines)) + 1)))
    record = {'utc': datetime.now(timezone.utc).isoformat(), 'mono_ns': time.monotonic_ns(), 'path': relative,
              'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'mode': args.mode,
              'match': args.match if args.mode != 'range' else None, 'ranges': ranges,
              'purpose': args.purpose, 'product_import_or_execution': False}
    with (OUT / 'reads.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + '\n')


if __name__ == '__main__': main()
