"""显式零费记忆命令；撤销提交与正文清理是两个事务。"""
from __future__ import annotations
from uuid import uuid5,NAMESPACE_URL
from .contracts import MemoryCommandInput, MemoryRefusal, bounded_json


class MemoryService:
    def __init__(self,ledger):
        self.ledger=ledger

    async def capabilities(self):
        return await self.ledger.probe_memory()

    async def submit_command(self,command):
        capabilities=await self.capabilities()
        if not capabilities["write"]:
            raise MemoryRefusal(capabilities["reason"] or "memory_permissions_not_ready","学习记忆写入暂不可用",503)
        if command.action=="purge" and not capabilities["cleanup"]:
            raise MemoryRefusal("memory_permissions_not_ready","记忆内容清理尚未就绪",503)
        receipt=await self.ledger.apply_memory_command(command)
        if command.action=="revoke" and not receipt.get("replayed") and not receipt.get("duplicate_of") and capabilities["cleanup"]:
            purge=MemoryCommandInput(business_key=str(uuid5(NAMESPACE_URL,command.business_key+":purge")),
              memory_id=command.memory_id,expected_revision=receipt["revision_after"],action="purge",
              body={"revocation_key":command.business_key,"manifest_sha256":receipt["manifest_sha256"],"confirm_memory_cleanup":True})
            try:
                outcome=await self.ledger.apply_memory_command(purge)
                receipt["purge_state_now"]=outcome["purge_state_now"]
            except Exception:
                # 第一阶段已经提交，清理故障不能把逻辑撤销回滚或伪称物理完成。
                try:
                    known=await self.ledger.read_memory_command(command.business_key)
                    if known:receipt["purge_state_now"]=known["purge_state_now"]
                except Exception:pass
                receipt["cleanup_status_unconfirmed"]=receipt["purge_state_now"]!="done"
        return bounded_json(receipt)

