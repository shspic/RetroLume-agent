# 功能检查初次失败原事实

2026-10-10T08:53:04Z前，使用既有backend/.venv运行c02_checks，退出1，失败在不同进程的owner identity整dict相等断言。owner identity含held字段，持有者True、竞争者False，不能整dict比较；正确核对为竞争者busy与同一非空kernel_object_path。

此为夹具断言错误，有据修正一次。原目录、source-identity、离线计数和失败保留，没有PG、API或renderer启动。此前系统Python因没有psycopg在import时拒绝，未进入batch；后续使用原既有虚拟环境，没有安装依赖。
