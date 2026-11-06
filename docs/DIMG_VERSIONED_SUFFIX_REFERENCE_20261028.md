# 65537源图尾部的参考读取边界

名片装饰12504的walk文件为75,656字节，SHA256 `58b767b36a089ba9d69021f719cabb9bfcf44cf7de53fca44fb81dd184f33ef8`。头声明版本65537、4帧、1方向、115×18；按声明逐条有界读取4个BGRA帧后结束于33,272，尚余42,384字节。默认严格读取器因此拒绝整个容器，先前未输出该参考，也没有把尾部猜成更多帧。

固定社区源码 [dimg.go的231–240行](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/itemcatalog/dimg.go#L231)（Git blob `c8e5e7a22c12ec18e63068b18f224497b5157f01`）明确在65537时允许声明帧之后仍有后缀；其注释的原生核查范围不能自动扩展到本文件。本项目没有执行该代码，也不据此认定尾部用途或腾讯原件身份。

为继续不依赖未知尾部的结构取证，读取器新增**显式、仅参考**选项 `reference_only_version65537_suffix`，物品提取CLI需逐次提供 `--declared-frames-reference`。它只按头和已有严格帧边界解码声明帧，保留整个输入SHA、已读字节数、尾部字节数与SHA，`strictCompleteContainerAccepted:false`、`referenceOnlyOpaqueVersionedSuffix:true`及未知解释。原文件不修改、不截断，尾部不删除、不忽略记录、不推测新帧；完整包仍保留在固定来源ZIP中。

默认精确长度门槛保持，65536有尾部仍拒绝；不提供该显式选项的65537亦仍拒绝。该路径只生成referenceOnly／notRuntimeArt参考PNG，不能作为完整容器验证、原生调用验证或运行资产。采用美术另行生成与记录，几何／状态／播放时序仍pending。本轮未运行全套测试或客户端；资源时段交还后再对默认拒绝、版本限制、边界与新增参考路径作相应检查。

已给 `tests/dimg-reference.test.py`补充人工字节夹具用例：默认拒绝后缀、显式65537参考保存未知尾部哈希且不增加帧、不得绕过版本／尺寸／像素长度边界、精确长度65537仍有完整容器证据。当前按资源暂停约定**未运行**；恢复后显式执行 `python tests/dimg-reference.test.py`。Node测试不自动发现该Python文件，不将此前46项Node通过当作此改动的验证。
