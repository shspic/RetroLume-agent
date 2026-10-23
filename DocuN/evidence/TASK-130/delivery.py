"""TASK130 文档及 Git 交付取证，不导入产品。"""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
E = Path(__file__).resolve().parent
def now():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()
def save(name, value):
    (E / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args, timeout=60):
    start=time.monotonic()
    p=subprocess.run(['git', *args], cwd=ROOT, capture_output=True, timeout=timeout)
    record={'at':now(),'args':list(args),'exit':p.returncode,'seconds':time.monotonic()-start,
            'stdout':p.stdout.decode('utf-8','replace'),'stderr':p.stderr.decode('utf-8','replace')}
    if len(p.stdout)>10000:
        record['stdout']='完整路径另见本卡清单，不重复大输出'
        record['stdout_sha256']=hashlib.sha256(p.stdout).hexdigest()
        record['stdout_bytes']=len(p.stdout)
    with (E/'git-commands.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(record,ensure_ascii=False)+'\n')
    if p.returncode: raise RuntimeError('Git失败，见命令证据')
    return p.stdout

if __name__=='__main__' and sys.argv[1]=='prepare':
    manifest=json.loads((E/'orchestration-20261023/input-manifest.json').read_text('utf-8'))
    checks=[]
    for item in manifest['files']:
        p=Path(item['path']); actual=sha(p)
        checks.append({'path':str(p),'sha256':actual,'matches':actual==item['sha256']})
    for item in manifest['rules'][:2]:
        p=Path(item['absolute_path']); actual=sha(p)
        checks.append({'path':str(p),'sha256':actual,'matches':actual==item['sha256']})
    save('input-check.json',checks)
    assert all(c['matches'] for c in checks)
    save('receipt.json',{'task':'TASK-130','round':'R-124','received_at':now(),
         'client':'Codex desktop','model':'GPT-6，平台未提供更细模型ID','role':'A-常规Git交付执行者',
         'window':'本聊天接收用户人工转卡；未创建或委派其他聊天','budget_seconds':5400,
         'product_runtime':0,'provider':0,'fees':0,'Q':'FROZEN'})
    changes={
      'README.md': [
       ('TASK128续作02已补齐正常API跨PG重开、中断保护和只读verify，连同已独审的修复及前三项，六项工程证据齐全，待主控最终核验；Q及真实付费保持关闭，详见上述正常首次安装说明。对已安装库不得重放迁移。',
        '2026-10-23，TASK128批准的关闭出站正常安装六项有限成果已由主控验收通过并关闭，TASK129独审结论有效。正常API的storage_ready、normal/R03与跨PG重开只证明关闭出站的存储及控制面；模型和integration未加载，create仍因config_invalid不可用。Q保持冻结，T0/72小时尚未开始，真实调用与费用仍为0；真实模型完整学习／面试、28项Must及供应商计量、账号、完整模板、Embedding容量与启用前置仍未闭合。验收范围见[TASK128最终裁定](DocuN/results/TASK-128-work-decision.md)及上述正常首次安装说明。对已安装库不得重放迁移。')],
      'deploy/normal-install.md': [
       ('六项工程证据齐全，等待主控核新增动态原件及最终验收。','2026-10-23，批准的关闭出站正常安装六项有限成果已由主控验收通过并关闭，见[TASK128最终裁定](../DocuN/results/TASK-128-work-decision.md)及[核证索引](../DocuN/evidence/TASK-128/orchestration-close-20261023/raw-evidence-index.json)。'),
       ('成功库、部分库和原收据全部保留，两库已停止；Q及真实付费仍关闭。','成功库、部分库和原收据全部保留；原执行post时点两库已停止，本说明不代表重新现场探测。正常API的storage_ready、normal/R03只证明关闭出站存储及控制面，模型和integration未加载，create仍因config_invalid不可用。Q冻结、T0/72小时未开始，真实调用及费用0；真实模型完整学习／面试、28项Must、供应商计量、账号、完整模板、Embedding容量和启用前置仍未闭合。'),
       ('四个独立 data/backup/control/restore 根、真实 Windows ACL/file-id、control_id、selection generation 及连接绑定只能在后续正常部署时核定，本卡不创建私有运行根。','TASK128已在批准的隔离正常安装目标核定四个独立 data/backup/control/restore 根、真实 Windows ACL/file-id、control_id、selection generation 及连接绑定；新部署仍须独立核定自己的绑定，本说明不创建私有运行根。'),
       ('## 未来显式 apply 与只读 verify','## 显式 apply 与只读 verify'),
       ('以下仅说明已实现参数。`$normalConfig` 和 `$installReceipt` 必须由未来运行卡给出真实绝对路径，收据父目录须预先存在；当前没有执行。','以下说明已实现参数。TASK128已在其精确许可目标完成apply及成功收据只读verify；新部署的`$normalConfig`和`$installReceipt`仍须由对应运行卡给出真实绝对路径，收据父目录须预先存在。本说明不授予再次执行权。'),
       ('该检查发生在未来真实数据库中才有动态效力；本轮执行记录器只证明本地调用顺序及停止分支，不能证明 SQL、事务、权限或启动已在 PG 生效。','TASK125的离线执行记录器只证明本地调用顺序及停止分支；TASK128真实001—015安装、角色权限及TASK129独审已在批准目标补齐动态证据，不能外推到新目标。'),
       ('只有未来安装及独立运行核验均满足后，才按原有正常源 loader 和四根绑定准备关闭配置，并使用原 `deploy/start_local.py` 的 `--container`、`--port`、`--shutdown-stdin` 启动。','TASK128已在批准目标完成安装及独立运行核验，按原有正常源loader和四根绑定准备关闭配置，并使用原 `deploy/start_local.py` 的 `--container`、`--port`、`--shutdown-stdin` 启动。新部署仍须先满足自己的安装及运行核验。'),
       ('首次真实 PG 安装、角色能力、应用读取、同库重开及停止组合验证仍待该运行卡完成。','上述首次真实PG安装、角色能力、应用读取、跨PG停开同库重开及停止组合验证已在TASK128批准目标验收；它们不证明真实模型业务或完整项目通过。')]
    }
    for name, replacements in changes.items():
        p=ROOT/name; before=p.read_bytes(); text=before.decode('utf-8')
        pre=E/'pre'/name; pre.parent.mkdir(parents=True,exist_ok=True); pre.write_bytes(before)
        for old,new in replacements:
            assert text.count(old)==1,old
            text=text.replace(old,new)
        p.write_bytes(text.encode('utf-8'))
        post=E/'post'/name; post.parent.mkdir(parents=True,exist_ok=True); post.write_bytes(p.read_bytes())
    import difflib
    diffs=[]
    for name in changes:
        diffs.extend(difflib.unified_diff((E/'pre'/name).read_text('utf-8').splitlines(True),(ROOT/name).read_text('utf-8').splitlines(True),fromfile=name+'.pre',tofile=name))
    (E/'docs.diff').write_text(''.join(diffs),encoding='utf-8')
    save('docs-hashes.json',[{'path':n,'pre_sha256':sha(E/'pre'/n),'post_sha256':sha(ROOT/n)} for n in changes])
    print('输入及规则指纹一致；两份说明已保存pre/post及有限diff。')
