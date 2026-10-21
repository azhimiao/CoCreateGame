# G01 技术架构与渠道构建合同

本章为HYPOTHESIS施工方案；没有创建Cocos项目或编译游戏。仅Python数据验证实际运行，不能据此写“Web性能达标”。

## 引擎与锁版

默认 **Cocos Creator 3.8.8 + TypeScript**，2D、整数格规则，不启用物理/3D/骨骼/联网系统。2026-10-21访问[官网下载页](https://www.cocos.com/en/creator-download)（E11），页列3.8.8、2025-12-16；这是确切候选，未声称比所有发行版更新。通过Dashboard获取；将精确编辑器build号、下载URL、安装包SHA256及附带TS编译器版本写入未来toolchain lock，未锁前禁止自动升级。

本轮 `Get-Command cocos,CocosCreator` 未在PATH找到可执行文件，**全机安装状态NOT_VERIFIED**；没有运行编辑器、空项目、Web/Android构建或真机测试。Cocos编辑器/EULA与MIT引擎分开审查，见08。TypeScript确切版本随安装候选锁定，当前UNKNOWN，不能随意指定另一个npm最新版。

## 模块与单向依赖

| 模块 | 责任与接口 | 禁止依赖 |
|---|---|---|
| Content | 验schema/引用/几何、20关ID→不可变Level | SDK、视觉节点 |
| Rules | 04的evaluate/commit/derive；纯整数、确定性 | Cocos帧时间、网络、随机数 |
| Solver | mask搜索、winning successor、死锁标签，≤256状态 | 渲染、提示币、外部服务器 |
| Session | 日志/revision、输入锁、状态机、教程标记 | 平台直接API |
| Progress/Save | 首通集合、双备份、重放校验、云冲突 | 自建统计上报 |
| BoardView/UI | 格→逻辑像素、箭条/门/船期/13屏、音画状态 | 直接改规则mask |
| PlatformAdapter | 统一ready、loading、gameplay、pause、storage、analytics capability | 不同渠道SDK互相导入 |
| BuildProfile | 编译时选择唯一adapter、去除调试与禁用分支 | 运行时加载其他渠道脚本 |

`Content -> Rules/Solver -> Session -> UI` 表示上游提供数据、下游使用；存档与adapter通过显式注入，规则模块不知道当前平台。共享机制仅提出接口，不向根shared-mechanics写文件。未来目录建议 `future/rules/`、`future/ui/`、`future/save/`、`future/content/`、`future/platforms/<profile>/`，任务各写自己的目录，集成任务才统一装配。

内部适配器合同：`init():capabilities`，`loadingStart/Stop()`，`gameplayStart/Stop()`，`readSave/writeSave(envelope)`，`trackAllowedEvent(name,payload)`，`onPause(handler)`。这些是自有包装名，不冒充官方SDK函数名。T03/T12/T13需将实际API路径/版本/错误码逐一映射并实测。SDK不可用时玩法本地继续，发布环境必须仍满足渠道强制集成审核。

## 各渠道独立包

| Profile | SDK与回传 | 包体/文件/加载门槛 | 工程闸门 |
|---|---|---|---|
| LOCAL_QA | 无SDK；本机opt-in日志，≤2000事件/会话环形缓冲 | 自拟≤15MB/250文件，首可玩≤8MB | 本地日志不能自动上传；发布时不带导出按钮 |
| P02_BASIC | 默认无SDK；禁变现；无GA/自建统计 | 官方总≤250MB、≤1500文件；**无SDK时总包≤50MB，移动首页≤20MB**；本项目保守≤20MB总/250文件 | 第一可玩时机真实；无广告/IAP代码、无P04SDK；审核素材不是儿童定位 |
| P02_FULL | **CrazyGames Full SDK必须**；仅官方统计/存档；本产品默认仍无广告 | 总≤250MB、≤1500文件；从开始加载至首Gameplay start的初始下载≤50MB，移动首页≤20MB | 只有Full邀请才做；事件不得在菜单伪造；广告功能若另批准再启用 |
| P04 | **Bridge必须**；只用Bridge统计，**禁GA4等第三方统计** | 官方上传压缩包≤300MB；root index.html；拉丁文件名；本项目目标≤15MB/250文件 | 无P02SDK/自建上报；不设URL域名锁；无外部登录要求；逐项做浏览器/旋转/后台QA |
| P05 | 原生SDK、ABI、数据协议UNKNOWN；不可预装别家SDK | 自拟APK≤100MB仅预算；对方实际限制UNKNOWN | 取得Cocos兼容与指定SDK版本书面确认后才出Android试包；不承诺Web可转APK |
| P01_RESERVED | 无广告、外链、开发者回传/名字输入 | 自拟≤15MB/250文件 | 只是隔离预案；不自动新增候选或提交；CREDITS仅名称及离线许可，不放URL |

官方依据 E03/E06/E07/E08/E09，均2026-10-21重核。P02单位按官网MB描述，CI保守用十进制bytes（1MB=1,000,000 bytes）计，官网未给压缩口径时同时报告解压总量、ZIP量、实际请求量，以更严格值判定。P04300MB口径为上传archive，不能拿它推导首屏速度。准备ZIP的体积与未来游戏包限制没有可比验证意义。

网络白名单：LOCAL_QA/P01无任何开发者服务端请求；P02_BASIC只允许包资源及宿主自身请求；P02_FULL只允许审核确认的CrazyGamesSDK/官方端点；P04仅Bridge与审核确定的平台端点；P05由合同列单。外部字体全部本地打包。禁止把`fetch`、GA4、Sentry、其他统计库因“调试”残留。验收需对包内依赖清单与运行抓包两种检查，不只搜索字符串。

## 布局、性能与资源预算（全部未测假设）

首批Web目标：总≤15MB、首可玩资源≤8MB、文件≤250；中端设备帧p95≤20ms、输入至反馈p95≤100ms、内存稳定运行30分钟不持续增长、求解≤50ms。测量必须记录设备/浏览器/屏幕/网络/采样方法，未安装前这些是目标不是“通过”。Android性能/崩溃率/CPI留存全部UNKNOWN。

只用2D批处理/一张≤2048²RGBA图集、字体本地子集、音频按需；退出界面注销事件，固定20关全部本地数据。不可因为去掉SDK而宣称平台合规。P04公开要求含较老OS/浏览器（E08）；Cocos候选是否覆盖Android5/iOS9及相应WebGL环境是**未解决兼容风险**，必须最低版本实机或获正式允许缩减声明，不得默认只测现代手机就通过。若官方要求无法满足，停P04分支并申请技术路线修订，不擅改规格。

## 构建与复现

本轮可执行命令：`python tools/validate.py`；`python tools/write_level_catalog.py`；`python tools/package.py`（后两者只生成文档/准备ZIP）。Python3.11.15、jsonschema4.26.0为本轮实用环境，不代表未来游戏运行依赖。

未来Cocos构建命令的确切形态来自[官方命令行文档](https://docs.cocos.com/creator/3.8/manual/en/editor/publish/publish-in-command-line.html)（E16）：

```powershell
# 开发批准后、安装并导出配置后才能执行；本轮未运行
& $env:G01_CREATOR_EXE --project 'F:\CoCreateGame\games\G01\future' --build 'configPath=./build-configs/p02-basic.json'
```

不预设`G01_CREATOR_EXE`路径。构建面板导出配置并锁版，`--build`参数不靠猜；官方文档列成功退出码36、参数错误32、构建错误34，应结合日志和产物核验，不能一律按0判断。各profile分别导出到自身目录，清理也只能本G01内已核实绝对路径。所有运行资源用相对路径，P02不允许包资源绝对地址。

未来`npm run test:rules/test:save/test:ui/test:campaign/test:web`与`build:p02-basic/build:p02-full/build:p04`是T04—T16需建立的脚本名，当前不存在，禁止报告已通过。每包输出SHA256、SDK版本、网络白名单、文件数、解压/压缩/首屏字节及真实QA日志；依赖构建失败不重命名Web包为APK。
