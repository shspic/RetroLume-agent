"""第一根仅核新能力/旧wire/规范数值与发送门，所有传输是显式合成。"""
from pathlib import Path
import subprocess
import sys
from control import ROOT,HERE,begin_root,end_root,failure,event


def main():
    number=begin_root('ROOT01-新能力协议与规范向量','offline')
    folder=HERE/f'root-{number:02d}';folder.mkdir(exist_ok=True)
    event('purpose',root=number,scope='新Embedding的typed wire v4/v3兼容、512维float32/007、确定顺序、无真实许可前拒；不运行PG/HTTP/SUP/browser/真实provider',
          expected='12个新方法按真实产品纯逻辑+最低传输替身核对，风险传播后续根',attempt_limit='一次选定检查，有实际修正依据才定向复检')
    command=[str(ROOT/'backend/.venv/Scripts/python.exe'),'-X','utf8','-m','unittest','tests.test_step018_embedding_contracts','-v']
    try:
        result=subprocess.run(command,cwd=ROOT/'backend',capture_output=True,timeout=90)
    except subprocess.TimeoutExpired as error:
        (folder/'stdout-timeout.txt').write_bytes(error.stdout or b'')
        (folder/'stderr-timeout.txt').write_bytes(error.stderr or b'')
        failure('ROOT01-subprocess-timeout','子解释器90秒到门，stdlib run已kill并wait；没有方法结果，保留在途根用于有据修正，不虚报12例执行')
        raise
    (folder/'stdout.txt').write_bytes(result.stdout);(folder/'stderr.txt').write_bytes(result.stderr)
    event('offline_result',root=number,entry=command[2:],exit_code=result.returncode,stdout=str((folder/'stdout.txt').relative_to(ROOT)),stderr=str((folder/'stderr.txt').relative_to(ROOT)))
    if result.returncode:failure('ROOT01',result.stderr.decode('utf-8',errors='replace')[-5000:])
    end_root(result='completed' if not result.returncode else 'failed',resources_confirmed_stopped=True)
    print(result.stderr.decode('utf-8',errors='replace'))
    return result.returncode


if __name__=='__main__':raise SystemExit(main())
