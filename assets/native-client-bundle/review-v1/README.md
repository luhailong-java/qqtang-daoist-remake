# 统一原生图片安装包

2026-11-14。此包聚合已经导出的自有图片：242 件 UI／570 个位置、583 个库存图标／602 个位置、五件头饰的十个世界资源／240 个位置，以及 52 件地图元素／116 个位置。合计 887 个原生资源、1,528 个源位置，已安装到用户提供的 QQTang-Local 目录并完整回读。 [清单](manifest.json) · [原格式合同](source-contract.json) · [安装证据](../../../docs/native-client-installation-20261114.json)

地图源包与 UI 共用 object.pkg／object.idx，因此不能用一个独立的原始地图包覆盖当前 UI。本次先逐批安全恢复已校验的原文件，再统一安装当前图片清单。292 个包内条目指向新的自有 zlib 流，原包作为完整前缀保留；其余 3,190 个索引条目不变。另安装 595 个松散图像文件。原文件备份统一位于项目忽略目录 `.artifacts/native-client-ui-backup/review-v1/` 的客户端专属子目录。

地图共导出 120 件候选／224 个源位置，此包只采用其中 52 件。13 件源不透明而新稿透明、59 件可见包络差异的警告保留在原清单中，合并去重后 68 件未默认安装；六件缺完整序列未导出。自有头饰采用完整已注册四倍帧整体降采样；库存图标采用可见内容等比适配，两类不能混用裁边方法。3941 的原不透明尾部按清单作兼容封装，实际运行仍待验。 [地图候选](../../native-client-maps/town-common-v1/manifest.json) · [头饰](../../native-client-heads/world-v1/README.md)

安装器默认使用此统一清单。验证当前安装及重新核对构建可执行：

```powershell
python -B scripts/build-native-art-bundle.py --maps-manifest assets/native-client-maps/town-common-v1/manifest.json --check
python -B scripts/install-native-ui.py --client-root "$env:USERPROFILE\Downloads\ABDM\Compressed\QQTang-Local\QQTang-Local\runtime\client-patched"
```

恢复本批全部图片：

```powershell
python -B scripts/install-native-ui.py --client-root "$env:USERPROFILE\Downloads\ABDM\Compressed\QQTang-Local\QQTang-Local\runtime\client-patched" --restore
```

共享消息链接的文字及描边颜色使用单独的 UI 数据补丁，图片恢复不会恢复该数据。该补丁只变一个共享颜色整数，全部 830 个代码段、网址、文案和回调保持原值。 [颜色数据与独立恢复](../../native-client-ui/text-color-v1/README.md)

全部原生 UI 和整款美术均未完成。已知 UI 图像目录还有 3,384 个路径未转换，其余人物动作、装扮、地图、怪物、特效、音频及运行验收继续待补，不能把此包当成整款终验。 [逐组差额](../../../docs/NATIVE_UI_REMAINING_20261114.md)
