# 原生商城其余图像候选

本批完整覆盖固定源 `object/ui/shop` 的 **132件减去已有20个商城控件，剩余112个图像路径、168个原始帧位**。范围包含角色横条/角色名、广告、购买/赠送/修复与验证面板、砸蛋、幸运转盘、货品框、折扣数字和角标等。绘制器为 `scripts/native-ui-shopextra-art.py`，全部kind使用 `shopextra-`；未重复已有20件，也不把物品库存或整个游戏的美术分母算入本组。

使用现有自有深玉、米金UI、图标、锤子和角色画稿，没有新增收费生图。`manifest.json` 保留逐源完整DIMG元数据、源帧PNG、原包/索引SHA及排除清单；`candidate-manifest.json` 保留112个原生patch、168个原生编码后解码PNG、自有素材/字体/角色合同哈希与逐帧Alpha政策。原声明画布、实际帧尺寸、裁片、偏移、像素模式、帧位顺序、头部及全部非像素字节保持源值，变化仅限每帧原像素平面。

Alpha政策按帧位统计，不能标成全部不变：

- **98个结构Alpha帧位精确保留源平面**，包括面板、输入框、单选控件、角色横条、灯位和框光等结构。
- **70个装饰/字形帧位在原完整帧矩形内重绘Alpha**，用于数字、文字、角色名、类别图标、角标、旧熊头外形、标题/插画等，避免保留原字形或旧角色轮廓。每帧记录重绘ROI、具体理由、差异包络和像素数量。

所有重绘仍受原生帧尺寸和原容器像素范围约束，不移动原生控件或更改回调。砸蛋标题8个位置与灯光7个位置分别保留，不能统一推断所有多帧资源的常态/禁用/高亮下标，也没有编造原时长或循环。

18个角色横条和18个角色名依据共享 [角色映射合同](../room-extra-reference/roster-mapping-audit.json)。固定PYC的 `charIconList[i-1]`、`shopPlayer_getRoleIdx()` 与 `info.roleID` 给出原生路径/角色号，再连接已确认的自有portrait/master及其来源哈希；不凭文件简称猜身份，不复用一个角色冒充缺失角色。原列表10/11/12/17为空槽，本组没有为它们补造路径。角色横条只裁自有256×256 portrait的 **(0,72,256,216)** 区域，预乘Alpha缩至 **73×41** 并放在 **(42,-2)**，在原116×35横条内自然裁切；不改变源原生几何，也不是世界挂点验收。

动态字色与布局来自 [静态机器证据](dynamic-layout-evidence.json) 和 [重点说明](STATIC_BINDING_NOTES.md)，区分直接RGBA、命名颜色加载、父节点BUILD_CLASS继承与unknown。不能把所有面板统一铺成深色或浅色：购买的白色名称、浅米色正文/价格使用深底，而明确蓝色的补差提示使用浅底；赠送的灰色价格使用浅底，白色收件号、黄色物品名和浅米色留言使用深底；修复正文/数值及砸蛋黄字/白色锤数量使用深底。TLabel/TEdit默认黑与TEditID/Password白字分别处理，未声明的TButton引擎字色仍待运行确认。已有PYC运行文案不会因图片重绘而自动替换，不能在其文字矩形上烘焙另一套字幕。

[页头币种证据](header-currency-evidence.json) 同时保留原图观察与PYC绑定。原页头上方实际写“酷比宝石”，本项目对应 **灵玉**；下方“QQ糖币”对应 **灵币**。上方技术变量名 `QQTTicket` 不能推翻原图的显示语义。原有 **Q币支付/充值类别保留**，因为本批没有修改其支付值、URL或回调；不引入“仙券”币种，也不将另一种余额冒充该类别。

4件没有精确路径或动态模板证据：`equiped.img`、`img_itemTag.img`、`tab_char.img`、`tab_itemChar.img`。它们仍按真实源路径/帧结构导出候选，活动用途保持unknown。其余路径的字面出现或模板候选也不等于页面实际激活、交互或时序已经验证。

从仓库根目录复现并只读检查：

```powershell
python -B assets/native-client-ui/shop-extra-reference/capture-source.py --check
python -B assets/native-client-ui/shop-extra-reference/export-shopextra.py --check
python -B assets/native-client-ui/shop-extra-reference/verify-shopextra.py --check
```

检查应覆盖112路径/168帧位、98结构Alpha平面、70装饰重绘政策、原生编解码回放、全部非像素字节、角色合同/字体/来源哈希及币种语义。全状态图只是浅/深底离线诊断，不是原客户端截图或用户视觉审核。

本批仅交付独立候选，没有修改主构建器、bundle、实际客户端或Git，也没有执行原程序或GUI。`sourceTimingVerified`、`nativeRuntimeVerified`、`visualAccepted`、`installedToClient`、`allShopUiOrRuntimeTextComplete` 均保持false；原时长、活动分支、动态字宽和用户最终画面仍待验证。整款游戏全部美术完成不能由本组路径覆盖推出。
