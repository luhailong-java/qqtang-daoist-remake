# GitHub公开仓库与首批文件范围

2026-10-27，America/New_York。用户明确授权把本独立项目上传到luhailong-java账号的公开仓库。

- 项目：QQ堂·道家Q版重制。
- 仓库：https://github.com/luhailong-java/qqtang-daoist-remake 。
- Git远端：https://github.com/luhailong-java/qqtang-daoist-remake.git 。
- 可见性：public；创建后由GitHub API确认owner为luhailong-java、private为false。
- 首批分支：codex/initial-public，初次提交无父提交。
- image参考仓库单独保留：本地origin为Azure Repos，历史GitHub为luhailong-cpp/image；本项目远端与其无等同关系。

上传范围为自有客户端／本地服务端、脚本、测试、配置、当前美术候选及来源文字、必要参考和导出的地图JSON。`.artifacts/`中的社区客户端ZIP／pkg／idx、设备登录辅助脚本、验证临时文件，以及dist、日志、Python缓存、环境凭据均由.gitignore排除。此次不使用Git LFS，图片作为真实PNG进入普通Git对象；首批最大文件约10.96MiB。独立项目提交不改动image共享HEAD、index或refs。

来源清单记录精确字节哈希，`.gitattributes`关闭文本换行自动转换，确保Windows与其他平台检出后JSON、来源记录和图像保持相同字节。

本批发布前重建素材清单：社区样本721个元素定义中，338个已有自有候选、383个待制作；全部accepted:false。该分母只是现有地图源元素，不是完整游戏美术总量。源地图377个、目录381项，社区来源的目标腾讯原版身份仍待确认。`node --test tests/*.test.mjs`为46／46通过，不能据此宣布全游戏玩法或全部美术完成。

当前实机终验仍受Work本地浏览器禁用限制。已有图像装配预览不冒称实机截图；未制作／比例／接缝／动作／原版规则缺口继续保留。仓库用于保存当前开发状态，非最终发布版。实际上传提交及远端可读性应以GitHub分支和提交记录为准。
