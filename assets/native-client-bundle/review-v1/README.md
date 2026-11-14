# 统一原生图片安装包

2026-11-14。当前统一包 **1,482个资源／2,548个非空位置**：UI837／1590、库存583／602、五件头饰世界10／240、地图52／116。实际用户目录已升级并完整回读，UI另保留1个结构空位。 [清单](manifest.json) · [源合同](source-contract.json) · [实际回读](../../../docs/native-client-installation-20261114.json)

包保留原object.pkg完整前缀，824条索引指向自有zlib流，其他2,658条不变；另替换658个松散图像。总660个实际文件备份在项目忽略的 `.artifacts/native-client-ui-backup/review-v1/` 客户端专属子目录。Client.exe不变。独立非执行副本已验证安装、重复执行、全量回读和恢复，实际客户端未运行。

地图120件／224位候选中只默认安装52件／116位；68件Alpha包络或不透明性警告仍排除，6件缺序列未导出。头饰保留注册后的完整四倍帧整体降采样；库存按可见内容等比适配，两者不能混用。3941库存的版本／尾部兼容封装例外仍待运行。TGA保留原头尾与方向，GIF保留原时间属性和C4控制位，调色板／LZW长度允许变化。 [格式](../../../docs/NATIVE_UI_FORMATS_20261114.md)

验证及恢复：

```powershell
python scripts/build-native-art-bundle.py --check
python scripts/install-native-ui.py --client-root "$env:USERPROFILE\Downloads\ABDM\Compressed\QQTang-Local\QQTang-Local\runtime\client-patched"
python scripts/install-native-ui.py --client-root "$env:USERPROFILE\Downloads\ABDM\Compressed\QQTang-Local\QQTang-Local\runtime\client-patched" --restore
```

共享链接颜色和五份UI文字数据独立于图片安装包。文字层9个展示常量、2,257个代码段及网址保留证明另记；图片恢复不撤回数据层。撤回数据时先文字工具、再颜色工具，颜色工具不会直接覆盖132ffe组合版本。 [文字及恢复](../../native-client-ui/brand-text-v1/README.md) · [颜色及恢复](../../native-client-ui/text-color-v1/README.md)

**原生全部UI和整款美术仍未完成。** 包内772个UI图像已覆盖，非库存UI仍缺168个表情，库存仍缺2622个图像路径；人物完整动作、其余装扮、地图全态、怪物、特效、音频及运行验收继续待补。 [最新差额](../../../docs/NATIVE_UI_REMAINING_20261114.md) · [完整交付](../../../docs/ART_DELIVERY_20261114.md)
