"""最后模板字段补齐的定向离线核对，不发送模型或重复已有测试。"""
import ast
import hashlib
import json
from types import SimpleNamespace
from .control import ROOT,EVIDENCE,batch,atomic,source_snapshot,event


def main():
    folder=EVIDENCE/"offline-06";folder.mkdir(exist_ok=False)
    with batch("offline","finite-description-model-contract-completion",maximum=60):
        source_snapshot(folder)
        ast.parse((ROOT/"backend/app/preview/business_contracts.py").read_text(encoding="utf-8"))
        from app.preview.business_contracts import messages_for
        from app.preview.description import canonical
        context='{"schema":"html.context.v2"}'
        messages=messages_for(SimpleNamespace(context_json=context))
        assert [message["role"] for message in messages]==["system","user"] and messages[1]["content"]==context
        assert all(set(message)=={"role","content"} for message in messages)
        contract=json.loads(messages[0]["content"].split("合同=",1)[1])
        registered=json.loads((ROOT/"deploy/preview/descriptor.schema.json").read_text(encoding="utf-8"))
        assert set(registered["required"])<=set(contract["root"])
        assert set(contract["math_ops"])==set(registered["operation_arity"])
        assert {"bar_values","bar_distribution","curve","points_lines"}==set(contract["sources"])
        assert len(messages[0]["content"].encode("utf-8"))<8192
        atomic(folder/"result.json",{"status":"PASS_TEMPLATE_STRUCTURE_ONLY","template_sha256":hashlib.sha256(canonical(messages[:1]).encode()).hexdigest(),
             "template_bytes":len(messages[0]["content"].encode()),"roles":["system","user"],"model_sends":0,"provider_quality":False})
        event("template_offline_complete",{"folder":str(folder),"scope":"template fields only; no new OneCall evidence"})


if __name__=="__main__":main()
