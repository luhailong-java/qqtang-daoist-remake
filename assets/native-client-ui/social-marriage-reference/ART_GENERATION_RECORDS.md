# 本组原创母图生成记录

本组真实调用宿主内置 `image_gen` 四次，得到下列四张原始 PNG。没有使用收费后备 API，也没有执行本地生成 CLI。宿主返回未披露实际模型与质量，`actualSubmittedModel/Quality` 与 `actualReturnedModel/Quality` 均记为 null；文件时间只记录返回文件的 UTC 修改时间，不冒充服务端生成时间。

完整逐字提示词、透明参数、风格参考文件及 SHA、工具返回提示、宿主原文件位置和每张原文件 SHA 均位于各自 `.png.generation.json`。请求总表为 `generation-requests.json`，工具返回总表为 `tool-results.json`，可机器复核汇总为 `illustration-evidence.json`。

| 母图 | 原文件 | 原尺寸/模式 | 用途 |
| --- | --- | --- | --- |
| 朱绢道侣庭院 | `illustrations/red-covenant-court-master.png` | 1341×1173 RGB | 原生朱绢背景及其缩略图 |
| 月门桃园 | `illustrations/moon-peach-garden-master.png` | 1341×1173 RGB | 原生月门背景及其缩略图 |
| 朱袍葫芦礼官 | `illustrations/cinnabar-ceremony-officer-master.png` | 1254×1254 RGBA | 大小礼官图与朱绢确认对话插图 |
| 玉衣结缘仙翁 | `illustrations/moon-knot-sage-master.png` | 1254×1254 RGBA | 大小礼官图与月门确认对话插图 |

两张用户已有风格图 `references/image/01-mail-event.png`、`references/image/team-ui-v2.png` 仅作玉金纸绢 Q 版风格参照。提示词明确要求全新场景及人物，不复制参考的 UI、文字、人物或布局；未提交 QQ 堂原人物或原场景作为编辑底图。

返回原文件位于 `C:/Users/luyua/.codex/generated_images/01a1d950-0e35-7500-a9be-e8db30fb08ca/`：

- 朱绢庭院：`exec-b3b6fe45-6d8e-4f2a-9163-f3a4d9490094.png`
- 月门桃园：`exec-10f20f36-2403-4cd0-819a-dc6db6e69f9c.png`
- 朱袍礼官：`exec-74011c0f-c6f5-4504-b232-3e327f6c8f1c.png`
- 玉衣仙翁：`exec-2e39df9b-4b88-468f-8309-57d13cd2acb8.png`

仓库的四张 master 是实返文件的字节相同副本。裁边、缩放、背景合成只在渲染派生原生资源时进行，不回写母图。四次生成供应十件派生原生资源，不计为十次生成。礼官透明边缘取自自有实返母图，未使用 QQ 堂原人物 Alpha。

静态图与引用哈希已检查；用户视觉确认、原生角色站位/遮挡、运行分支及原时序仍待验，不能将生成成功等同整款游戏美术完成。
