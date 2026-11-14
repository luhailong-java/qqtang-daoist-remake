# 原生地图候选转换

本批只转换已有原创候选，没有调用新生图，也没有修改或安装客户端。依据 [转换计划](../../../docs/native-map-conversion-plan-20261114.json) 的120个技术通过定义，导出98个单帧资源及22个完整序列资源，共224个原始帧位。17024–17029缺少完整序列，未导出。

`manifest.json` 的 `items` 包含全部120件；`defaultInstallNativePaths` 仅列52件、116个帧位。该子集的透明度类别与 alpha>=8 可见边界，在4x整帧缩小和原生像素量化后均与源帧匹配。此条件不等于画面、地图查找绑定、组合绘制原点、原时序或原客户端运行验收。

13件存在源图全不透明而候选有透明度的差异，59件存在可见边界差异；两组可重叠。全部具体警告及源/候选边界记录均保留。`accepted`、`geometryAccepted`、`visualAccepted`、`nativeRuntimeVerified` 仍为 false；原始逐帧时长与组合原点保持 unknown。

`source-contract.json` 保留原包/索引哈希、逐资源原始容器元数据、转换计划条目、候选生成/派生/别名证据与哈希。`patch` 保留完整原生路径；`decoded` 是原生编码后独立解码的RGBA PNG。只替换原像素平面，原容器头、帧顺序、尺寸、偏移、模式和全部非像素字节保持不变。4x帧整体以预乘Alpha Lanczos缩小至1x，没有按Alpha裁边或套用库存图标居中适配。

从仓库根目录重放：

```powershell
python -B scripts/build-native-map-art.py --check
```

`--check` 为只读检查：验证输入哈希、所有224位置的整帧重采样、原生编码、解码像素和PNG文件字节、原生非像素字节、元数据及独立zlib往返。实际安装必须由统一包构建器合并到当前客户端资源包，保留已安装UI等资源；不能用固定源包整体覆盖当前包。

本批 defaultInstallNativePaths 的 52 件／116 个源位置，已与既有 UI、库存和头饰统一安装。其余 68 件仅为导出候选，不计入已安装。 [统一安装与恢复](../../native-client-bundle/review-v1/README.md)
