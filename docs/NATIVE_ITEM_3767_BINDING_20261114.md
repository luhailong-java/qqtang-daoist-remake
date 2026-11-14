# 3767 原生库存路径复查

结论：3767 仍没有可确证、现存且唯一的原生库存 IMG 可替换。584 个自有候选中，583 件已有原生库存安装，3767 继续待证；其余2,361个源物品缺自有画稿的状态不变。

固定源 `item-resource-index.json` 将3767记为 `eye/12`（08纪念·篮球），`source_zip=eye/eye12.zip`，仅声明 `object/eye/eye123.img`、`eye125_stand.img`、`eye125_walk.img`，没有 `res/uiRes/icon` 文件。

发现明确的外层配置别名：`configs/item-image-aliases.json` 将3767指向 `object/eye/eye123.img`，同时在依据中明说 **eye12.zip has no shop icon**。其目标是外观层：DIMG65537、声明58×55、实际帧38×15、偏移(11,21)。该别名不能充当原生库存 IMG 绑定。在固定源13个可读程序源码中未找到该别名文件的消费者，原生 UI PYC 也未发现其文件名常量；这只是已检查范围内的静态结果。

原生 `uiMain.pyc` 的 `UpdateMyPropC2CDealDlg` 在字节偏移435–504，直接从 `itemList[info.m_nItemID]` 的0/1字段取得类别、资源号，拼接 `res/uires/icon/%s/%s%d.img` 并调用 `Win_SetImg`。源 `itemCFG.py:1818` 与 `commodityCFG.py:2420` 都把3767声明为 `eye/12`，因此该源配置对应的请求路径是 `res/uires/icon/eye/eye12.img`，不是按物品ID猜文件名。固定ZIP松散目录及固定 `object.idx` 均无此路径。

另有版本限制：两个可读源PY声明848，而其旁边旧PYC静态 `version` 为163，完整惰性常量树均未出现3767。实际运行采用哪个配置尚未验证，因此这里不宣称已验证3767的运行绑定。即使采用848源配置，目标库存图文件也仍缺失。

没有创建图片、缺失路径或客户端文件，没有修改bundle，也没有运行原客户端或操作Git。后续若补齐3767，需另行证明或明确实现原生缺失路径，而不是把外观层别名当成已经恢复的库存图标。[机器证据](native-item-3767-binding-20261114.json) 保留各固定源成员哈希、原生指令窗口、配置行及路径查找结果。
