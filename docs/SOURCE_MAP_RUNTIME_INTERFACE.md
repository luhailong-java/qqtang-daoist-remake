# 社区源地图运行接口与边界

核对日期：2026-10-26。优先需求为 `USER_REQUIREMENTS_LOCK_20261026.md`。本轮未运行外来 Python、EXE、DLL 或社区工程。

## 数据与证据

`src/original-maps.js` 仅读取已导出的 JSON 数据；`server/map-catalog.mjs` 读取固定本地目录并验证逐图导出 JSON 的 SHA256。381条目录全部返回，377个地图文件的数据来源仍为社区修改后客户端，未获腾讯原始身份认证。22张存在未知正元素ID的地图停止导入，不猜碰撞或贴图。

本轮实际静态阅读固定提交 `4b3a245fd985cabd4abd68ade6c282cc163d9edb` 的以下源码，未执行：

- [competitive_battlefield.go L32–59](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/competitive_battlefield.go#L32-L59)：人物方向位0..3，火焰方向位8..11；出生起点出向属性单独来自序列化layer0；静态对象占据与通行独立。
- [同文件 L223–304](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/mapdata/competitive_battlefield.go#L223-L304)：仅正锚点实例化；负值为延续标记；占地从正锚点向右/下按size展开，原点不使用贴图offset；两层按层/行序安装，重叠为后写覆盖；LifeTime与通行位分开。
- [types.go L138–177](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/battleengine/types.go#L138-L177)：右8、上4、左2、下1；人物起点用反向exit位，目标用行进位；火焰用同方向位左移8。
- [movement.go L80–96](https://github.com/kuuhaku1314/qqtang/blob/4b3a245fd985cabd4abd68ade6c282cc163d9edb/internal/game/battleengine/movement.go#L80-L96)：社区像素碰撞还有中心/边缘/转角探针，当前格级引擎没有复现这些细节。

据此保留完整三层、所有使用元素的size/GridAttr/offset/属性、出生组和目标表，并生成**候选碰撞投影**。layer2作为原始地面/展示数据保留，不据它覆盖前两层碰撞。每格保留方向位、layer0出向位、耐久、实例ID及占地，`grid`的0/1/2只是显示兼容摘要。40px格距、600×520等逻辑像素为固定社区实现常量推算，尚未取得腾讯原件交叉核验。

## 首张导入与范围

中国城01：`source-201`，目录ID201，`town01_4.map`，15列×13行，最多4人；原文件SHA256为 `10f84593742d90af379f9698d7e003111ea8c5b209f87ac27f3717afdcbec4ca`。出生组A按原顺序为 `(11,12)、(1,0)、(12,0)、(2,12)`；B组和目标表为空，没有补造抢包据点。元素3019完整4×2占地保留，没有按一格压缩。

当前仅原生规则1目录可启动本引擎的普通竞技，且需元素、占地、出生检查通过。其他原生规则仍列实际数据与禁用原因。抢包/足球/推箱/PvE不套用中国城01，也不把三张技术试稿换名当作源地图。50张非15×13保留文件头宽高；当前均不属于已支持规则，不能启动普通竞技。

`courtyard/town/factory`仅保留为明确的`draft-map`兼容技术测试，目录展示在独立`draftMaps`字段，状态`unaccepted-custom-draft`。

## 服务接口

- `GET /api/maps`：无需身份，返回`maps`实际381条目录、`draftMaps`三张试稿、来源哈希和投影证据。每条包含`id/name/catalogId/width/height/maxSeats/nativeRule/playable/playableModes`；禁用项含`unavailableCode/unavailableReason`。
- `GET /api/maps/source-201`：返回`map`描述和`sourceMap`完整已编译候选数据（含三层、元素、坐标表、实例、碰撞）。不存在返回404。已知但无法编译的图`sourceMap:null`且描述解释原因。
- `POST /api/rooms`示例：`{"name":"中国城练习","map":"source-201","mode":"classic","bots":3,"duration":180}`。`source-201`强制最多4席，超限AI/席号被拒绝；第五位人类不能进入满人房。
- `/api/state`与SSE中的`currentRoom`含`max/maxSeats/mapInfo`，房间列表的`max`同样来自实际地图。`mapDirectory.url`指向完整目录。前端不能继续固定生成8席，应采用房间上限；源图只显示其`playableModes`。
- `/api/action`的`config`使用同一地图标识；缩小人数时如已有高位真人或人数过多将原子拒绝，房间旧配置不变。

引擎使用 `createGame({map:'source-201',sourceMap:compiled,participants,...})`。没有`sourceMap`时源标识直接报错，不退回随机布局。`width/height`、出生、边界、方向碰撞和爆炸均取源数据；源图启动不会随机放箱、加边界墙或生成目标。`game.sourceMap.layers/tables/elements`是保留的来源，运行破坏另记于`sceneObjects`和候选`collision`，不改原始层值。

## 验收与未完成

测试覆盖首图三层/哈希/出生/4席、4×2占地、方向人物/火焰分离、负标记保留、未知元素/超界拒绝、19×7人工夹具的真实边界与爆炸、40×17实际PvE数据不降格、源耐久与无随机替代、HTTP地图目录和第五人拒绝。人工夹具只验证代码能力，不作原版地图证据。

尚未完成：腾讯原始身份/目标版本认证、原生像素碰撞与转角滑动、普通竞技的原生推物细节、原道具ID与墙内/隐藏物品行为映射、特殊原生规则、原美术贴图锚点与原创道家Q版同坐标美术替换。源图不使用试稿随机掉落表掩盖缺失。以上限制保留在每个`sourceMap.runtimeLimitations`，不能将候选可运行写成原版1:1验收。

中国城01以3个种子、无人操控真人各模拟60秒，均完成计时结算，源层仍各195格，未插入随机箱子或改变出生区。当前保守AI受紧凑出生区与上述未复现细节限制，部分角色仅走动，整局约2次放泡/4个破箱。此结果是后续原版机制研究的具体缺口，没有为改善演示移动源图建筑、扩大通道或降低原占地。
