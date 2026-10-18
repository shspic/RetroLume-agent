"""启动已配置的本地资料工作台；Ctrl+C结束本次应用和本次启动的数据库。"""
import json
import os
import signal
from pathlib import Path
import subprocess
import time
import sys
import argparse
import threading

ROOT=Path(__file__).resolve().parents[1]
NAME="retrolume-local-pg"
IMAGE="sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"

def docker(*args):
    result=subprocess.run(["docker",*args],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=20)
    if result.returncode:raise RuntimeError("Docker操作未完成，请检查Docker Desktop是否已启动")
    return result.stdout.strip()

def serve_owned(port):
    """本机启动器的精确stdin生命周期；仍由正常app/lifespan收尾。"""
    sys.path.insert(0,str(ROOT/'backend'))
    import asyncio,uvicorn
    from app.main import create_app
    from app.runtime import psycopg_compatible_loop_factory
    server=uvicorn.Server(uvicorn.Config(create_app(),host='127.0.0.1',port=port,timeout_graceful_shutdown=150))
    def close_on_owner_end():
        sys.stdin.readline()
        server.should_exit=True
    threading.Thread(target=close_on_owner_end,name='local-launcher-owned-input',daemon=True).start()
    with asyncio.Runner(loop_factory=psycopg_compatible_loop_factory) as runner:runner.run(server.serve())

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8000)
    parser.add_argument('--container',default=NAME)
    parser.add_argument('--shutdown-stdin',action='store_true',help='由当前启动句柄的stdin一行或EOF触发正常关闭')
    parser.add_argument('--serve-owned',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args()
    if not 1024<=args.port<=65535:raise RuntimeError('端口无效')
    if args.serve_owned:return serve_owned(args.port)
    config=ROOT/"config/database.local.json"
    data_dir=os.environ.get("RETROLUME_DATA_DIR")
    backup_dir=os.environ.get("RETROLUME_BACKUP_DIR")
    if not data_dir or not backup_dir:
        raise RuntimeError("缺少RETROLUME_DATA_DIR或RETROLUME_BACKUP_DIR；请在本机设置并保持两目录独立")
    dsn=os.environ.get("RETROLUME_DATABASE_URL")
    original_dsn=dsn
    factory=None
    selected_target=None
    if os.environ.get('RETROLUME_DATA_EXIT_CONFIG'):
        sys.path.insert(0,str(ROOT/'backend'))
        from app.data_exit.config import load_profile
        from app.data_exit.control import ControlHub
        from app.data_exit.restore import TargetFactory
        profile=load_profile()
        if profile is not None:
            hub=ControlHub(os.environ['RETROLUME_CONTROL_ROOT'])
            selection=hub.state()['selection']
            if selection is not None:
                factory=TargetFactory(hub,os.environ['RETROLUME_RESTORE_ROOT'],profile['factory'])
                selected_target=factory.target(selection['target_id'])
                dsn=factory.readonly_credentials(selected_target.target_id)['readonly_dsn']
    if not dsn:
        if not config.is_file():raise RuntimeError("缺少本地数据库配置；请设置RETROLUME_DATABASE_URL或创建受忽略的私有配置，切勿把密码发送到对话")
        dsn=json.loads(config.read_text(encoding="utf-8"))["url"]
    # 不启动同名但来源不一致的容器。
    selected_name=selected_target.name if selected_target is not None else args.container
    selected_image=factory.profile['image_id'] if factory is not None else IMAGE
    if docker("inspect","--format","{{.Image}}",selected_name)!=selected_image:
        raise RuntimeError("数据库容器与已配置镜像不一致，请先检查")
    own_cid=docker("inspect","--format","{{.Id}}",selected_name)
    if selected_target is not None and own_cid!=selected_target.cid:raise RuntimeError('只读副本身份不符，不能回退原库')
    already_running=docker("inspect","--format","{{.State.Running}}",own_cid)=="true"
    started=False
    process=None
    try:
        if not already_running:
            if factory is not None:factory.start(selected_target)
            else:docker("start",own_cid)
            started=True
        deadline=time.monotonic()+20
        while True:
            if factory is not None:
                factory._wait_pg(dsn)
                break
            import psycopg
            try:
                with psycopg.connect(dsn,connect_timeout=3):pass
                break
            except psycopg.Error:pass
            if time.monotonic()>=deadline:raise RuntimeError("数据库启动超时；保留数据，不自动重建")
            time.sleep(.3)
        # 按实际数据库/登录就绪核对，不假定retrolume用户名；重开不迁移、不更换正常库。
        sys.path.insert(0,str(ROOT/'backend'))
        from app.data_exit.schema_checks import assert_data_schema_sync
        from psycopg.rows import dict_row
        with psycopg.connect(dsn,row_factory=dict_row) as application:
            assert_data_schema_sync(application)
            if application.execute('SELECT rolsuper FROM pg_roles WHERE rolname=current_user').fetchone()['rolsuper']:
                raise RuntimeError('业务进程不能使用superuser连接')
        env=os.environ.copy()
        env.update(RETROLUME_DATA_DIR=data_dir,RETROLUME_BACKUP_DIR=backup_dir)
        # 目标连接仅用于其就绪检查；源旁证连接保留原身份，不冒目标为源。
        application_dsn=original_dsn if selected_target is not None else dsn
        if application_dsn:env['RETROLUME_DATABASE_URL']=application_dsn
        else:env.pop('RETROLUME_DATABASE_URL',None)
        print(f"Open http://127.0.0.1:{args.port} - Ctrl+C to stop.",flush=True)
        process=subprocess.Popen(
            [
                str(ROOT/"backend/.venv/Scripts/python.exe"),
                str(Path(__file__).resolve()),
                "--serve-owned",
                "--port",
                str(args.port),
            ],
            cwd=ROOT/"backend",
            env=env,
            stdin=subprocess.PIPE,
            creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW) if os.name=="nt" else 0,
        )
        if args.shutdown_stdin:
            def close_from_owner():
                sys.stdin.readline()
                if process.poll() is None:
                    try:process.stdin.write(b'stop\n');process.stdin.flush()
                    except (OSError,ValueError):pass
            threading.Thread(target=close_from_owner,name='local-launcher-owner',daemon=True).start()
        process.wait()
    except KeyboardInterrupt:
        pass
    finally:
        if process is not None and process.poll() is None:
            try:
                # 独占匿名输入管道优先请求正常lifespan；无控制HTTP或全局进程操作。
                process.stdin.write(b'stop\n');process.stdin.flush()
                process.wait(timeout=170)
            except (OSError,subprocess.TimeoutExpired):
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=3)
                print("应用退出未完成预览确认；保留preview-control收据，同Windows用户重启核对后才能再次打开预览。",flush=True)
        if started:
            if docker("inspect","--format","{{.Image}}",own_cid)!=selected_image:
                raise RuntimeError("本次数据库身份未确认，保留资源等待核对")
            if factory is not None:factory.stop(selected_target)
            else:docker("stop","--time","5",own_cid)

if __name__=="__main__":
    try:main()
    except (RuntimeError,OSError,KeyError,json.JSONDecodeError) as error:
        print(str(error))
        raise SystemExit(1)
