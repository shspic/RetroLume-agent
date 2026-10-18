# TASK-112 原字节校验补充定位

F112-02同一Node入口还存在起始BOM被规范校验忽略的路径。renderer-protocol.cjs 8行TextDecoder只设fatal，不设ignoreBOM；默认先移除起始BOM，9行只比较解码后的text。规范JSON原字节前加EF BB BF时，解码字符串与canonical(value)仍相同。Python严格decode后JSON拒绝起始U+FEFF，两端接受域和UTF-8无BOM合同不一致。

2026-10-11查阅[WHATWG Encoding TextDecoderCommon](https://encoding.spec.whatwg.org/#textdecodercommon)，默认ignore BOM为false且初始U+FEFF不进入输出。正文为机制推导与冻结源码结合，未运行产品或新增测试。该缺口并入F112-02的Node接收一致性修正，不增新权限方案或整批重测门。

可在同一renderer-protocol文件中一起修显式null与原字节BOM，保持四runtime身份。补证只需header/body无BOM和起始BOM对照，以及已有字段类型反例。若镜像内容变更仍必须有新image/load许可与绑定。
