# 从用户提供目录启动的原生 UI 替换

更新2026-11-14。实际 `QQTang-Local/QQTang-Local/runtime/client-patched` 已安装 **837个UI图像资源／1,590个非空位置**，并保留原始空位1个。安装后的文件和原生解码像素均已回读。原生全部UI和整款美术仍未完成。 [实际回执](native-client-installation-20261114.json) · [完整进度](ART_DELIVERY_20261114.md)

| 本轮新增范围 | 资源／非空位置 |
|---|---:|
| 房间剩余面板、角色插画／头像与模式说明 | 115／159 |
| 商城剩余角色条、名字、购买／赠送／验证、砸蛋／转盘等 | 112／168 |
| 社交、家族、资料与道侣仪式 | 94／175 |
| 家族徽章、等级、模式图标、普通／点击／fight光标 | 141／188 |
| 13张推广图与2张默认资料GIF | 15／15 |
| 聊天气泡、菜单、数字、录像、网络等松散控件 | 47／131（另1空位） |
| 新增合计 | 524／836 |

此前313／754覆盖登录、选区、大厅、通用控件、房间／商城操作、设置、对局／结算／录像、导航、聊天、交易、背包／任务、锻造、宠物及网页外框。当前包内772个UI图像路径全部覆盖，另65个松散UI路径已装；页面数、动态文字和运行交互另行验收。

画法沿用本项目玉绿、青绿、象牙米白、暖金云纹和原创大头短身人物。37个UI身份包含20个有角色映射证据的自有身份与17个独立额外头像槽；后17个没有虚构世界实体绑定。18个商城角色横条与角色名共用房间映射合同，原逻辑别名与回调不变。

各原生画布、位置数、空位、裁片、偏移与像素格式保留。Alpha按组区分功能结构与旧字形／人物轮廓，不宣称全部原样；源蓝字／白字／浅米字分别安排浅纸或深玉底。TGA保留头尾与方向，GIF保留500ms、loop0、disposal1及原C4兼容位。原时序、鼠标热点、佩戴挂点和实际叠放继续待验。 [格式说明](NATIVE_UI_FORMATS_20261114.md)

全部图片统一包共1,482资源／2,548非空位置，包含583库存、10头饰世界资源、52地图。824个包内条目更新，原包完整前缀与另外2,658条索引保留；658个松散图像另装。Client.exe未改。包内资源不能通过单独旧批覆盖，安装器按已核验回执恢复源后整体升级。 [统一包](../assets/native-client-bundle/review-v1/README.md)

```powershell
python scripts/build-native-login-art.py --check
python scripts/build-native-art-bundle.py --check
python scripts/install-native-ui.py --client-root "$env:USERPROFILE\Downloads\ABDM\Compressed\QQTang-Local\QQTang-Local\runtime\client-patched"
```

图片统一恢复使用同一安装器的 `--restore`，备份位于项目忽略目录、客户端专属子目录。五份UI文字数据及链接颜色单独备份，完整撤回这两层数据必须先 `native-ui-brand-data.py --restore`，再 `native-ui-color-data.py --restore`。uiMain的132ffe组合版本保留，9个展示常量、2,257个代码段和全部网址的证明未被本轮图片升级改变。

非库存UI图像分母1005个路径，还剩168个聊天表情；库存图像另有2622个路径未覆盖。启动器、系统标题、远端页面、字库、服务端文案不在本路径验收内。原客户端未执行、未用GUI自动代审，运行与用户视觉验收仍false。 [逐组差额](NATIVE_UI_REMAINING_20261114.md) · [592位表情计划](NATIVE_EMOTION_PLAN_20261114.md) · [启动持久性静态证据](NATIVE_LAUNCHER_UI_PERSISTENCE_20261114.md)
