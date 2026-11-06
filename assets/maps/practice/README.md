# 练习场景美术复用候选

2026-10-28。22个源定义均有当前自有候选，**新增模型生成0次**。它们与water源元素的可见画面本来相同：逐JSON核对visibleGroupId、原帧尺寸、referencePng哈希相等后，直接指向本项目新画的water PNG。关联证据在source-alias-relationships.json；不凭目录名、数字相近或画面相似猜测复用。

每个150xx练习元素仍保留自己的占地、GridAttr、元素偏移、原帧偏移和独立records/150xx.source.json。像素文件复用不等于逻辑定义合并；art.json显式provenanceRecord指向本元素记录，生成来源继续追溯water的逐图记录。无额外裁切、缩放、镜像或重新生图。

22项均为候选，accepted／geometryAccepted／seamlessVerified／inGameAccepted仍为false，承接water本身可见比例与木板数量等未通过项。当前本机重型作业时段被另一任务占用，尚未重新执行全族图像解码与哈希QA，也没有实机验收，不能以复用数量宣布练习场已完成。
