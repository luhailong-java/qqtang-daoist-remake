# 六件童趣背包库存源合同

本主题的封闭规则为源 `catalog.json` 中 `category=npack` 且 `name` 字面包含“背包”的全部条目，严格得到6个ID；它是完整题名主题，不冒称同一发行套装，也不把所有背饰或“旅行包/背袋/伪装成背包”的其他物品混入。本轮只补这6件库存候选，世界动作另行制作。

|源ID|源名|精确icon资源|本项目身份|物理包络尺寸|
|---|---|---|---|---|
|1169|足球背包|npack82.img|蹴云圆囊|25×25|
|1329|月兔背包|npack94.img|月兔行囊|22×26|
|1330|考拉熊背包|npack95.img|云栖考拉囊|41×35|
|1331|可爱小熊背包|npack96.img|山灵小熊囊|36×33|
|1553|小猪猪背包|npack107.img|福豚锦囊|35×38|
|3027|甜筒背包|npack224.img|灵酪甜筒囊|38×47|

精确资源从 `references/qqtang-item-data/catalog.json` 各条 `installed_files` 选择 `res/uiRes/icon/npack/*.img`，不按名字或源ID猜资源号。固定ZIP `.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip` 的SHA256已实际核对为 `fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7`，member前缀 `QQTang-Local/runtime/client-patched/`。这是社区修改样本，不冒称已证腾讯原版美术/版本。

唯一物品输出目录 `assets/items/back-adornments/travel-backpacks/`。源IMG只静态读取并用项目可信DIMG解码器，未执行客户端。每次最多6个明确源ID，分别恢复6张库存源图、各件世界源位置0静态图；精确member/IMG SHA/编码像素SHA/解码RGBA SHA/PNG SHA/原frame记录与rawOffset都在本目录 `references/{ID}/`。

前五张库存源是56×53的蓝色不透明UI框图，native alpha覆盖UI，不能拿整个alpha当物理包络。原图完整保留；本轮实际观察物理边界，暖色/中性前景RGB仅用于辅助测量，再作reference-only整数裁口：1169 `[15,14,40,39]`；1329 `[17,13,39,39]`；1330 `[7,9,48,44]`；1331 `[10,10,46,43]`；1553 `[10,7,45,45]`。物理裁图仍保留角落蓝色源像素供参考，不程序抠图冒充新画。字段明确 `notNativeAlphaBBox=true`。

3027库存源38×50、rawOffset=[10,3]，底部黑椭圆是非物理UI落地阴影。按有色物理甜筒完整边界取 `[0,0,38,47]`，角落重叠阴影仍只作源参考。新图明确省略这些UI框/背景/阴影，用AI直接生成真实透明物件。所有源像素reference-only，不直接充运行素材。

姿态合同：圆球保持圆形轮廓；月兔是双竖耳的大脸囊；考拉是灰色大脸+短身，较小暖灰幼考拉袋附在库存图的观察者右侧；小熊是大圆头、圆耳和很短下袋，不能变长身玩偶；小猪是猪脸、双耳、鼻吻和紧凑下前袋；甜筒保持斜向左下尖、粉色圆勺体和右上青/红配件。自己的道家Q版形象提供缝线、玉饰、暖金、象牙白与织物材质，不生成穿戴者或直接照搬源像素纹理。

世界源每件stand/walk文件字节相同，均声明24源位置；这里只解码了位置0。按编码SHA+尺寸分组的数目依次24/13/18/15/10/20，它们只是**编码组**，未解码全位置，不能冒称已核完整独立可见raster。所有源记录/rawOffset保留，cardinal/时长/循环/挂点保持null/unknown。本轮 worldCandidatePositions=0，worldCandidateCoverageComplete=false，pixelReferenceCoverageComplete=false；不把库存齐件说成全相位完成。考拉世界位置0的小袋在另一侧，源图原样保留，不从库存正面猜世界方向或程序镜像。

新库存只生成256×256 RGBA与64/96实际移动端变体；按生成alpha≥16包络对比上述原物理包络，偏差≤10%，并核每种导出尺寸的真实alpha包络。仅裁格及等比premultiplied-alpha LANCZOS派生，不程序画图/拉伸/镜像。母图按真实原生extent登记，提示词预计尺寸不是裁口依据。

仅内置image_gen；项目2.6sunburst/high是已核配置目标，工具没有模型/quality选择器，actualModel/actualQuality=null。每次调用前将functions.store原字符串直接JSON转义封存，CRLF原样UTF-8 SHA，不用read_text换行归一重构。完整prompt、原始prompt文件SHA、refs顺序/角色/SHA、hostSource/返回字段、原母图及编辑裁格来源链都保留；技术未达标用真实AI重试。

全部新候选visualAccepted/geometryAccepted/accepted/runtimeAdopted/completeAnimationAccepted=false，userReviewStatus=pending。禁止GUI/CUA/sky/替代GUI，未获静态、时序、挂点或实机批准。冻结披风目录、其他agent文件、全族采用清单与Git均不修改。
