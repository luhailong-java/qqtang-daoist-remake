# 本批生成入口核对

生图前实际重读image的AGENTS、config/image-generation.json和IMAGE_MODEL_POLICY。2026-10-29再次打开[官方Sunburst型号页](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)，页面仍将其列为当前最高能力图像生成/编辑型号，支持档位包含max；本批沿用现配置目标，不改共享配置。

仅内置image_gen。其schema没有model/quality或精确size选择器；目标及提示词不能当实际调用锁定。逐图actualModel/actualQuality继续null，实际原生尺寸以返回PNG为准。没有API、video、付费路线或凭据变更。
