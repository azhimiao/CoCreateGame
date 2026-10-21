# 技术架构、版本、构建与平台限制

## 已核实与未运行

默认 **Cocos Creator 3.8.7 + TypeScript**，只做2D Web-first。E08/E09核实官方手册、2025-08-22发布公告及官方release存在；这是固定研究基线，不声称最新。E10的3.8语言页写TS支持基线4.1.0、独立类型检查及部分语法限制，因此游戏逻辑限TS4.1可表达子集，使用ES模块、legacy decorator，不用const enum/CommonJS。此处4.1.0是官方文档的语言支持标签，**不是可安装的npm稳定版本**；独立类型检查工具固定为已核实存在的 **TypeScript 4.1.2**，来源 https://registry.npmjs.org/typescript/4.1.2 （2026-10-21访问）。编辑器携带的转译器/编译链需安装时检查，本轮未安装或运行；若不兼容先修订本档案，不擅自换版本。

本轮只运行Python规格检查器。PATH未检出CocosCreator/CocosDashboard命令，**安装状态UNKNOWN，编辑器路径UNKNOWN，构建未执行**；没有创建Cocos工程，也没有npm构建日志。Python/jsonschema实际版本见validation-report。不得把Python解空间遍历或官方版本存在称作本地游戏性能验证。

## 未来工程边界

全部未来源码规划在本项目 `implementation/`，本轮没有这些产物。采用Boot单入口场景+屏幕prefab，BoardRenderer重绘纯RuleState。规则无cc、DOM、SDK与音频依赖；UI和平台层依赖规则接口。目录归属由tasks的write_scope分开，禁止不同Agent同时改同一文件。共享目录不写，想复用先在本项目写提案由主控审查。

依赖顺序：validated JSON → Rules/SessionReducer → progression/persistence → board/screens → profile adapter。Renderer不能回写机关位；Audio只听事件；SDK不解释LevelWon。Boot需校验数据、初始化profile、恢复存档后才渲染可操作关局。不集成物理引擎、路径动画引擎或通用在线经济服务。

## Profile必须编译隔离

| 包 | SDK/统计/网络 | 变现与发布门槛 |
|---|---|---|
| local-qa | 无平台SDK，无外网请求；本地事件、手动导出回放 | 只离线测试；调试控件不进入任何正式包 |
| P01 | P01 adapter为no-op；无开发者回传、无外链、无广告、无姓名输入；素材全部本包 | 纯本地进度；credits只显示作者/公司名；不得将授权价写成已知 |
| P02-basic-nosdk | 无SDK；全包计初始下载量；禁变现 | 全包≤50MB，移动首页资格≤20MB；总文件≤1500；不称Full |
| P02-basic-sdk | 官方SDK，首个真正可操作状态发gameplay start；其余最小集成按当日规范核对 | 初始≤50MB/移动首页≤20MB；总≤250MB且≤1500文件；禁变现 |
| P02-full | 必须官方SDK；gameplay start/stop，存储/用户功能若使用再单审 | 同总量/初始/文件数门槛；V1仍无广告；Full资格与审核未取得 |

**P04不是G04候选包**。若未来获批适配，必须禁止GA4等第三方统计，只用官方Bridge内置统计或本地离线QA，不复用任意网页包默认全局遥测。P01也不能偷偷用“轻量埋点”回传。为简化边界，本项目所有正式包均不引入独立统计服务/自有后台。

SDK版本号目前UNKNOWN，接入时锁定官方版本、文件哈希、许可、网络域名与实际回调；不能把一款Bridge宣称兼容全部渠道。Full SDK初始化失败时显示可重试错误，不能生产环境自动切无SDK仍报通过。离线QA profile才允许降级。

## 官方硬约束与测量口径

E06：https://docs.crazygames.com/requirements/technical/ （2026-10-21访问）规定总资源≤250MB、≤1500文件；初始下载≤50MB，移动首页资格≤20MB。SDK集成时初始区间从加载开始到首次进入真正可玩状态并发送gameplay start，菜单不算；无SDK则用**全部资源总量**判50MB/20MB。Full必须SDK，Basic禁止广告；按主控要求Basic视为**禁一切变现**。

不能通过提前发start、只计算zip压缩大小、外链延迟下载等规避。官方页面MB是否采用十进制、压缩前后并未完全定义，按最保守口径：1MB=1,000,000 bytes，同时报告构建目录未压缩总bytes、zipbytes、HAR transferred/resource bytes与首个可玩事件时点。文件数统计全递归文件，含引擎、SDK副本、图集、音频与任何分包；source map不入正式包。审批/QA最终口径仍需平台确认，不能标已确认。

项目更严的内部目标（HYPOTHESIS）：全包/首可玩≤10MB、文件≤200，给SDK与平台限额留余量。没有实际Cocos产物，所有当前包体指标**UNKNOWN**，本目录准备zip不属于游戏包，不可拿它代替测量。

## 性能与兼容目标，均未实测

目标60fps（参考设备）、低端≥30fps、移动提交规则到可见反馈p95≤100ms、纯规则单动作p95≤2ms；长关提示2秒内完成。冷启动在10Mbps、100msRTT、CPU4倍节流条件可玩≤8秒；桌面JS heap≤100MB、移动≤120MB、贴图估计≤32MiB。目标是自拟验收线，不是平台公布标准，也不是实测。

实际测量保留设备型号、RAM/系统、浏览器版本、网络/缓存条件、构建哈希、3次冷/热采样、帧时分布、内存与HAR。目标矩阵：Chrome/Edge桌面、Safari macOS、4GB Chromebook、Android Chrome与WebView/P02容器、iPhone Safari/P02容器；具体设备版本等可用时填。无设备=UNKNOWN，不用模拟器推定真机。WebGL不可用给U11说明；context lost先暂停，恢复后从权威态重绘，失败可重载存档。

引擎裁剪只保留2D/UI/音频/必要网络，关闭3D/物理/骨骼/视频模块。图集最多2×2048、DPR上限2、低端降1，位型文字仍清晰；无后处理。系统字体无外部请求，字体栅格缓存需实际测内存。音频以手势恢复，后台暂停；不能因iOS无声重开关卡。P02要求Chrome/Edge，Safari不良可能被禁用、Chromebook4GB需平滑运行（E06），均列实测门槛。

## 构建流程与未来命令合同

安装获批后记录编辑器绝对路径与完整版本、许可；创建2D空工程，保存web-mobile/web-desktop配置，在干净目录构建探针；再实施规则。拟提供npm脚本typecheck/test:rules/validate:content/test:save/test:replay/test:input/test:flow/test:visual/test:progression/test:e2e/audit:assets/audit:network/audit:bundle/build:p01/build:p02-basic/build:p02-full，**目前均未实现/未执行**。tasks中这些命令是将来交付合同，不是现有成功记录。Cocos CLI实际参数以已安装版本 `--help` 为准，冻结设置JSON和真实日志后再写可复制命令，避免假造可执行路径。

正式产物须相对路径、HTTPS下测试、无绝对磁盘路径/硬编码开发域名/远程字体/未知第三方请求；以本地HTTP和平台测试宿主分别验证。网络白名单按profile生成，P01预期只本包资源，P02只必要官方SDK域；广告能力默认false。每次构建产出manifest（hash/bytes/files/profile/version）并在平台环境复测。仅满足包体不等于浏览器能玩或可发行。
