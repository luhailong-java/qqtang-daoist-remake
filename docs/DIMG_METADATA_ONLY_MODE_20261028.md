# DIMG有界元数据读取（2026-10-28）

`scripts/inspect-reference-dimg.py`新增关键字参数`metadata_only=False`。默认仍解码第一项有尺寸帧、要求严格EOF；显式`reference_only_version65537_suffix`仍仅允许65537声明帧后的未知后缀并保留其长度/哈希。没有修改既有默认调用与CLI入口。

`inspect_dimg(data, metadata_only=True)`只校验签名、版本、帧数/方向数整除、标记、非空帧支持模式、尺寸/总像素计数上限、payload字节长度/边界、offset和EOF，并记录每帧已编码payload SHA。它不调用`decode_frame_pixels`，返回的图片为`None`，不产生`decodedRgbaSha256`、alpha或可见包围框。全部结构空帧的容器可在此模式列出；默认解码模式仍拒绝没有可见图片的容器。

元数据结果显式标记`pixelDecodePerformed:false`、`pixelPayloadValidation:"unknown"`、`visibleAlpha:"unknown"`、`runtimeUsable:false`。为避免将字节结构通过误记为完整像素验收，`strictCompleteContainerAccepted:false`，另用`strictDeclaredStructureAccepted`表示严格完整结构/EOF结果；显式未知后缀存在时后者也为false。不得据此称为可运行资源或完整像素验证。

独立小CLI：

```text
python references/qqtang-map-data/motion-contract/inspect-packed-metadata.py --batch batch-01 --resource object/mapElem/town/elem50_stand.img --resource object/mapElem/town/elem51_stand.img
```

每次明确选择1–6个不同的`--resource`，不接受自动全包扫描。可逐资源重复`--expected-sha256`，数量和顺序须与资源一致；可用`--output-dir`指定项目内自有目录。默认输出`references/qqtang-map-data/motion-contract/metadata-batches/<batch>/`。默认不接受65537后缀，需要逐次显式`--reference-only-version65537-suffix`。

CLI只读固定object.idx及所选包字节区间，有界zlib解包，核对索引哈希、包长度、原始/压缩区间SHA与现存源证据；不重新哈希大包或ZIP。对其他族尚无既存原始SHA的资源应显式传入预期SHA，记录中会区别是否有预期值。原SHA与图片查找关系仍是社区源/候选证据，不能证明腾讯原始客户端身份。

CLI另将模块的`decode_frame_pixels`设为禁止调用护栏，确保此入口不能意外RGBA；结果记录每帧尺寸、offset、结构空标记、encodedSHA和EOF。`encodedRasterGroups`比较模式/尺寸/payload SHA，`sameRasterAndOffsetGroups`还比较offset；跨定义整DIMG SHA不参与帧内部归组。同payload不同offset仍是不同摆放状态，不自动删除。

不同payload组只证明编码字节不同，未证明可见RGBA不同；可能含全透明或等价像素。帧名、方向、循环、时长和动画/破坏态语义不猜。新画清单必须先以明确代表帧作小批视觉/调用取证，再确定真正不同的美术状态。

人工字节夹具已写入`tests/dimg-metadata-only.test.py`，涵盖禁止解码、默认行为、空标记、offset、长度/模式/EOF拒绝、65537后缀和payload/offset分组。按本机重型任务暂停约定，**未运行这些测试**。本轮生产读取不生成PNG、不生图、不运行浏览器或客户端、不操作Git。
