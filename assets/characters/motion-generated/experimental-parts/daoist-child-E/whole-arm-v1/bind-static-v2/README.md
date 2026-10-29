# 《灵葫大作战》道童E：最终一次肩部遮挡/艺术绑定修正

2026-10-28 America/New_York（UTC记录跨29日）。仅一次真实A/B静态渲染，0AI图。本批替换v1矩形肩遮挡，远臂作指定的一次绑定微移，未修改任何母图、躯干源PNG或臂源alpha。当前保留v2为较佳静态候选；不继续此接头的第三次返修。

## 先实看，再手工划定同源肩圈

实际看原生torso及`torso-shoulder-inspection-4x.png`，确认其绿金肩孔内部已有成品白袖stub。v1矩形前景pass把这块白袖和下方衣料重新盖到新整臂上，在约y393形成直切。

`shoulder-ring-ownership.json`手工定义原生310×314 torso中的outer polygon减inner hole，仅保留原绿金环：源ROI[22,35,130,174]，导出`torso-shoulder-ring-native.png`为108×139原生裁片、alpha≥8为3273像素。内孔排除旧白袖；外环下缘不纳入原下垂衣料。没有自动颜色抠图、阈值选色、羽化或重画。选中像素的原RGB/alpha不变，未选像素只在新增所有权裁片中置alpha0，原torso/臂文件完全不改。原始ROI/多边形/排除理由、控制点与哈希在`.source.json`，并已实际查看`torso-shoulder-ring-ivory-4x.png`确认绿金环中未夹旧白内芯。4x图是nearest工程查看，不是新增高清细节或正式游戏图。

## 本次固定变换

两条臂共用0.18比例，近RIGHT空拳肩点[262.5,359.5]不变。farLEFT整臂连葫芦一次从[340,355]移到[334,360]，纯艺术attachment delta[-6,+5]，A/B一致。v3头/torso/腿每个矩阵逐项保持不变；未动髋、脚、caller/root或native frameOffset。两姿仍用同一臂绑定，不是手脚交替动画。

顺序仍为far臂5、远腿10、近腿20、头35、torso40、near臂70。新near臂先在前层覆盖底层旧白stub，再由绿金肩圈前景80盖住新臂边缘。肩圈使用同一torso原矩阵[0.48,0,0,0.48,225.18,310.76]，加原ROI起点后其裁片矩阵为[0.48,0,0,0.48,235.74,327.56]；不重新对齐或缩放该环。v1矩形pass已完全移除。

所有原生臂裁区/手工肩肘腕指点沿用v1来源；其旧位置/旧矩阵和此次新矩阵逐件保存在`proposal.json`及各627图旁`.source.json`。该信息不声称是恢复的原QQ精确骨骼。没有旧分段臂、单手葫芦或额外hem。

## 实看结论与具体边界

已实际查看`two-contacts-627-ivory.png`（两个原627未缩放）及`two-contacts-96-ivory.png`（两个原96格加20px标签区）。**v2比v1有明确改善**：near的y393矩形直切消失，连续白袖能从原绿金肩圈自然接出，未再把旧白stub作为前景补丁恢复。Far移入后白cap露出量减小，胸前肩缘仍有少量白袖体积，但本次未见断裂。手/葫芦比例与身份保持。

这只支持保留v2为较佳静态候选，尚未得到协调者完整静态采用批准。Far覆盖量没有像素级认证；先前裤裆小金尖仍未归因。持葫芦手按来源/逻辑链固定LEFT，但拇指遮挡，未独立证明解剖左右手。两姿同臂而腿交换不能当walk通过。

96文件为整个627方画布按96/627等比PMA LANCZOS缩放，人物可见高度约68px，不是96高人物。它能看身份和持物，接缝细节不能靠该小图判定。暗底动态/慢放、运行、真实动作时长与完整动画均未验收。

## 交接

- `proposal.json`：所有源SHA、旧/新节点矩阵、far位移与ring-only遮挡合同。
- `visual-review.json`：实际看图证据、v2优先原因和未通过边界。
- `contact-A-rgba.png` / `contact-B-rgba.png`：当前627方透明确定性装配；各有`.source.json`。
- `contact-A-96.png` / `contact-B-96.png`和两米白联系表：来源记录齐全。
- `render-once.py`检测已有contact PNG后拒绝重渲染；本批只执行一次。

状态`preferred_static_candidate_near_shoulder_transition_improved`，`runtimeAdopted=false`，`completeAnimation=false`。本机hold保持，未运行测试/构建/浏览器/全库QA，未改src/Git/正式rig。

## 后续静态候选数据交付

协调者随后仅授权数据导出，已依据真实`src/cutout-rig.js`schema写出`rig-contact-A.candidate.json`与`rig-contact-B.candidate.json`，各7节点、同源肩圈普通前景PNG、仅空tracks静态action。每节点保存已渲染`expectedStaticImageMatrix`；9个部件文件只核存在和编码SHA，0图像解码/模块调用/测试/渲染。手工参考根沿既有候选证据，worldRoot/nativeTiming仍null，所有运行/静态/全动画批准仍false。详见`RIG_CANDIDATE_DATA_DELIVERY_20261028.md`与`rig-candidates.delivery.json`；没有建立默认正式`rig.json`。
