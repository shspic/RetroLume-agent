"""明确动作的本机数据维护入口，不安装服务或自动迁移数据库。"""
import argparse
import asyncio
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))


def main():
    parser=argparse.ArgumentParser(description='核对数据操作或显式建立隔离只读副本')
    parser.add_argument('action',choices=['capabilities','job','plan','verify'])
    parser.add_argument('--id');parser.add_argument('--plan-sha256');parser.add_argument('--business-key')
    parser.add_argument('--deletion-policy',choices=['respect_current_deletions','snapshot_only_readonly'],default='respect_current_deletions')
    parser.add_argument('--confirm-readonly',action='store_true')
    args=parser.parse_args()
    from app.main import create_app
    from app.data_exit.contracts import DataError,DataJobCommand
    app=create_app();runtime=app.state.data_exit
    if runtime is None:raise DataError('restore_executor_missing',503)
    if args.action=='capabilities':result=runtime.caps()
    elif args.action=='job':result=runtime.hub.reconcile(args.id)
    elif args.action=='plan':result=runtime.restore.prepare(args.id,args.deletion_policy,runtime.context())
    else:
        if not args.confirm_readonly or not args.business_key or not args.plan_sha256:
            raise DataError('invalid_input',400)
        runtime.restore.plan(args.id,args.plan_sha256)
        receipt=runtime.hub.create_or_get_job(DataJobCommand('restore',args.business_key,
            {'plan_id':args.id,'plan_sha256':args.plan_sha256}),runtime.context())
        result=runtime.restore.verify(receipt['job_id'],args.plan_sha256)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    try:main()
    except Exception as error:
        from app.data_exit.contracts import DataError
        print(json.dumps({'error':error.code if isinstance(error,DataError) else 'storage_unavailable'},ensure_ascii=False))
        raise SystemExit(1)
