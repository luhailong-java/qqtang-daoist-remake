# sourceRole9原生E步态：有界静态取证

本项目独立外观映射`roster-skin-mapping-20261028.json`明确sourceRole9→daoist-child道童；该映射是本项目选择，不代表原腾讯人物名字。固定社区v1.3.4 ZIP SHA沿既有证据为fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7，本轮未在机器冻结时重哈希整个包，也未执行客户端/包内代码。

## 精确资源链和方向

实际重新读取ZIP中`QQTang-Local/runtime/client-patched/object/player/player9.ini`285字节，SHA `54e609aec636603ad02e9449dff0baf011ad3c614659796c8446549f895e5c44`，与既有映射证据一致。walk赋值hair/face/cloth/leg=10901，head/body/foot=1。选6个明确对象：`object/{hair,face,cloth,leg}/{同类}10901_walk.img`以及`object/body/body1_walk.img`、`object/foot/foot1_walk.img`。没有读第7个head1。`native-walk-headers.json`保存每项pkg offset/压缩长度/压缩SHA/40字节头；6项均真实4方向、共24帧、每向6帧，100×100声明画布，不是此前假定的4帧。

先只取leg的f0/f6/f12三个极小探针，总196像素。黑鞋形状最初不足以定E；随后实际看face12鼻/嘴朝屏左，group2是W代表，纠正了鞋尖判断。另看face0鼻/嘴朝屏右，才确认group0是真E。没有按目录/方向序号猜N/E/S/W；其他组的完整语义顺序仍未验证。相关实际探针为`group2-direction-probe-5x.png`与`group0-face-direction-probe-5x.png`，raw layer仍保留原尺寸/offset。

E动作板是`group0-six-phase-board-5x.png`，实际3×2按f0/f1/f2/f3/f4/f5顺序，所有脸/鼻均朝右。每相位在原100画布上按各层原始frameOffset放置，不独立bbox-fit或变更根点；5倍nearest仅供看像素，不是原生高清。`group0-six-phase-board.json`保存全部原始索引/相位范围、分层尺寸/offset/像素SHA、容器和pkg来源。采用的诊断叠层顺序body→foot→leg→cloth→face→hair为明确的可读性处理；head1未读，未独立证明原客户端的完整绘制顺序，不把这张诊断图说成客户端原渲染。

## 四相位接触差异与不能证明处

先查看了f1/f2/f4/f5的四姿态完整板与固定原区域[34,60,66,84]的12倍下身inset（`group0-e-lowerbody-12x.png`）。下表脚部bbox均为alpha≥8在原100画布中的LTRB，来自四张已解码小leg PNG；只是屏幕左/右可见组件，不直接等于持续的解剖近/远身份。

|原帧/相位|leg尺寸与offset|屏左组件bbox|屏右组件bbox|可见变化|
|---|---|---|---|---|
|f1/1|21×6；(40,75)|(40,75,48,79)|(53,75,61,81)|屏右鞋下沿更低，近侧可见手臂向后|
|f2/2|21×9；(39,72)|(39,72,46,78)|(52,76,60,81)|屏左鞋抬起，屏右保持低位|
|f4/4|21×9；(40,72)|(40,76,48,81)|(54,72,61,78)|屏左鞋落低，屏右抬起；可见手臂已向前|
|f5/5|22×7；(39,73)|(39,73,46,80)|(53,75,61,80)|两腿通过接近相同下沿、脚形不同|

这证明源E有清楚的脚部抬落/前后摆与手臂半周期变化，排除了我们失败稿的两个同姿态源输入。但腿只有6–9像素高，髋/膝被短裤挡住；仅凭排序x或臂摆相反，不能把同一条近RIGHT/远LEFT的骨链独立追踪为已验证。`group0-e-lowerbody-review.json`明确`anatomicalNearFarChainProven=false`。source reference仅用于相位/相机功能，本项目新图仍须自己证实近RIGHT脚相对髋在两接触时异号，不能照搬遮挡当作通过。

## 0/3不能整帧别名

根要求补0/3后，仅解码这两处同6层的12个小图，共5828像素；复用之前已读的1/2/4/5，不全24帧解码。逐层比较encodedPixelSHA、尺寸、offset、pixel mode：body/foot/leg/cloth/hair的0与3均相同，face的SHA不同（表情/眼睑不同）。所以整组`allVisibleLayers0And3Identical=false`、`aliasApproved=false`，不以腿层重复推导整帧重复。比较原值均在six-phase JSON中。

本次整个取证过程6明确容器、46个很小的分层解码调用（包括方向探针和重复必要读），累计22653像素；实际E完整板为6个姿态位置，每位置6原始分层，另有方向探针。只展开/解析这6个选中容器元数据，未解码全144层帧或其他角色。容器版本65536和声明范围均严格完整匹配；原始player.py动作[4,300]的300仍未解释单位，时序保持null。

## 一次新输入AI稿的结果

根允许只用自有runtime master+本张真实六相位板+两主风格再做一次。实际生成`../east-native-reference-contact-pair-v1.png`两个相反接触关键姿态；原生2048×768，但仍画成近景腿前/远腿后两格，空右臂也都向后。具体未通过记录见旁review.md/generation.json，未切帧/启用、不继续同点堆稿。原QQ红发/白红运动服/黑鞋外观完全没有采用为本项目身份。

全部为静态读取/必要小图/远端内置生图与新图单件检查；机器heavy时段未交还，不运行客户端、浏览器、测试、全量QA、src或Git。
