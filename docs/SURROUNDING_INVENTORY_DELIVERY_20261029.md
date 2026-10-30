# 灵葫大作战：62件护罩、环绕与仙驾库存候选

源catalog的`ear`类别62个唯一物品ID现均有256×256自有风格库存PNG，入口`assets/items/surroundings/art.json`，不是62套世界动画。原ID、原名和原描述逐项保留，新显示名另列；代理道童/月影、植物服、龙和机甲不增加账号角色数量。

本批12次真实内置image_gen调用，保留12张原生1536×1024母图；最终62件使用11张选定母图。Jv1的光束碰到上边且与下行过近，实际AI编辑Jv2将光环缩回独立范围后采用，editOf/实际参数/源SHA齐全。其余源参考只约束内容、视面与功能，外观承接两主风格；联名人物、车队标志与原头像没有作为成品绘制。

每批按真实alpha8间隙登记不等格裁区，预乘alpha等比缩至224内容范围、居中256画布。`docs/surroundings-*-export.json`、每件provenance、逐母图generation和prompt记录实际native/缩放/裁切，工具未披露的actualModel/actualQuality保持null。输出不是62次模型生成，也不是原生256生成。

协调者已逐批实际查看A–K的256暖米白联系图（`qa/surroundings-*-contact-256.png`），本批每件输出四边alpha8接触0；轮廓、主体和切片未发现串入邻物。该检查没有覆盖24–48px店面辨识、全部状态、头身挂点、所有角色叠放和世界运动，visualAccepted/runtimeAdopted仍false。

62项世界stand/walk只取得124份metadata-only证据、65种不同完整DIMG和1520声明帧位置；实际世界美术未制作，时间/方向/挂点与源历史版本未批准。细节见`SURROUNDING_MOTION_CONTRACT_20261028.md`，不能把metadata齐或库存齐写成整款游戏美术完成。

`verify-inventory-candidates.py --metadata-only`已核对62ID精确覆盖、源文案、输出/母图/生成记录SHA、真实PNG头和裁区范围，errors0，未导入Pillow/解像素。完整PNG规格检查配置为远端Actions步骤：核验256尺寸、真实透明、至少16px可见留边及源裁区不切轮廓。只有实际Actions成功才记通过，工作流存在不代表结果。

本机重型测试/构建/浏览器暂停继续。当前整款游戏仍缺角色完整动作、穿戴世界资源、其他物品与UI状态和最终验收；本批按候选开发状态保存。
