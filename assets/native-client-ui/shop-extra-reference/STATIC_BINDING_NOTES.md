# 商城其余112件静态证据

[dynamic-layout-evidence.json](dynamic-layout-evidence.json) 覆盖 `object/ui/shop` 的132件减去既有20控件，实际112路径、168个源帧位。5个固定源PYC完整惰性解析共2,277个代码scope，保留331个相关scope与234个有布局/文字属性的字色证据。没有执行/导入原客户端、构造CodeType、使用GUI、读取用户目录或操作Git。

56件有精确字面路径，56件被动态模板候选集合覆盖，两组有重叠；完全无这两类证据的4件是 `equiped.img`、`img_itemTag.img`、`tab_char.img`、`tab_itemChar.img`。路径出现本身不证明实际页面处于活动状态。

`charIcon` 实际18件。`uiShop` 顶层 `charIconList` 的STORE_NAME偏移2021明确列出22个槽，`getCharIconName` 使用 `shopPlayer_getRoleIdx()` 返回的i和 `charIconList[i-1]` 拼路径。实际对应roleIdx为1–9、13–16、18–22；10/11/12/17为空字符串，没有本批路径。JSON保留完整列表及指令窗口，不从缩写猜角色。`rolename%d.img` 明确由 `ui_updateMyItems` 的 `info.roleID` 格式化，但角色身份和自有master仍须另接已确认角色合同。

`wareAttr/0.img` 至 `9.img` 是 `ui_updateWares` 用 `rebateH`/`rebateL` 配合 `%d.img` 的独立数字图，不是猜测排列的数字条。`point`、`zhe`和折扣背景有明确关联指令；其余角标的 `%s.img` 依赖运行时 `attrMap`，未猜字典值。所有数字、角色名、广告和标题都应检查Alpha是否含旧字形；旧字形Alpha不能自动当作功能遮罩照搬。本审计不做图像验收或原帧时长推断。

字色必须逐区域处理：

- 购买：name白色，txt及price1/2/3浅米色 `zoneChooseColor`，需要深底；QB/QD补差提示明确蓝色，需要浅底。
- 赠送：price灰51需要浅底；receiveUin显式白色（虽基类为TEditID）、wareName显式黄色、留言MULTIEDIT浅米色，需要深底；补差提示蓝色需要浅底。
- 修复：title/text/time/price均使用浅米色 `zoneChooseColor`，需要深底。
- 砸蛋：description明确黄(255,255,0)，锤数量明确白色，需要深底。
- 模板共34个scope全部保留。TLabel/TEdit、TEditNum/TEditPoint等默认黑色；TEditID/TEditPassword明确白色。具体控件覆盖与已证实的同级父类继承优先，不能统一按“EDIT默认黑”处理。TButton未声明的引擎字色保持unknown。

命名颜色的uiMain字面量定义被记录，但共享模块命名空间运行解析仍未执行。JSON区分直接RGBA、命名加载、带BUILD_CLASS窗口的继承和unknown。原PYC里的Q币/Q点支付提示等运行文案仍是独立数据，图片替换不能冒充它们已改，也不能在其文字矩形上烘焙另一套字幕。

本证据只负责固定源结构，不做角色身份猜测、原生安装、动画时序或视觉通过声明。
