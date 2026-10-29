# 宠物技能书静态图标

2026-10-28首轮80/80候选已落盘，14张内置生成母图A–N，80张256×256RGBA独立静态图标。制作范围：社区版本848目录 skill 类80项（27001–27080），8种功能各1–10级。名称、描述、效果与installed_files来自 references/qqtang-item-data/catalog.json，原目录身份未证明覆盖腾讯全部历史版本。不是技能动效、人物动画或业务接入完成。

源DIMG逐次仅解码1–6明确ID；references/structure-*.png为保比例检查放大，只参考书本形态和等级，不作为运行像素。每张内置生成图实际附该批结构图、image两张主风格图，以及本项目 assets/items/items-a-v1.png 的自有图标完成度参考。每次生成前实际重读 image/AGENTS.md、统一配置与执行策略。型号/质量入口未披露，actualModel/actualQuality=null，配置目标另存。

skills-*.png.generation.json、prompts/ 与 exports/ 保存真实提示词、时间、参考哈希、裁区；icons/*.png.provenance.json 保留原ID/名称/描述、alpha、等比裁显、缩放与来源。导出256×256RGBA，原生模型母图另记尺寸；缩放非新生图。等级数字和功能小章帮助区分，文案/数值仍以数据目录为准。

逐批实际看完母图，1–10数字序列及功能书皮已画出，未将母图目视算作运行验收。N只有两书，实物超出名义512格，已实际隔离裁区（40,0,560,580）与（570,0,1100,580），完整保留玉心/流苏。K和L双勇气组小徽记组合、材质/书扣和书脊在不同批次有轻微变化，统一性待复核。全部 visualAccepted:false、runtimeAdopted:false。透明软光、64px可读性、逐件数字/功能标识及实际挂点仍待验收。本机重型作业时段由其他任务使用，不做全量解码/扫描/编译/测试，只继续每批必要小落盘。

项目关联：QQ堂道家Q版重制，GitHub https://github.com/luhailong-java/qqtang-daoist-remake 。本目录实际新图位置 assets/items/skills/；image相对来源 designs/mail-ui-v1/01-mail-event.png、designs/team-ui-v2/team-ui-v2.png，关联类型风格参考。核实日期2026-10-28，image自身远端与本项目地址分别在主关联记录保留。
