# 自有道家Q版道具图标

2026-10-28。社区样本 `item_config_version=848` 的 `item` 类32项已有首轮原创图标，每项保留原ID、名称和描述，见 `art.json`。这32项只是2,945条物品记录中的一个类别，不等于全部商城、装扮、战斗掉落或技能资产完成。

六张内置生图母图：`items-a-v1.png` 至 `items-f-v1.png`，每张旁有独立 `.png.generation.json`。配置目标是统一配置中的型号和最高质量；内置入口没有开放型号/质量选择器，实际返回未披露，记录为null。实际附上两张主风格参考、对应原物品结构板及需要的自有身份/既有图标参考。原游戏像素只用于功能/形态参考，不作为运行美术导出。

`icons/` 为256×256 RGBA等比裁显候选，透明边缘使用预乘alpha LANCZOS缩放，逐件`.png.provenance.json`记录母图、SHA256、原生尺寸、裁区、缩放和位置。裁切/缩放不是新生图。软光晕、实际背景辨识、清晰度、物品状态和运行挂点尚未完成验收；`visualAccepted`、`runtimeAdopted`全部false。

原物品参考与来源见 `references/qqtang-item-data/README.md`、`catalog.json`。腾讯原始未修改版本身份尚未确认。文字与功能在独立数据层保留，不将药剂外观改动当作规则更改；道童头像礼花替代旧品牌形象。

处理脚本 `scripts/export-item-art.py`，批次裁区 `docs/items-a-export.json` 至 `items-f-export.json`，实际提示词 `docs/items-*-v1.prompt.txt`。本轮仍受本机重型资源协调约束，未做浏览器或全量QA，见 `docs/LOCAL_RESOURCE_WINDOW_20261028.md`。

其他独立类别继续生产：`skills/art.json`80项、`food/art.json`10项、`forge/art.json`7项、`petcards/art.json`首批6项；均为未接入、未终验候选，各有自身母图／来源与裁显记录。`battlefield/art.json`另按sceneId记录18个对局拾取物首帧，对应17个不同PNG，和账号库存物品ID分开；源资源完全相同的26／62显式共享新图，不将共享或裁切算作新模型生成。完整来源物品目录仍为2,945项，这些小类别进展不等于全部完成。
