# 原生消息框链接字色候选 v1

本批只提供颜色常量补丁工具、精确哈希合同和静态证明，不包含第三方 PYC 文件。原生背景美术由图片安装器管理；此补丁只把消息框链接的蓝色改为浅蓝紫，配合当前深玉底。

来源为本地 QQTang-Local v1.3.4 社区修改客户端的 `res/uiRes/uiMain.pyc`，不能据此认定为腾讯官方原版。源文件 SHA256 必须为 `18074d6e8e0e6cd0fdcb0d70eba6e94d3b512359c191b8a37030e017b2839411`，长度 301556 字节，头部 `3bf20d0a029f924d`。目标 SHA256 必须为 `54b1bc67712edcf6ee4649effa9adf1e1d7b66174bd9bb637cbf3f90b02b9bf6`。

## 变化范围

`?.UI.children.SysMsgbox.children.hyPerLink1` 的 `co_consts[6]` 从整数 0 改为 200。按文件起点计，绝对半开区间 `[63481, 63485)` 的四字节整数负载由 `00000000` 换为 `c8000000`；`63480` 处的 marshal 整数标记 `69` 保留。实际不同的字节只有偏移 `63481`。

该常量由两项颜色属性共用，全部五处 `LOAD_CONST 6` 位于该代码段相对偏移 `30, 33, 51, 54, 57`。没有独立序列化的 RGBA 元组可直接替换，因此本批有意同步改变两项颜色。

| 属性 | 原 RGBA | 候选 RGBA |
| --- | --- | --- |
| `drawcolor` | `[0,0,255,255]` | `[200,200,255,255]` |
| `textEdgeColor` | `[255,0,0,0]` | `[255,200,200,200]` |

工具用项目的有界惰性解析器重新读完整个文件，前后均消费全部字节、得到 20766 个常量树对象和 830 个代码段。逐段比较全部 `co_code`；把唯一改动的整数还原后，对整棵解析树做递归相等检查。因此 URL、caption、回调、其他常量、名称、代码字段、行号表及非颜色赋值均保留。客户端代码不被 import、marshal.load、exec、eval 或构造为 CodeType。

`manifest.json` 记录证明摘要；完整逐段哈希证据在 `docs/native-sysmsgbox-color-patch-plan-20261114.json`。本批摘要按有序 `{scope,sha256}` 列表的 UTF-8、键排序、无空白 JSON 计算，为 `cac8abb6c87c28146abff1cdff3e270624d165f3969958d03d248b72f7ca4d05`。早期计划的列表字段和 JSON 编码不同，其摘要不能直接对比。

## 操作

从仓库根目录运行；`<CLIENT_ROOT>` 由操作者替换为包含 `Client.exe` 的目录。默认只读验证；安装、恢复均要求所有 `Client.exe` 已关闭。工具不会启动客户端。

```powershell
python scripts/native-ui-color-data.py --client-root '<CLIENT_ROOT>'
python scripts/native-ui-color-data.py --client-root '<CLIENT_ROOT>' --apply
python scripts/native-ui-color-data.py --client-root '<CLIENT_ROOT>' --restore
```

安装前再次核对路径、源字节、原哈希及完整解析证明。独立原文件备份、操作锁和回执存于被 Git 忽略的 `.artifacts/native-client-ui-backup/text-color-v1/selected-client-<hash>/`，与图片安装器的备份互不共用。完整本机客户端路径只写入该私有回执；标准输出只含 `clientRootAlias` 与客户端内相对路径。

写入采用同目录暂存及 `os.replace`，随后重新读取并做完整验证。捕获到失败时，仅在当前内容仍是本次确切目标内容的情况下回滚到操作前字节，避免覆盖外部未知改动。进程终止会自动释放 OS 锁；如在写入和最终回执之间中断，可再次运行安装或恢复，工具从精确哈希和原备份恢复判断。备份损坏时拒绝恢复。若文件已是目标哈希但本工具没有原备份，重复安装会报告 `backupVerified=false`，恢复仍要求可验证的原备份。

本批不修改 `object.pkg`、`object.idx`、图片清单或其他模块。图片安装器的 `--restore` 不恢复此颜色补丁；应使用本工具的 `--restore` 单独恢复。

## 检查与状态

```powershell
python tests/native-ui-color-data.test.py -v
```

14 项检查覆盖公开合同、完整惰性重放、默认只读、重复安装与恢复、原哈希拒绝、坏备份拒绝、运行中阻断、前后写入失败回滚、prepared 状态恢复、并发锁和停进程检查期间的外部改动。精确源测试只从忽略的本地参考 ZIP 读取原始字节，并在 `.artifacts/native-ui-color-data-tests/` 下建立与清理模拟客户端；缺少本地参考包时这些测试明确跳过，公开合同检查仍运行。

当前为技术验证通过的配色候选，未由本工具运行客户端，也未完成人工视觉验收。不能据此声称全游戏美术完成。

本批已由 root 安装到用户提供目录，安装后重新惰性解析，目标 SHA 与清单一致；全部 830 个代码段保持原值。变更的是超链接前景和共享描边颜色，实际 GUI 字库效果仍待验。 [安装回读](../../../docs/native-ui-color-installation-20261114.json)

2026-11-14 文案叠加：54b目标是颜色层的中间基线，当前uiMain在此基础上叠加两处自有文案后为132ffe6179118c04c74a78c128acad027853eb4c65704e8b3ce20b09faf66d38。默认verify可严格逆还原文本字段后验证颜色，不写文件，并返回实际SHA与upstreamBrandTextVerified。颜色apply/restore会拒绝直接覆盖文案版；完整恢复必须先用 [文字工具](../brand-text-v1/README.md) --restore，再用本工具 --restore。 [当前叠加回读](../../../docs/native-ui-color-installation-20261114.json)
