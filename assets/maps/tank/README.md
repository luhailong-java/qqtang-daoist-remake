# 机关地图补充美术

2026-10-28：二进制补充19030—19054共25/25个ID有新画候选，accepted仍0。原40px格子、帧尺寸×4导出、占地、GridAttr和源偏移按二进制证据保留；图片文件名关联仍candidate，canDoSpecial/canHide因二进制未序列化保持null。

`binary/`含真实母图、提示词、generation记录、结构参考板和小批导出。A/B/C/D共18件裁切等比导出；E新增水面和土材质，结合D草地，以原40²草/土/水区域掩模合成19048—19054共7件。合成未复制原RGB，不属于新的模型生成；每次最多3ID，记录在`binary/exports/terrain-*.json`。所有7件160²、alpha255，源岸线阶梯拓扑严格保留。水纹和草地铺接、土材质偏暖与阶梯边缘手绘融合仍未验收。

19030/19031坦克建筑使用本项目道童身份替换源腾讯人物；保留炮口、风扇窗、开盖、前入口和车体。源木箱/钢罐文字用云印替换。主风格真实引用image两张指定主图；实际内置入口不披露型号/质量，记录目标Sunburst/max、实际null。

明确待修：19037树首稿可见比例偏宽约21.3%，G独立重画已改善为约5.87%，仍未验收，19040圆罐重新查看单件源帧确认原本双槽，首稿双槽保留；G为19037当前最佳候选；其余所有建筑内结构、锚点、边缘/接缝、实机均未通过。当前只能做必要小批落盘，不运行全族扫描、编译或测试。

## 项目关联

- 项目：QQ堂道家Q版独立复刻；GitHub：https://github.com/luhailong-java/qqtang-daoist-remake 。本轮资源尚未提交/上传。
- image仓库origin：https://luyuacpp.visualstudio.com/image/_git/image ；image的GitHub地址待确认。
- 风格参考：`designs/mail-ui-v1/01-mail-event.png`、`designs/team-ui-v2/team-ui-v2.png`；新项目实际位置`assets/maps/tank/`。
- 源结构：本项目binary-supplement参考索引、解码帧，仅用于形状及地图拓扑，不复制原画RGB。核实日期2026-10-28。
