# 原生交易与寄售控件候选

2026-11-14。`object/ui/deal` 全部二十件资源、五十八个非空源位置已用现有自有深玉／米金画板重绘并重新编码。原生尺寸、原始偏移、帧数、像素模式及所有非像素字节均保留。候选 PNG 为最终 IMG 再解码的像素。本目录不安装客户端，画面与运行验收仍待完成。 [原图及来源](manifest.json) · [候选及哈希](candidate-manifest.json) · [全部候选帧](candidate-all-states.png)

| 类别 | 资源 | 源位置 |
| --- | --- | --- |
| 当面交易／请求 | `AgreeBtn`、`C2CDealPanel`、`DisagreeBtn`、`LittleAgreeBtn`、`LittleRefuseBtn`、`RequestDealPanel` | 18 |
| 寄售背景、列表及设置 | `bg_pawnshop`、`commiteditem`、`commitpanel`、`pawnSettingPanel` | 4 |
| 寄售操作 | `cancelbtn`、`cancelhorizontal`、`commitbtn`、`confirmbtn`、`lookuppetBtn`、`mystoragebtn`、`pawnedcancelBtn`、`updateBtn` | 32 |
| 寄售页签 | `tab_pawned`、`tab_pawning` | 4 |

十八件资源在固定包内 `uiMain`／`uiSelRoom` 存在十九处路径字面量或属性绑定。`cancelbtn` 和 `confirmbtn` 的源图文案清晰可读，当前检查的四个模块中没有命中其路径，运行绑定继续待证。相关解释没有扩展到未知页面或点击行为。

`uiMain` 的当面交易名字、邀请名字直接加载 `zoneChooseColor`；金额、`uiSelRoom` 寄售设置输入及已寄售行的字段直接加载 `lightColor`。二十一个作用域的直接颜色存储、字节位置、指令片段与源代码摘要见 [文字色证据](contrast-evidence.json)。匹配的 `uiMain` 全局字面量分别为浅米白和白色，动态文字区域使用深玉底；共享命名空间的实际加载、运行颜色仍待核验。没有把缺失的字面量赋值误当成黑字默认。

普通四帧按钮保留源顺序，灰色原位为 3；竖排取消的灰色原位为 1，另两位置保留高亮差异。两页签分别保留两位置。宠物信息按钮采用自有宠物卡的爪印裁块，未延用原笑脸像素。内容格、输入井与滚动轨依据源图位置重建，物品、名字及金额不烘焙示例数据。源中的币种图文改写为项目已有名称“灵玉”，没有改动交易数值或回调。

生成与回放：

```powershell
python -B assets/native-client-ui/deal-controls-reference/decode-references.py
python -B assets/native-client-ui/deal-controls-reference/contrast-evidence.py
python -B assets/native-client-ui/deal-controls-reference/export-deal.py
python -B assets/native-client-ui/deal-controls-reference/export-deal.py --check
```

主构建器可注册模块 `deal-controls: native-ui-deal-controls-art.py`，对应此目录的 `manifest.json`。制作只读固定 ZIP、资源包及 PYC 常量树；未执行原客户端代码，未进行 GUI 代审，未操作 Git 或实际客户端。 [QQ 堂来源](../../../docs/QQTANG_REFERENCE_SOURCE.md) · [自有绘制器](../../../scripts/native-ui-deal-controls-art.py)

2026-11-14 接入回执：本组已由主构建器导出并合入统一原生图片包，实际客户端文件已回读核对。独立导出器不负责安装；当前安装与恢复范围以 [统一包](../../native-client-bundle/review-v1/README.md) 和 [回读记录](../../../docs/native-client-installation-20261114.json) 为准。视觉与运行验收状态继续待完成。
