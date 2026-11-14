# 原生客户端自有库存图标

2026-11-14，America/New_York。将已有 584 个自有物品候选逐项匹配目录中的实际库存路径，本批已转换并安装 578 个单帧原生 IMG。原生预览是最终 IMG 再解码的像素，不用高清 PNG 代替原生结果。 [转换清单](../assets/native-client-ui/inventory-v1/manifest.json) · [源格式合同](../assets/native-client-ui/inventory-v1/source-contract.json)

图形取自项目已有自有 PNG，先按 Alpha≥8 的可见范围裁边，再等比放入原生帧。保留原声明画布、原图像宽高、像素模式和原始偏移，使用预乘 Alpha 缩放，避免大透明画布使小图变得过小。没有把库存图标当成角色佩戴、入场或地图动画，也没有增加物品候选 ID 数。

五件多帧资源另行处理：27061、27073 的源位置是技能等级数字，9011–9013 各有两个材质状态。3767 没有唯一的已安装库存 IMG 路径，继续待证，不按编号猜路径。未覆盖的 2,361 个源物品 ID 仍缺自有画稿。

3941 的 `res/uiRes/icon/eye/eye80.img` 是单帧 version65537 容器，尾部有 4,636 字节无法解释的数据。本批使用已支持的 version65536 封装其声明的一帧，保留原声明画布、19×43 图像、偏移、像素模式及其他头字段，排除不透明尾部。清单记录原尾部哈希和封装变更；这是兼容候选，尚未从运行客户端确认显示，不代表已理解原尾部格式。

安装前在独立副本完成安装、重复安装、恢复检查；实际目录安装由原 577 件批次安全恢复后升级到 578 件，随后逐文件回读核对。每批备份在项目忽略目录 `.artifacts/native-client-ui-backup/inventory-v1/` 的客户端专属子目录。此批只写库存图标，不改包索引或主程序。 [安装复核](native-client-installation-20261114.json)

```powershell
python -B scripts/build-native-inventory-art.py --check
python -B scripts/install-native-ui.py --client-root "$env:USERPROFILE\Downloads\ABDM\Compressed\QQTang-Local\QQTang-Local\runtime\client-patched" --manifest assets/native-client-ui/inventory-v1/manifest.json
```

恢复本批库存图标需明确指定本批清单；默认的 UI 清单不会恢复库存批次。

```powershell
python -B scripts/install-native-ui.py --client-root "$env:USERPROFILE\Downloads\ABDM\Compressed\QQTang-Local\QQTang-Local\runtime\client-patched" --manifest assets/native-client-ui/inventory-v1/manifest.json --restore
```

人工视觉、图标实际用途与客户端运行均待验，全部 UI 与整款美术保持未完成。 [完成账](ART_COMPLETION_CHECKLIST.md)
