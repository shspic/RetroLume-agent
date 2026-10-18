# TASK-041 / TASK-042 最终证据

只针对真实资料保存闭环；旧SPIKE未运行。所有私有配置和连接秘密不在此目录。

- install-report-postgres.json位于代码根：固定psycopg/binary3.3.5及tzdata；pip-check.log通过。
- migration.log：已批准新库首次迁移命令输出；非UTF-8控制台文本，具体能力由真实集成佐证，不单独当全约束证明。
- integration.json：真实上传、读取、列表、坏文件独立、失败替换、两个并发替换200/409、实际PG NOT NULL失败回滚通过；首次重开前端口bind探针遇Windows10048，未继续该轮。旧输出保留。
- integration-resume.json：只接续未运行的重开/浏览器，数据库正常停止再启动后资料保留。端口探针改为检查监听而非TIME_WAIT占用，不终止外部进程。
- browser.json：真实浏览器上传、读取、替换、坏文件隔离、纯文本HTML不执行和跨窗口版本反例；未安装新浏览器，使用已有开发工具。
- browser-final.json、build-final.log：loaded最终显示修正，正文/版本/列表一致及无移动端横向溢出。原静态审查P2和类型空值错误已保留并关闭。
- materials-desktop-final.png / materials-mobile-final.png：最终页面，均为合成资料。
- independent-review.md：隔离TASK-042静态与证据限定审查通过，不声称独立重跑PG或断电恢复。
- final-stop.json：本次应用/数据库停止，容器与数据保留。
- final-hashes.json：最终源码及锁文件hash，不包括私有配置。

仅3份标有合成验证的资料；没有真实用户资料、外部模型或费用调用。未验证断电恢复、完整产品权限、PDF/检索/学习/面试。源码验证脚本在tests/，请勿为文档重复运行。
