# 糖泡与火焰源结构核对

只静态读取已固定SHA的社区样本，不执行客户端。原版未修改身份和播放时序仍未核实。`references/qqtang-packed-art/`是独立DIMG解码的结构参考，不能当本项目运行成品。

`bomb1_stand`为4帧，0和2原始编码像素SHA相同，宽高/offset亦相同；新画候选因此让2显式复用0。1是纵向胀大，3是横向压扁，逐帧保留原尺寸和offset。`bomb4_stand`也是4帧，但0和2的编码像素不同，所以四帧独立，不用重复图替代。两组导出见`assets/effects/bubbles/manifest.json`，7张新画派生PNG对应8个源帧条目，尚未运行采用或循环验收。

`flame1_stand`共7帧：0/2相同、1/3相同，4/5/6为原始空帧。`flame2_stand`和`flame3_stand`也各7帧，但全部可见，只有0/2相同，3至6是不同的衰减形态。不能把flame1的空帧结论套到其他资源。首张材质母图`flame-pairs-a-v1.png`提示词末段对此曾做了错误泛化；实际提示词保留，生产合同已纠正，A仅提供flame1两相及flame2前两相，后续独立新材质补齐后者的其余相位。没有将未生成的相位标为完成。

`assets/effects/flames/manifest.json`按真实encoded-pixel SHA、原尺寸和offset识别重复，只明确相同者复用；空帧用`empty:true,file:null`保留，不补特效。新AI材质只提供RGB，最终透明轮廓取对应源alpha并放大4倍，目标帧尺寸仍为原帧4倍。操作是新材质裁切/缩放/原alpha合成，不是每帧独立新生图，也不称原生高清轮廓。接缝、混合、运行锚点和时序均未通过。

另静态解析的六个`.eff`效果文字见`references/qqtang-effect-data/`；Python只用有界`ast.literal_eval`读取元组/列表。`magic13`等资源名与`magic0013.img`的数字名对应仅为待验证候选，不冒称已证明客户端解析方式。“普通糖浆”效果文件中含药剂图标，不能仅凭文件名把它当十字爆破渲染。
