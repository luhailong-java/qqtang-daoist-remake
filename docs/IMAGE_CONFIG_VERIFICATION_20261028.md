# 本轮图像入口核对

2026-10-28，America/New_York。读取当前image根规则、统一配置和执行策略，官方型号页仍标明GPT Image 2.5 Sunburst为最强图像生成／编辑型号，质量档包含low、medium、high、xhigh、max和auto；本轮保持配置目标sunburst／max，不改写旧图记录。

依据：https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst ，https://openai.com/index/introducing-chatgpt-images-2-5/ 。本轮核对由项目协调者统一完成，制作工不重复改共享配置。

实际使用内置image_gen。入口只开放prompt、参考图和透明背景参数，没有model／quality选择器，不能据公告或配置认定某张输出已锁定API分支；逐图actualModel／actualQuality仍为null并明确未确认。没有调用新增付费API／CLI，没有改凭据或预算。
