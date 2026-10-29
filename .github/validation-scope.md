# 源码验证分支的固定范围

2026-10-28。此验证小批基于公开首批`6ea487b8b8fe316eff28f371f2e83d243eeab25b`，保留其已发布素材；只加入当前src/server、测试、列出的解析／导出工具与HTML。工作区正在制作的新增美术不纳入这次源码验证，不把部分源码检查称全部美术或整款游戏验收。

目标账号是用户已授权的luhailong-java，2026-10-28再次以现有本机Git凭据核对API账号ID300703237、public仓库及push权限；既有scope包含repo/workflow，没有新增登录或变更凭据。上传独立`codex/art-validation-20261028`分支，默认`codex/initial-public`保持原发布状态。固定提交／tree与逐文件输入SHA另存本机忽略的`.artifacts/remote-ci/`；不用切换工作分支或共享index捕捉在途美术。

检查使用GitHub标准`ubuntu-latest`托管运行器，仅公开仓库允许执行，contents权限只读；官方Actions以完整40位提交SHA固定，Node22、Python3.12、Pillow12.0.0。没有自托管运行器、缓存或产物上传。公开标准运行器适用[GitHub Actions计费说明](https://docs.github.com/en/billing/concepts/product-billing/github-actions)。本机资源协调继续有效，本轮测试／构建在远端执行。

预期检查为Node逻辑／服务端／源地图和新部件几何测试，DIMG严格解析／显式65537尾随段／metadata-only夹具、旧UI常量纯数据夹具、Python语法及基线素材打包。DIMG元数据测试明确不解RGBA；旧UI夹具不运行客户端字节码。实际结果以该提交对应的Actions日志为准，写入工作流本身不代表已通过。

此批不验证本机未上传的新PNG、完整地图几何、所有方向／动作、原版时序、挂点、所有页面状态、中文字号或各分辨率。源码通过后仍继续美术制作与独立运行验收。
