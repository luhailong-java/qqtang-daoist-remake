# 原生展示文字数据补丁候选

本计划只替换5个原生UI模块中的9个指定GBK字节串常量。它不修改回调、URL或字节码，不执行/导入原客户端、不构造CodeType，也不安装实际目录。候选PYC只在忽略目录 `.artifacts/native-client-brand-text-v1/after/res/uiRes/`；公开目录只保存构建脚本、manifest和说明。

| 模块 / 精确scope后缀 | const | 新文字 |
|---|---:|---|
| levelCFG / LevelCfg | 182 | 灵葫道友 |
| levelCFG / LevelCfg | 201 | 灵葫真人 |
| levelCFG / LevelCfg | 209 | 灵葫大天师 |
| uiMain / PlayerWord | 12 | 恭喜你们已在灵葫仙境结为道侣! |
| uiMain / C2CDealDlg.children.NegotiateBtn.OnClick | 5 | 您的灵玉不足，本次出价未成功。 |
| uiRoom / selMapDlg.children.sel.OnClick | 6 | 灵葫温馨提示 |
| uiSelSect / billboard | 13 | `    灵葫大作战，欢迎道友！`（前导四个空格） |
| uiShop / functionTab.OnClick | 8 | 灵玉 |
| uiShop / ware1.children.buyA.OnClick | 23 | 灵玉 |

完整scope、旧文字、新文字、GBK原始长度及前后SHA均在 `manifest.json` 的逐模块 `proof.reversibleStringFields` 中。范围是绝对PYC字节偏移的半开区间，包含marshal字节串标签`s`、4字节小端长度及GBK负载，支持可变长度的局部可逆替换。选取依据是精确scope+constindex+旧字符串+该scope的字节码哈希，不以全文件字符串搜索替换。

`uiMain` 的before **必须是已着色版本** `54b1bc67712edcf6ee4649effa9adf1e1d7b66174bd9bb637cbf3f90b02b9bf6`。构建时由固定ZIP原版施加既有 `native-ui-color-data.py` 合同得到该前像；原未着色ZIP版作为调用输入会拒绝，避免覆盖已经安装的提示字色修复。文字恢复的目标也仍是这份着色版本；若将来同时恢复颜色，应先恢复文字，再使用颜色工具恢复。

每次构建与回放均完整惰性解析五个模块的2,257个代码scope，比较所有 `co_code` 字节；after树只还原这9个指定常量后，必须与before树**整体相等**。同时检查对象计数、8字节PYC头、所有URL常量和9个字段以外的全部序列化字节完全不变，并按after范围逆向局部替换还原精确before字节。uiRoom的8个同名 `filterMap.<lambda>` 以出现序号保留，未被字典去重遗漏。

构建API：

```python
before, after, proof = prepare_module(module_name, raw_bytes)
```

只接受manifest中5个模块的精确before或本计划精确after字节，其他版本、被篡改文件和原未着色uiMain都拒绝；两种已知输入返回同一个规范before/after/proof。API只处理字节，不接收客户端路径、不写文件。

生产 `prepare_module`、事务apply/restore和颜色只读兼容**不依赖源ZIP或私有候选文件**。before输入以固定SHA锁定后直接生成after；after输入只在指定scope/index逆替换9个展示字段，要求恢复出的before SHA精确匹配，再重建canonical after并完整证明。`pinned_pair`/ZIP只供最初构建来源检查。测试已清空来源缓存、将ARCHIVE指向缺失文件，并在真实惰性字节样本的事务/颜色只读/恢复过程中禁止打开ZIP，均通过。

从仓库根目录构建私有候选或只读检查：

```powershell
python -B assets/native-client-ui/brand-text-v1/build-plan.py
python -B assets/native-client-ui/brand-text-v1/build-plan.py --check
```

该计划的 `installedToClient`、`nativeRuntimeVerified`、`textWidthVerified`、`visualAccepted` 仍为false。实际文本宽度、字库覆盖、运行分支与画面效果尚待原客户端验证；URL、启动器/窗口标题、可执行文件品牌和其他展示文字不在本计划范围。后续事务安装必须独立备份、精确前像校验、逐文件回读，并保留已有颜色版本。

事务器为 `scripts/native-ui-brand-data.py`，默认仅verify。以下为接口；独立候选制作阶段没有安装，随后协调安装的实际回读见文末：

```powershell
python -B scripts/native-ui-brand-data.py --client-root "<runtime/client-patched>"
python -B scripts/native-ui-brand-data.py --client-root "<runtime/client-patched>" --apply
python -B scripts/native-ui-brand-data.py --client-root "<runtime/client-patched>" --restore
python -B tests/native-ui-brand-data.test.py
```

`operate(client_root, action='verify')` 返回可公开的只含目录alias的回读对象：`files[].actualSha256`、before/afterSHA、模块状态、`verifiedFileCount=5`、`verifiedUnchangedCodeScopeCount=2257`、`displayConstantCount=9`、`verifiedUnchangedUrlConstantCount=10`、`changedFileCount`、`backupVerified`、`actualUiMainSha256`、`uiMainColorIntermediateBaselineSha256`、`upstreamColorPatchPreserved`。公开结果不含实际客户端路径；私有备份与事务回执位于 `.artifacts/native-client-ui-backup/brand-text-v1/<目录alias>/`。

事务器在写入前完整预检五文件和公共依赖哈希，拒绝未知版本、reparse路径、运行中的客户端及不匹配私有备份；使用OS锁，并在每个原子替换前重新验证前像。失败仅回退本事务尝试写入、且当前仍精确等于本事务desired的文件；外部竞争写入不会被回滚覆盖。已着色uiMain在文字恢复后仍保留54b版本。已经带文字版本而没有本工具备份时，重复apply只识别版本，不声称已有备份，restore会拒绝。

`native-ui-color-data.py` 仅verify分支已兼容叠加后的 `132ffe6179118c04c74a78c128acad027853eb4c65704e8b3ce20b09faf66d38`：经brand严格逆还原至54b再验证原颜色合同，返回 `actualUiMainSha256`、`upstreamBrandTextVerified=true` 与完整叠加证明，不写文件。颜色apply/restore对brand版保持拒绝，并提示先运行brand文字restore；不会用54b覆盖新文案。旧颜色回执的54b只代表中间基线，不能冒充文字叠加后的当前SHA，实际新回执须在真实安装后重新生成。

2026-11-14 实际安装：协调者已将五份文件的九个展示常量安装到用户提供目录，完整回读确认2,257个代码段及全部网址未变，私有备份已验证；uiMain当前为132ffe版本，原有颜色层保留。计划内的installedToClient=false描述候选构建器不安装；当前文件状态以 [安装回读](../../../docs/native-ui-brand-installation-20261114.json) 为准。GUI、文字宽度和运行仍待人工验收。
