"""启动已配置的本地资料工作台；Ctrl+C结束本次应用和本次启动的数据库。"""
import json
import os
import signal
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
NAME="retrolume-local-pg"
IMAGE="sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f"

def docker(*args):
    result=subprocess.run(["docker",*args],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=20)
    if result.returncode:raise RuntimeError("Docker操作未完成，请检查Docker Desktop是否已启动")
    return result.stdout.strip()

def main():
    config=ROOT/"config/database.local.json"
    data_dir=os.environ.get("RETROLUME_DATA_DIR")
    backup_dir=os.environ.get("RETROLUME_BACKUP_DIR")
    if not data_dir or not backup_dir:
        raise RuntimeError("缺少RETROLUME_DATA_DIR或RETROLUME_BACKUP_DIR；请在本机设置并保持两目录独立")
    dsn=os.environ.get("RETROLUME_DATABASE_URL")
    if not dsn:
        if not config.is_file():raise RuntimeError("缺少本地数据库配置；请设置RETROLUME_DATABASE_URL或创建受忽略的私有配置，切勿把密码发送到对话")
        dsn=json.loads(config.read_text(encoding="utf-8"))["url"]
    # 不启动同名但来源不一致的容器。
    if docker("inspect","--format","{{.Image}}",NAME)!=IMAGE:
        raise RuntimeError("数据库容器与已配置镜像不一致，请先检查")
    own_cid=docker("inspect","--format","{{.Id}}",NAME)
    already_running=docker("inspect","--format","{{.State.Running}}",NAME)=="true"
    started=False
    process=None
    try:
        if not already_running:docker("start",own_cid);started=True
        deadline=time.monotonic()+20
        while True:
            status=subprocess.run(["docker","exec",NAME,"pg_isready","-U","retrolume","-d","retrolume"],capture_output=True,timeout=3)
            if status.returncode==0:break
            if time.monotonic()>=deadline:raise RuntimeError("数据库启动超时；保留数据，不自动重建")
            time.sleep(.3)
        env=os.environ.copy()
        env.update(RETROLUME_DATA_DIR=data_dir,RETROLUME_BACKUP_DIR=backup_dir,RETROLUME_DATABASE_URL=dsn)
        print("Open http://127.0.0.1:8000 - Ctrl+C to stop.",flush=True)
        process=subprocess.Popen(
            [
                str(ROOT/"backend/.venv/Scripts/python.exe"),
                "-m",
                "uvicorn",
                "app.main:create_app",
                "--factory",
                "--loop",
                "app.runtime:psycopg_compatible_loop_factory",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            cwd=ROOT/"backend",
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name=="nt" else 0,
        )
        process.wait()
    except KeyboardInterrupt:
        pass
    finally:
        if process is not None and process.poll() is None:
            try:
                # 先让uvicorn执行lifespan，关闭预览监督链；只向本次创建的进程组发送。
                if os.name=="nt":process.send_signal(signal.CTRL_BREAK_EVENT)
                else:process.terminate()
                process.wait(timeout=20)
            except (OSError,subprocess.TimeoutExpired):
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=3)
                print("应用退出未完成预览确认；保留preview-control收据，同Windows用户重启核对后才能再次打开预览。",flush=True)
        if started:
            if docker("inspect","--format","{{.Image}}",own_cid)!=IMAGE:
                raise RuntimeError("本次数据库身份未确认，保留资源等待核对")
            docker("stop","--time","5",own_cid)

if __name__=="__main__":
    try:main()
    except (RuntimeError,OSError,KeyError,json.JSONDecodeError) as error:
        print(str(error))
        raise SystemExit(1)
