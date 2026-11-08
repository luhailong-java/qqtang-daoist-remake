# QQ堂重制客户端与本地服务端

2026-10-26。本文件描述本项目从零编写的开发协议，**不是腾讯原客户端或原运营服务器的协议兼容声明**。默认只监听 `127.0.0.1:4387`；同一电脑可打开多个浏览器页签，各自建立独立本地身份，进入同一房间联机。

## 启动和状态

运行 `node scripts/serve.mjs`。无 npm 依赖，Node.js 22+。`PORT` 可改端口；启动器始终使用回环地址，不主动开放局域网或互联网。关闭终端或 Ctrl+C 停止游戏服务。房间和会话在内存中，重启清空；客户端需要重新创建身份。不存在 QQ 账号密码登录，也不访问腾讯账号或服务器。

GET `/api/health` 不需要身份，返回服务名称、版本、`authoritative:true`。其他接口除创建身份均需要本服务签发的 token。

## 身份与请求

POST `/api/session`，JSON `{name,character}`，返回201 `{token,session:{id,name,character}}`。昵称截断12字，默认角色 `maomao`。token 是当前开发会话的随机凭据，只返回给创建者；建议存 `sessionStorage`，每页签独立。公开玩家id与私有token是不同值。

普通请求使用 `Authorization: Bearer <token>`。GET `/api/state?token=...` 返回完整快照；GET `/api/events?token=...` 建立SSE。EventSource不支持自定义Authorization，因此SSE允许查询token；它仅发给本机服务，不应写入公开链接或远端日志。

所有POST使用 `Content-Type: application/json`，正文上限8192字节。带Origin的请求必须与服务Host相同，回环模式拒绝外部Host。错误为非2xx及 `{ok:false,error:"中文消息",code:"错误码"}`。常见401身份失效、403房主权限/来源不符、409状态冲突、429限流。请求不能通过传入他人的 `id` 或 `ownerId` 操作另一玩家。

## 房间

| 接口 | JSON输入 | 结果 |
|---|---|---|
| POST `/api/rooms` | `{name,mode,map,bots,duration,channel}` | 创建并进入房间，调用者为房主 |
| POST `/api/rooms/:id/join` | `{}` | 加入空席，满席但有AI时替换一个AI |
| POST `/api/action` | `{action,...}`，见下表 | 执行房间操作 |
| POST `/api/input` | `{type:"move",dx,dy}` 或 `{type:"bomb"}` 或 `{type:"item"}` | 服务端执行本人输入，额外返回accepted布尔 |

默认创建三个真实的本机AI练习模板，普通竞技/抢包山/合作探险。它们不代表在线真人；首位真人加入后成为房主。每房最多八席，AI数量0–7，时长60/120/180/300秒。默认频道 `free`，客户端也可创建 `practice` 频道的房间。地图默认 `courtyard`，界面和引擎采用 `courtyard` / `town` / `factory`；地图实际规则由引擎管理。

| action | 参数 | 权限及规则 |
|---|---|---|
| ready | `ready:bool` | 当前玩家准备；房主自动准备 |
| character | `character:id` | 未在房间也可更换本地角色；房间内需处于等待状态 |
| team | `team:"red"/"blue"` | 等待时改队；合作探险统一红队 |
| config | `config:{name,mode,map,bots,duration}`，也接受平铺字段 | 仅房主；等待时修改，其他真人需重新准备 |
| seat | `seat:0..7,locked:bool` | 仅房主，只能开关空闲席位 |
| start | 无 | 仅房主；至少两位真人/AI，其他真人均准备；竞技需两队，必要时自动把一个AI分到另一队 |
| pause | `paused:bool` | 仅房主，对局进行中暂停/恢复整个房间 |
| return | 无 | 仅已结算；全房回等待，其他真人重新准备 |
| leave | 无 | 离开并移交房主；进行中本人被移出，其他人可继续 |
| chat | `text:string` | 房间消息最多200字，400ms间隔，保留最近50条 |

## 实时快照

SSE帧为 `event: data` 和 `data: <JSON>`；客户端用 `eventSource.addEventListener('data', ...)`。连接时立即推一次，之后约100ms推送，15秒心跳注释。HTTP变更也返回 `{ok:true,...snapshot}`，客户端不必等待下一帧才更新界面。

快照顶层为：`session`、`rooms`、`currentRoom`、`characters`、`modes`、`server`。`rooms`包含id/name/mode/map/count/max/status/channel/botCount/ownerId/template。`currentRoom`为空或包含id/name/mode/map/duration/channel/ownerId/members/lockedSeats/chat/game/paused。成员为 `{id,name,character,team,isBot,ready,seat}`；游戏状态按src/game.js公共契约序列化，以下划线开头的引擎内部字段不外发。

服务端每50ms推进引擎。客户端只发方向和动作，不上传自己的坐标、速度、分数、伤害或胜负。输入每身份最多60次/秒；移动节流、糖泡容量、碰撞与道具是否可用继续由引擎判定。

客户端失焦只释放本机按键，不自动暂停其他玩家。房主主动暂停冻结整个权威状态；非房主没有暂停权限。SSE断开保留30秒房内席位，重连同token取回同一状态；超出后移出并移交房主。无活动且无实时连接的身份30分钟后清理。房间最多30个，身份最多100个。

## 验证

`node --test tests/server.test.mjs` 实际启动临时端口服务，覆盖双身份准备开局、权限/配置冻结、输入归属、暂停冻结、八席上限/替换AI、空席开关/房主移交、SSE真实快照/重连，以及JSON边界和真实PNG资源。最终通过数量以实际测试输出及项目总验收记录为准。
