"""本轮方法计时、完整argv/as-run及有界离线消费，不启动服务。"""
import argparse
import os
import subprocess
import sys
import time
from c03_support import C03Budget, ROOT, EVIDENCE, freeze, sample, save


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('label'); parser.add_argument('timeout', type=int)
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    budget = C03Budget(); value = budget.check(); budget.root('c03-check-group')
    label = args.label + '-' + str(time.monotonic_ns())
    destination = freeze(label)
    if args.label == 'frontend-build': budget.reserve('frontend_build')
    available = min(value['limits']['offline_seconds'] - value['offline_seconds'],
                    value['continuation']['offline_round_max'] - (value['offline_seconds'] - value['continuation']['baseline_offline_seconds']))
    timeout = min(args.timeout, available)
    environment = dict(os.environ); environment['C03_CASE_ATTEMPT'] = label
    start = sample(); log = EVIDENCE / 'offline' / (label + '.log'); log.parent.mkdir(parents=True, exist_ok=True)
    method = {'label': label, 'start': start, 'argv': args.arguments, 'cwd': str(ROOT), 'timeout_seconds': timeout,
              'as_run': str(destination.relative_to(ROOT)), 'log': str(log.relative_to(ROOT)),
              'env_keys_added': ['C03_CASE_ATTEMPT'], 'root': 'c03-check-group', 'layer': '本地离线/受控连接检查或构建，新增PG/API/监听0'}
    save(EVIDENCE / 'methods' / (label + '-begin.json'), method); budget.event('c03.method.begin', method)
    with log.open('xb') as stream:
        try:
            result = subprocess.run(args.arguments, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                    env=environment, timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW, check=False)
            code = result.returncode
        except subprocess.TimeoutExpired: code = 124
    end = sample(); seconds = (end['mono_ns'] - start['mono_ns']) / 1e9
    value = budget.load(); value['offline_seconds'] += seconds; budget.save(value)
    method.update(end=end, exit_code=code, seconds=seconds)
    save(EVIDENCE / 'methods' / (label + '.json'), method); budget.event('c03.method.end', method)
    print(__import__('json').dumps({'label': label, 'exit_code': code, 'seconds': seconds, 'log': str(log)}))
    return code


if __name__ == '__main__': sys.exit(main())
