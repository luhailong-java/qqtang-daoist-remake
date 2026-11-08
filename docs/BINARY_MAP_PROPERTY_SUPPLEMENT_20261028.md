# 二进制地图属性补充

2026-10-28仅做静态读取、字节和字段比较，不执行客户端。固定社区包中的 `object/mapElem/mapElem.prop` 为27,664字节，SHA256 `9b27eb66494c74770e9242ba4df34d7c03db7dd44b130a02440abff95a284a64`；与已固定ZIP内同名成员逐字节相同。来源包及其腾讯目标版本身份边界保持不变，不能据此称为经认证的腾讯原件。

`scripts/inspect-binary-map-properties.py` 将文件解释为版本2、773条记录：8字节头，每条24字节固定字段及宽×高个uint32网格属性。严格读至文件尾，无重复ID、无尾随字节。721条与现有Python字面量定义共享的记录，在宽高、偏移、LifeTime、Level、canMove和GridAttr上全部相等，字段差异0。完整逐条原始值及比较证据见 `references/qqtang-map-data/binary-properties-inspection.json`。

新增52条为 `16201–16227`（exploration候选）及 `19030–19054`（tank候选）。先前377张地图引用而Python表缺失的27个编号全部在这52条中找到。它们的核心几何不再缺失，但尚未进入已验证的 `elements.json`、全量运行清单和绘制终验；旧记录“27个定义缺失／22图受影响”是此前状态，不能当成本轮仍未找到数据。

`canDoSpecial`、`canHide`不在该二进制格式中序列化，新增项必须保持null／未知。字段解释由721条一致性支持，原生函数如何使用这些字段及具体历史版本仍待独立核实。数值前缀与资源包精确路径支持族和图片候选关联，不替代原生图片查找函数的证明。

`scripts/build-map-supplement-reference.py` 每次只解码1–6个显式ID；参考PNG与逐件来源在 `references/qqtang-map-data/visual-reference/binary-supplement/`。源参考仅用于结构和尺度，不能作为自有游戏成品。生产工具通过显式 `extraInventory`／`--extra=`读取该补充索引，不覆盖旧721项。新画沿用真实原帧画布、原占地和偏移，保留未知字段及二进制记录证据，全部候选仍需验收。

本轮本机重型检查按 `LOCAL_RESOURCE_WINDOW_20261028.md` 暂停。轻量JSON／文件存在快照为 `ART_PRODUCTION_STATUS_20261028.json`，当前分母773；已验证旧生产账与运行清单保持原截止点，恢复时段后再统一核验接入。发现来源、完成首稿、运行采用和最终通过分别记录。
