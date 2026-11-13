# 道童东向步行六相位

2026-11-12。按已核对的 sourceRole9 东向六相位顺序绘制道童。原创棕色短发、金发带、玉绿长衫及左手金葫芦沿用现有道童身份。源板仅用于东向视角和动作结构。原始板按 100×100 声明画布保留六个分层资源的偏移，叠放顺序为先前静态诊断用法，head1 层未读取。实际原生根点、帧时长、循环方式和其他方向顺序仍缺证据。 [源相位取证](../assets/characters/motion-generated/daoist-child/native-role9-evidence/NATIVE_E_GAIT_REVIEW_20261028.md)

内置 image_gen 返回两张 2172×724 RGBA 母图，按 724 像素三格划分 f0–f2 和 f3–f5。第三次调用以 f4 的原像素裁格为输入，尝试修正 f5 脚跟抬升与前脚落位。单张重绘的画面比例有变化，保留为补充审阅稿。三次调用的实际提示词、引用、输出路径与哈希均已登记，工具没有披露实际模型和质量。 [相位与来源清单](../assets/characters/motion-continuation-20261112/daoist-child-east/manifest.json)

六个相位均已切出 256×256 RGBA 样本。共用 0.3184 等比缩放和地面基准，以手工估计的髋部横坐标排版。Alpha≥8 的裁格和导出边界没有可见像素，六张样本文件各异。脚底基准仅供对比，实际原生锚点继续留空。 [浅深底 112/64 像素预览](../assets/characters/motion-continuation-20261112/daoist-child-east/review-light-dark.png)

f1、f2 的近脚在屏右，f4 的前景脚落到屏左，空手随之从后摆切换到前摆。f3 加入闭眼，区别于 f0 的开眼通过姿态。f5 已出现屏左抬跟与屏右落脚，但长衫遮住近远腿的连接，完整步态连续性待人工确认。项目现有动作入口未启用这组样本，验收状态仍为待审。 [下身放大对比](../assets/characters/motion-continuation-20261112/daoist-child-east/lower-body-diagnostic.png)

重放裁格和来源校验可运行 `python -B assets/characters/motion-continuation-20261112/daoist-child-east/export-diagnostics.py`。
