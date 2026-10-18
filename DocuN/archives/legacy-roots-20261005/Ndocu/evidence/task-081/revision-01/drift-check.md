# TASK-081 修正轮01 漂移核对与读取定位（只读证据）

- 日期：2026-09-24（Asia/Shanghai）；执行者：沿 081 原 Work Buddy 增强执行窗口（实际 GLM-5.3，如实登记）。
- 漂移核对（复用首轮 read-hashes.txt 冻结值，仅复算受影响文件）：
  - backend/app/activities/repository.py = 045a3cf8b1c81d7a1336c3bd2e90e891e4e53934027c9fea9727fafde7202534（与首轮一致，无漂移）。
  - backend/app/pdf_import/_windows_job.py = 797f445f807d7d9264ea33bddb3388b4848b5d01c10498c221b352b24a236425（与首轮一致，无漂移）。
- 归档核对：Ndocu/archives/TASK-081-before-revision01-20260924.md 内容为**原始任务卡全文**（"原合同"），非首轮结果；首轮结果原文仍在 Ndocu/results/TASK-081-result.md 下半部分保留（修正轮01 置顶）。
- 本轮读取（最小上下文，未变已读不重复）：首轮结果全文（本窗口自写）、TASK-076-work-decision.md、LATER_REQUIREMENTS.MD NFR-003/SEC-002 原文、repository.py claim/settle/admit/mark、_windows_job.py 终止/等待段（L115-177）——以上除首轮结果外均在本窗口首轮已读且 hash 未变，未重复读取完整历史报告。
- 本轮写入：仅 Ndocu/results/TASK-081-result.md（修正轮01 置顶+首轮历史保留）与本目录本文件。未改源码/迁移/正式 docu/旧证据/公共库/Git；未测试/compile/PG/Docker/应用/模型/网络/安装；未读凭据；运行/费用预算 0。
