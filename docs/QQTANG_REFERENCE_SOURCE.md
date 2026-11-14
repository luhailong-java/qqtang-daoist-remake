# 《灵葫大作战》参照的《QQ堂》与客户端来源

更新：2026-11-14，America/New_York。

## 参照对象

本项目参照的是腾讯PC端游**《QQ堂》（QQTang）**。本次对话中的“QQ弹客户端”按已有项目上下文指《QQ堂》；不将《弹弹堂》《泡泡堂》、QQ游戏大厅中的《火拼QQ堂》或其他泡泡游戏混作同一版本。

参照内容是原版玩法、操作、流程、地图行列/格子/分层、建筑占地、道路、障碍、出生点及碰撞。UI、角色和场景表面美术继续使用本项目原创道家Q版画风。固定边界见[用户需求锁定](USER_REQUIREMENTS_LOCK_20261026.md)。

**目标腾讯历史版本尚未锁定。** 不能仅按下载页标题、文件名、社区兼容版本或当前能启动的怀旧包，宣称已经取得腾讯未修改原件。

## 当前实际使用的固定参照源

| 项目 | 实际来源与状态 |
|---|---|
| 已取得研究输入 | [kuuhaku1314/qqtang 社区v1.3.4发行包](https://github.com/kuuhaku1314/qqtang/releases/tag/v1.3.4)，是修改后客户端/恢复项目发行物，不是已认证的腾讯原始安装包 |
| 固定下载URL | [QQTang-Local.zip](https://github.com/kuuhaku1314/qqtang/releases/download/v1.3.4/QQTang-Local.zip) |
| 字节数 / SHA-256 | 288,298,460 / `fd9d80320605bebbe6c5d42fa182dfbe74486405fa3718093513b10969fabec7` |
| 本机保存 | `.artifacts/reference-inputs/QQTang-Local-v1.3.4.zip`，以及同目录静态抽取的`object.pkg`、`object.idx`与数据；由Git忽略，不随自有游戏公开上传 |
| 格式研究基线 | 社区提交[`4b3a245fd985cabd4abd68ade6c282cc163d9edb`](https://github.com/kuuhaku1314/qqtang/commit/4b3a245fd985cabd4abd68ade6c282cc163d9edb) |
| 实际可复查数据 | 已恢复386件白名单数据，其中377地图；地图三层/尺寸/原字节SHA与既有参考一致。原始来源、SHA和偏移保留，未把第三方原贴图用作本项目运行美术 |
| 版本线索 | `5.2.1.201`来自社区补丁的原客户端兼容说明，只是线索，尚不是用户锁定的腾讯目标版本 |
| 运行边界 | 未运行原包中的EXE/DLL/Python；未用Computer Use/CUA/sky或替代GUI验证原游戏 |

[固定参考恢复方式与逐文件哈希](../references/qqtang-map-data/README.md)、[本轮源复核](SOURCE_REVALIDATION_20261111.md)、[地图几何证据与缺口](QQTANG_MAP_DIMENSION_EVIDENCE.md)。社区原作者也在[开发说明](https://github.com/kuuhaku1314/qqtang/blob/main/README-DEV.md)明确区分原始客户端与其恢复工程；其发行包不能替代原件身份核验。

## 用户提供的本机客户端目录：已静态核验

2026-11-12，用户提供下载后的`QQTang-Local/QQTang-Local`目录。本机位置可写作`%USERPROFILE%\Downloads\ABDM\Compressed\QQTang-Local\QQTang-Local`；精确绝对路径仅存本项目忽略的本机核查回执；此次安装前核查未改动输入。11 月 14 日起按用户要求安装自有原生美术，当前改动见文末安装记录。

**结论：这是社区QQTang-Local包；本轮核查的静态部分与已固定v1.3.4发行ZIP逐字节相同，不能将它改称腾讯未修改原始客户端。** 因此可以继续用它核对已有静态资源和社区样本；它没有补足腾讯原版身份、原始动作时长或头部挂点的证据缺口。

- 比较范围：根README/发行清单/启动器、`runtime/client-patched`顶层EXE/DLL，以及`map`、`object`、`data`、`res`静态资源目录。
- 9,209件文件、717,485,649字节全部SHA-256相同；其中377张`.map`一致。在这组限定目录内没有缺失、额外或不同文件。这不是整个运行目录/服务端/存档全部相同的声明。
- README明确自称“QQ堂怀旧版”、指向`kuuhaku1314/qqtang`，说明重建Client.exe和移除TP。README及发行清单无显式semver tag；v1.3.4对应关系来自固定ZIP的字节比较，`schema_version=1`不是游戏版本号。
- `release-manifest.json`为1,850,860字节，SHA-256 `bccfa25e8799f2cc0f0e9b31806a288b4400b71534b5330d32153b61718e6b32`，包名`QQTang-Local`，生成时间`2026-10-22T22:27:32.598074+00:00`。

PE资源版本和本机Windows Authenticode静态检查：

| 文件 | 文件版本资源 | 检查返回 | 限定解释 |
|---|---|---|---|
| `QQTang-Launcher.exe` | `0.0.0.0` | `NotSigned` | 社区启动器，不是腾讯原始安装包证据 |
| `runtime/client-patched/Client.exe` | `5, 2, 1, 201` | `NotSigned` | 当前修改后主程序保留5.2.1.201版本资源；版本字符串不证明未修改 |
| `Core.dll` | `5, 2, 1, 201` | `HashMismatch` | 能读到Tencent证书信息，但当前文件未通过签名哈希检查 |
| `QQTDir.dll`、`QQTModules.dll`、`QQTSection.dll` | `0, 10, 1, 1` | `HashMismatch` | 同样不能将保留的签名证书当有效原件认证 |
| `TerSafe.dll` | 无版本资源 | `NotSigned` | 2,048字节，与社区兼容层描述对应 |

主程序为13,860,864字节，SHA-256 `670af4f24b3db6bac030a61d628cedc8e4522468f4ef4cb88a2239ad6b946f74`。这组返回值只说明实际读取到的版本/签名状态，不据此推断恶意软件或声称它已通过腾讯认证。

公开摘要和七个二进制的大小/完整SHA/版本/签名返回见[用户目录静态检查回执](reference-evidence-20261112/user-client-static-check.json)。逐9,209文件比较表和原始本机路径在忽略目录`.artifacts/local-client-inspection-20261112/`。未读取账号数据库、存档、日志、抓包、run-state或网络配置内容，未启动客户端、安装器、DLL、脚本或GUI。

## 原始客户端现在能否下载

用户刚提供的本机目录已核验为上述社区样本。本轮另查到了历史官网、玩家原版备份及下载站条目；**截至本次记录，尚未取得并核验一份完整、未修改的腾讯原始客户端。** “页面存在”“写着官方版”“有下载器”与“完整原始包可下载且身份已核实”分别记录。

| 入口 | 本轮实际核查 | 作为参照的边界 |
|---|---|---|
| [腾讯历史下载页](http://qqtang.qq.com/web2008/page/download.htm) | 本机网络解析`qqtang.qq.com`失败，web读取也未成功；不能据此断言所有网络永久不可用 | 历史官网入口，当前未从这里取得安装包 |
| [历史官网存档索引](https://web.archive.org/cdx/search/cdx?url=qqtang.qq.com/web2008/page/download.htm&output=json&filter=statuscode:200&from=2020&to=2023&collapse=timestamp:6&fl=timestamp,original&limit=-6) | 索引可读，包含2021-12-18、2020-07-16的页面记录；本轮回放页面返回429，未读得内部CDN直链 | 只证明有历史网页存档，不证明原始安装包现在可取 |
| [玩家的《QQ堂5.2下载》备份文章](https://www.cnblogs.com/yaoling1997/p/15733773.html) | 文章可读，作者自述从官网获取并备份5.2，给出[百度网盘分享](https://pan.baidu.com/s/1C1ryoQ-0Jq5TyxxWeB6GDg)，提取码`ynvj` | 可继续核对的原版候选；分享内容/当前完整下载/文件哈希和签名尚未验证，未列为已取得原件 |
| [星动QQ堂条目](https://www.singdown.com/play/3592/34506859.html) | 页面可读，声称5.2/82.61MB，源码出现`QQTang5.2_Beta1Build1_DL_signed.exe`；按明确相对路径拼接同站URL后HEAD返回404 | 未取得文件，不能按文件名中的`signed`认定签名有效；未执行其JS/WASM下载器 |
| [华军QQ堂条目](https://www.onlinedown.net/soft/192829.htm) | 页面标`5.2.1.201`，大小2.450MB；标题“官方版”不是签名证据 | 不能按此体积和标题认定拿到完整客户端 |
| [PC下载网条目](https://www.pcsoft.com.cn/yx/44336.html) | 页面大小2.50MB，并明确写提供“官方下载器” | 下载器不等于完整离线安装包；本轮未执行下载器 |
| [《QQ堂》怀念版历史网页](http://qqt.95hyc.cn/index.html) | HTTP页面实际返回200；HTTPS证书已过期。源码说明是交互演示网页，历史客户端入口主要关联演示与视频 | 可作历史界面/版本外观线索，不能将网页程序或“历史版本客户端”标题当作已取得原生PC安装包 |

上表的第三方自述均保留其来源身份；未因它写“官方”便升级为腾讯认证文件。未支付下载费用、未执行页面提供的JS/WASM下载器，也未登录外部网盘。

## 取得原件后怎样用于参照

1. 下载到本项目忽略目录，记录原页面、实际文件URL、重定向链、下载时间、文件大小与完整SHA-256；保留原包，不覆盖现有社区样本。
2. 静态检查安装包/主程序的版本资源、数字签名及可验证时间戳。文件名和PE版本只能作为证据的一部分，不能单独证明未修改。
3. 用可信工具静态列出/解包，只读地图、资源索引、脚本字面量和图像容器，不启动未知EXE、DLL或安装器。
4. 将地图、物品、动画声明及原偏移与当前社区样本逐文件比较，分别登记相同、被改动和缺失的项；同版证据充足后才锁定正式参照版本。
5. 原版动作时长、头部挂点、运行流程等未被数据证实的部分继续待验。根据用户要求，实际画风、实速和游戏效果交用户人工审核，不以GUI自动化代审。

找到原始安装包后可以据其数据继续制作与核对；当前已有社区参考继续用于不依赖原件认证的原创美术工作，不把来源缺口改记为已完成。


## 2026-11-12 接续改图与后续手游

本轮继续依据用户提供目录中的静态头饰资源核对相位结构。407麋鹿酷比精灵对应本项目原创“霞角鹿灵”：24个原位置、18组不同像素，四个可见视向；2000心愿对应“五心祈愿”：24个原位置、24组不同像素，每相位五颗分离心形。两件stand/walk文件各自逐字节相同，且分别与固定ZIP相应成员相同；核查不赋予未知方向语义、原时长或挂点。

来源合同、PNG与对应源SHA见[407来源合同](../assets/items/head-adornments/docs/WORLD_407_SOURCE_CONTRACT.md)及[2000来源合同](../assets/items/head-adornments/references/world/2000/source-contract.json)。新绘采用自有角色身份及原有道家Q版手绘风格，原客户端贴图只作结构参考。

用户已明确后续制作手游。制作端保留高清母图、RGBA、源逻辑规格和原偏移，并另做32/48/64像素诊断预览；该预览不定义手游格距、碰撞或挂点。具体约束见[手游美术方向补充](MOBILE_ART_DIRECTION_20261112.md)。

## 2026-11-13 接续取证

用户进一步明确从所提供目录启动原生客户端后，全部 UI 应为自有道家 Q 版。已清查 772 个包内 UI 路径及松散资源，接续至 11 月 14 日完成 157 个原生 UI 资源、374 个状态位置，以及 583 个库存图标（含五件多状态资源）的转换和实际安装。该目录的登录背景、登录字标、object.pkg、object.idx 及对应库存 IMG 已按本项目记录变更。上文 2026-11-12 的逐字节相同结论是安装前记录，后续以当前安装回执为准。 [原生交付与恢复](NATIVE_CLIENT_UI_DELIVERY_20261113.md) · [安装字节复核](native-client-installation-20261114.json)

同一固定 QQTang-Local 样本用于核对角色 9 的西向组 2（f12–17）和南向组 3（f18–23）、地图元素 17033／17037／17038 的 18 个原生位置，以及 `fpack`、`frame`、`bg` 各六个库存资源。库存依目录记录的实际资源成员匹配，未用物品编号猜测佩戴或展示资源。人物和地图保留原生声明与偏移；时序、循环与运行挂点仍待证。 [本轮美术与逐项来源](ART_DELIVERY_20261113.md)

2026-11-14 接续：39、114、407、2000、408 的十个 stand／walk 松散资源也已按自有画稿转换并安装。头饰批不改包文件，安装前静态路径计划与安装后回读分别保存。 [世界帧交付](../assets/native-client-heads/world-v1/README.md)

2026-11-14 当前图片已合并为 802 资源统一包，其中 UI 157 件、库存 583 件、头饰世界 10 件、地图 52 件；207 个包内条目指向自有像素。UI 主声明另仅修改共享超链接的一个颜色整数，全部 830 个执行代码段保持原值，Client.exe 未改。 [统一包](../assets/native-client-bundle/review-v1/README.md) · [配色数据回读](native-ui-color-installation-20261114.json)
