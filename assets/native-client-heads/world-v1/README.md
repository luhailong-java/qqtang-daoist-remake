# 五件头饰的原生世界帧

2026-11-14（America/New_York）。本批将现有自有头饰 39 云玩珍藏篮、114 绯霞纱花环、407 霞角鹿灵、2000 五心祈愿及 408 绯耳灵伴导出到各自的 stand／walk 原生路径，共十份 IMG、240 个源位置、94 张独立原生 PNG。固定 ZIP 和用户目录的十个路径均为松散文件。 [原生安装清单](manifest.json) · [源 IMG 合同](source-contract.json) · [静态路径核对](../../../docs/NATIVE_HEAD_WORLD_INSTALL_PLAN_20261114.md)

现有画稿已在原帧四倍画幅内注册。转换器对完整 density4 帧作一次预乘 Alpha 的 0.25 等比 LANCZOS 缩小，直接得到原帧宽高。原始偏移、声明画布、未知头字段、索引、别名、空标记、帧数及 RGB565／Alpha32 模式均保留。五件的源 stand／walk 各自字节相同，导出也逐字节相同。 [原生像素浅深底对照](contact-native-light-dark.png) · [转换器](../../../scripts/build-native-head-world-art.py)

逐帧保存输入画稿、加工来源、母图及生成记录的实际摘要。现有画稿的模型记录保持原值，本批为确定性格式导出。十份资源均已通过结构、像素编码及重复重放检查，原时序和角色头挂点仍待核验，小尺寸外观、遮挡和动作衔接待人工审核。

本批已安装到用户提供目录的十个松散路径，写入后逐文件回读一致；人工视觉及运行仍为待验。独立副本通过安装、重复执行与恢复检查。原文件备份位于项目忽略目录 `.artifacts/native-client-ui-backup/world-v1/` 的客户端专属子目录，此批不写 object.pkg 或 object.idx。 [综合回读](../../../docs/native-client-installation-20261114.json)

```powershell
python -B scripts/build-native-head-world-art.py --check
```

恢复本批时需单独指定其清单。默认 UI 批次不会恢复头饰。

```powershell
python -B scripts/install-native-ui.py --client-root "$env:USERPROFILE\Downloads\ABDM\Compressed\QQTang-Local\QQTang-Local\runtime\client-patched" --manifest assets/native-client-heads/world-v1/manifest.json --restore
```
