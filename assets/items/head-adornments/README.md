# 头顶装饰：背包图标与世界表示分离

2026-10-28：thadorn源类别35/35项已有256×256 RGBA背包静态候选，A—F六张首稿母图、G单件竹蜻蜓修图。全部accepted/visualAccepted/runtimeAdopted为false。背包图标不是头顶世界sprite或完整穿戴动画。

先实际读catalog名称/描述/installed_files，再对stand/walk分别读取DIMG小头，并显式--inventory-icon取得真正res/uiRes/icon/thadorn图。没有拿object stand当背包图。source-state-inventory.json记录35项70个世界资源头：31项24帧4方向/v65536，2项24帧4方向/v65537，42为2帧1方向、54为4帧1方向；stand声明总798帧，walk逐项与stand字节同SHA。此为源声明，不是已生产的新图，也不代表帧内去重或时序验证。rawOffset/未知头字保留，世界头未全解析，不能当完整容器已验证。

4499/4556真正inventory为65537/BGRA，严格完整解析成功，无未知后缀例外。4556 inventory RGB全白、alpha亮斑，无可辨内部环线；sourceVisualLimitation保留，当前自有光圈依源描述设计，原生混合与世界内部几何待定。若后续世界65537有未知尾段，只能显式reference-only记录，不能套正式运行。

图标art.json保留原itemId/category/sourceName/sourceDescription、真inventory引用/哈希/原帧/offset，另列projectDisplayName。3931/3932原积分+1%仍在原描述，未改能力。QQ娃娃/酷比脸换自有道童或仙灵；NBA鹰标换原创玉羽灵鹰，不复制球队标志。1368/1369改为本项目10/1云冠视觉，源周赛奖励/非卖描述保留。蓝框、头部占位椭圆和投影没有复制入新背包图。

真实采用的image身份见adoption-index.json：旧包11霞角鹿→407，新包14绯耳灵→408，04桂灯童→1539。使用同项目petcards/references/canon中的已核实字节及历史记录；这只是本项目新外观选择，不是腾讯历史人物关联或MMO属性映射。原image内容未改，关联由协调者统一更新。

每次内置image_gen实际附功能图、两主风格、自有items-a完成度参考；必要身份用真实图片板。目标Sunburst/max、实际型号/质量null按逐图记录。切片等比缩放如实记录，不是新模型生成。A/B/C/D/E/F部分物件跨名义512边界，已按实物间隙独立裁切；没有非等比挤压。G去掉236竹蜻蜓不应出现的小电弧。42/54背包又从真实高分辨世界新画母图切出，复用而非新生图，54孤立邻图白条已消失；42弱红alpha散点仍待清理。当前只做必要小批落盘/目视，未跑全包QA、构建或实机。

## 世界表示缺口

当前42（2位置/2PNG/1方向）、44（24位置/18PNG/4声明方向）、54（4位置/4PNG/1方向）、138（24位置/9PNG/4声明方向）、236（24位置/4PNG/4声明方向）、1246（24位置/6PNG/4声明方向）、1311（24位置/10PNG/4声明方向）、1248（24位置/12PNG/4声明方向）、1296（24位置/12PNG/4声明方向）、1312（24位置/12PNG/4声明方向）、1354（24位置/12PNG/4声明方向）、1368（24位置/12PNG/4声明方向）已有世界候选，共12项、246个原始线性位置、113份不同PNG，剩23项没有世界候选。每位置原native尺寸×4、rawOffset和源顺序保留，cardinal/方向分块、时长和loop未知。挂点合同见docs/HEAD_ATTACHMENT_CONTRACT.md，各项WORLD_ID_SOURCE_CONTRACT.md保留不同来源/切片/未通过项。42约1.30%—1.36%、54约1.65%—2.04%、44约0.42%—6.73%、236约2.98%—5.92%、1246约0.61%—7.50%、1311约0.91%—6.33%、1248约0.33%—9.06%、1296约0.97%—9.52%、1312约0.17%—4.08%、1354约1.49%—11.79%、1368约0.10%—5.45%包络比例残差；138仍有10.65%/13.63%残差。全部未验收、未接运行，完整动画、native原点/符号、当前角色头节点和实机仍未知。

## 项目关联

- 新项目：灵葫大作战（QQ堂玩法道家Q版独立复刻）；GitHub：https://github.com/luhailong-java/qqtang-daoist-remake 。本轮未提交/上传。
- image origin：https://luyuacpp.visualstudio.com/image/_git/image ；其GitHub地址待确认。
- 风格：designs/mail-ui-v1/01-mail-event.png、designs/team-ui-v2/team-ui-v2.png；具体仙灵改造参考及目标文件见adoption-index.json。
- 新项目实际目录：assets/items/head-adornments/，核实2026-10-28；不改共享Git、src或全局清单。


138天使环新增世界候选：24原始线性位置采用9份不同相位PNG，source raster+offset共18组，不能称为9帧原始动作。A母图选0/1/2/6/7/8，C实际编辑母图选12/13，B母图选14；每一位置的native尺寸、rawOffset与sourcePhaseIndex独立记录。9份图像按原尺寸×4导出，24条序列记录见world-art.json；来源与选择见docs/WORLD_138_SOURCE_CONTRACT.md和exports/138-selection.json。当前总数以上方世界表示缺口章节为准。全部未验收，时序/方向语义/挂点及实机仍未知。

44鸟巢帽新增18份新画world相位，24源位置rawOffset各自保留。3张母图实际附各6原相位与两主风格；前后/侧面和三鸟轮流跃起分别绘制。A裁切间隙一次修正后所有18当前内容bbox不碰单元边，灰底逐6查看；几何连续性/alpha全检查/时序挂点与实机仍未通过。详见docs/WORLD_44_SOURCE_CONTRACT.md。

236/1246各补24位置，分别4与6份新世界图。236横向0/6经B实际编辑改善；1246的B/C实际编辑和A安全间隙530重裁分别记录，邻图白条已移除。当前总数以上方世界表示缺口为准，详见docs/WORLD_236_SOURCE_CONTRACT.md、WORLD_1246_SOURCE_CONTRACT.md。

1311神奇树新增10份新world相位，24源位置逐项保留。B后四相位镜向叶序错误经C实际编辑纠正，7/8包络偏差15.53%/11.86%改善0.91%/6.33%。10份当前图按6+4灰底实看，全部未验收，详见docs/WORLD_1311_SOURCE_CONTRACT.md。

1248乌云新增12不同world相位、24位置。按源区分左右云卷、无电/小电/大电与云体明暗，B为实际编辑A并保留关系；未套用背包大电光到全部帧。6+6灰底查看，bbox不碰裁边，仍未验收，详见docs/WORLD_1248_SOURCE_CONTRACT.md。

1296彩虹新增12不同world相位、24源位置，保留三云和大/小云换侧。B6/8包络偏高经D实际编辑B改善0.97%/3.94%，C层级变弱未采用；7/10仍9.52%/9.10%残差。6+6当前灰底实看，全部未验收，详见docs/WORLD_1296_SOURCE_CONTRACT.md。

1312明月新增12不同world相位、24源位置，源三云数量和月牙开口分别保留。C正向/E反向为当前候选；E实际编辑D，比例残差2.10%—4.08%，仍未验收，详见docs/WORLD_1312_SOURCE_CONTRACT.md。

1354 UFO新增12不同world相位/24位置；B8/9经C/D两轮实际AI编辑，D8改善3.44%、D9仍11.79%，其内部飞碟/光束比例待验，先保留最佳候选推进其他缺件。详见docs/WORLD_1354_SOURCE_CONTRACT.md，未接运行。

1368周前十新增12world相位/24位置，正/反数字10视面区分，使用自有玉云冠而非原TOP字皮。C修反向冠体比例到0.10%—1.81%，B正向4.26%—5.45%，完整动画未验；见docs/WORLD_1368_SOURCE_CONTRACT.md。
