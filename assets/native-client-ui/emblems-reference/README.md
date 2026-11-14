# 原生徽章、段位、模式图标与光标候选

本组覆盖 `object/ui/kinTotem` 49 件、`level` 72 件、`map` 17 件和 `cursor` 3 件，共 **141 件 / 188 个非空源位置**。只做静态解码、原创素材生成、原生像素导出和结构核对；没有启动原客户端。画面、时序、等级阈值、鼠标热点与运行结果均待验，整款美术未完成。

三档徽章、箭头、伸指/屈指手势和六枚特殊模式图标通过宿主内置图像生成工具实际生成。`masters/*.generation.json` 保存实际提示词、参考哈希、原始 PNG 尺寸、返回文件路径与来源；服务未返回模型/质量，记为 null。铜色 v1 太接近金色，最终采用有单独编辑记录的 v2，保留原稿供追溯。

`process-masters.py` 通过 Alpha<8 的完整透明沟槽分格，逐格裁出主体，并检查裁外没有 Alpha>=8 的可见内容。没有等分后截断主体、取最大连通块、重画主体或沿用原游戏物品 Alpha。`cutouts.json` 记录 33 个切片的边界、哈希与生成记录。后续缩小使用预乘 Alpha LANCZOS，再编码为原生 RGB565/33 阶 Alpha。

`own-mapping.json` 保留每个源槽、源帧尺寸/偏移、原创视觉来源。48 个家族选项使用 48 个不同的自有素材；000 仍为无图案色块。现有物品、食物和地图图形仅作为 UI 图案使用，不声称这些图案建立了物品 ID 或世界实体绑定。c01–c06 与 d01–d06 的六对源文件字节完全相同，因此保留六对共用条章。细小段位条扩展自有玉金 UI 的几何与色阶，未复制原字形。

光标保留普通箭头 9 位、点击手势 2 位和 `fight.gsa` 9 位、画布和偏移；点击光标使用两张分别生成的手势母图，在共同逻辑坐标内配准。后缀为 `.gsa` 的文件经完整解析实际是 DIMG，与包内 `arror.img` 源字节完全相等，因此使用同一组原创箭头。历史 census 原 opaque 记录保留，`native-ui-format-refinements-20261114.json` 追加确证格式。徽章流光和压扁相位是自有候选，未标记为原版实速或终验。

重放：

```powershell
python assets/native-client-ui/emblems-reference/process-masters.py --check
python assets/native-client-ui/emblems-reference/build-plan.py
python scripts/build-native-login-art.py --check
python assets/native-client-ui/emblems-reference/review-candidate.py
python tests/native-ui-format.test.py
```

`candidate-qa.json` 对 141 件 / 188 位逐项核对所有非像素字节、源窗口和导出像素。3 张 `candidate-contact-*.png` 同时显示原生 1:1 与整数放大图，供人工审核；静态检查通过不等于视觉或运行通过。
