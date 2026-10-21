# G02 技术架构与渠道构建合同

2026-10-21｜**候选方案，未创建Cocos项目、未构建、未测本地性能**。离线Python报告不能证明Creator、浏览器或移动SDK工作。

## 1. 核实的版本与选择边界

候选编辑器 **Cocos Creator 3.8.8**：官方英文下载页E12确有发布记录（2025-12-16），访问日2026-10-21；不是声称最新版。本轮不安装编辑器/SDK、不接受商业条款、不生成最终游戏工程。

外部类型检查器候选 **TypeScript 5.6.3**：微软官方版本标签/许可E18可核。它不是已核实的Creator内部编译器版本。Cocos 3.8官方语言页E13写的是TS4.1.0能力与legacy decorator限制；因此源代码先限制于该语言子集，不用新decorator、const enum、import=、export=等不受支持写法。独立tsc检查和Creator转译是两道验收，不能以一者通过代替另一者。该候选组合兼容性 UNKNOWN，T03必须用实际安装版本/hash、类型声明和最小场景构建确认；失败就REVISION_REQUIRED并审查变更，不偷偷升级版本。

Python本轮实际3.11.15，jsonschema4.26.0，见验证报告；这些是规格校验工具，非客户端运行依赖。TS/npm/Node版本最终由T03生成lock记录；不把本机node存在当工具链已验证。

## 2. 模块分界与未来目录

未来实现仍放本项目内`implementation/`，本轮没有创建这些文件：

| 单写者目录 | 内容 | 依赖边界 |
|---|---|---|
| core/ | RuleCore、legalActions、不可变状态 | 不import cc、DOM、SDK、Date/Math.random |
| data/ | 内容校验、RunStore、Undo、SaveCodec、Replay、Hint | 只依赖core和抽象存储；hash归一见04 |
| ui/ | Cocos场景/Prefab、InputRouter、ScreenRouter、Audio | 不直接修改堆栈；发Command收快照 |
| art/ | 原创源文件、运行资产、许可台账 | T06单写，UI只消费发布资产 |
| content/ | 20关数据副本/实验配置（带源hash） | 从GameSpec导出，不能运行时改题 |
| platforms/p02/ | Basic/Full专用adapter | 只此构建引入CrazyGames SDK |
| platforms/p04/ | Playgama Bridge adapter | 不引入GA4或其它外部统计 |
| mobile/ | 待确认后的独立原生可行性分支 | 接口/构建条件先于引擎承诺 |
| qa/、toolchain/ | 实际日志/截图/版本锁 | 单写结果；公共package配置由T03集成者合并 |

纯规则层返回数据事件，View按快照呈现；PlatformAdapter只提供能力，不向RuleCore注入广告/云/时间。单个产物只能选一个平台adapter；编译期剔除其它SDK及密钥，不用运行时域名猜测同时加载多家脚本。SDK版本/来源/hash/许可在获准集成时登记，当前不捏造最新SDK方法名。

## 3. 平台适配接口与生命周期

自定义合同（不是官方SDK API名）：`init():Promise<Capabilities>`、`loadingStart/Stop()`、`gameplayStart/Stop()`、`loadSave()/writeSave()`、`track(ApprovedEvent)`、`requestInterstitial(requestId)`。Capabilities包括save/analytics/ads是否可用，默认均false。平台缺能力时降级本地免费玩法。init10秒超时进入可玩但禁广告/网络统计；平台强制SDK初始化才能审核时，QA标失败，不能把降级误报平台合规。

进入真正可操作PLAY才发gameplayStart，菜单/二次加载不提前发。暂停、广告、后台和结算发Stop且幂等；恢复要玩家点继续。广告不影响求解/容量/进度，失败/关闭/超时统一继续；本轮所有广告关闭。生产日志不含开发者私服上报。

## 4. P02硬门槛（E04/E05，已web重核）

官方technical https://docs.crazygames.com/requirements/technical/ ，FAQ https://docs.crazygames.com/faq/ ，访问2026-10-21：

* 总资源文件≤250MB，文件数≤1500；初始下载≤50MB；移动首页资格初始≤20MB。
* SDK存在时首载窗口为开始加载至首次真正可玩的gameplayStart；无SDK时按**整个游戏文件总量**计，故总包≤50MB，争取移动首页则整个包≤20MB。不能用拆目录/晚发start规避。
* Basic可无SDK且**禁止变现**，含广告和IAP；Full SDK必须。要兼容Chrome/Edge，Safari、Chromebook 4GB等需实际验收；不是所有网页自动开移动App权限。
* PEGI-12内容兼容、排除面向儿童内容；G02定位13+，不使用低龄识色/儿童教育营销。年龄定位并不是正式评级证书。

内部更严预算（HYPOTHESIS）：首可玩传输≤12MB、全包≤20MB、≤200文件。未来检查器同时统计原始文件总量、文件数、初次请求字节和可玩时间；按十进制MB保守验收，记录资源压缩方式。压缩包大小、空项目构建大小、Python运行速度均不能充当游戏性能测量。

## 5. P04、P01及合同隔离

P04技术页E07 https://wiki.playgama.com/playgama/game-requirements/technical-requirements ：Bridge必接；禁GA4及类似第三方统计。仅Bridge官方允许统计或本地离线QA；不内嵌自建分析、Sentry遥测或隐藏回传。网络验收按构建请求allowlist核对，无开发者统计端点。E07§5.2允许内容内部滚动但§5.5要求主场景单手可玩而无额外滚动；G02六盘谜题不主张大型策略/RPG例外。采用06的PLAY完整无滚动布局；320×568含safe/font1.3及568×320小横屏均有静态矩形合同，不能把该校验称实际渲染/平台通过。菜单滚区按04唯一pointer所有权，不借滚动移动件。存档/方向改变/弹窗关闭/无外部注册要求需实测；桌面使用横向满工作台布局而非窄竖条。

P01不是G02候选。若人类日后改范围批准P01，必须独立无广告/外链/开发者回传/姓名输入构建，credits只放纯文本声明，E10；不能把P04/P02生产包直接交过去。P03只是权利冲突对照，Web独家未审前不能并行答应P02/P04分销。SDK适配不等于分销许可。

## 6. 构建流程与可执行命令边界

**本轮真实可执行**（PowerShell，从任意工作目录用绝对路径）：

```powershell
python -B F:\CoCreateGame\games\G02\tools\verify.py --all
```

可选重建数据/人读表：在G02先运行`python -B tools/author_data.py`，再`python -B tools/render_levels.py`，最后verify；author_data只产生研究JSON/Schema，不是游戏生成器。通常复核只运行verify，不重新生成设计输入。

以下是T03后才存在的**未来命令合同**，当前NOT_RUN、无package.json、不应执行并把找不到文件当游戏失败：

```powershell
npm ci
npm run typecheck
npm run test:rules
npm run test:persistence
npm run test:replay
npm run test:levels
npm run test:ui
npm run test:platform -- P02
npm run test:platform -- P04
npm run test:network -- P04
npm run test:browser
npm run check:bundle -- P02
```

T03负责人须提供这些npm脚本和锁文件：typecheck为独立tsc --noEmit；rules对照Python向量；levels重放20解/消融；persistence/replay按04；UI/browser按10浏览器自动化与截图；platform用SDK回调模拟+真实portal预览，network记录实际请求，check:bundle按本节计算。10中人工项目仍需设备/研究员，npm退出0不能代替真人结论。

Creator CLI模板（官方E14，**未执行**）：

```powershell
$g02CreatorExe = '实际安装并核对hash的CocosCreator.exe绝对路径'
$g02FutureProject = 'F:\CoCreateGame\games\G02\implementation\cocos-project'
& $g02CreatorExe --project $g02FutureProject --build 'platform=web-desktop;debug=false'
```

真正工程有场景UUID、裁剪模块、平台配置后，从Editor构建面板导出`configPath`配置并纳入版本控制，分别产出p02-basic、p02-full、p04包。官方成功退出码36，32/34失败，不把所有非0都按常规shell失败解释；还需存在产物、日志无编译错误、浏览器可玩。CLI仍可能需要GUI环境。脚本中的分号在Creator参数字符串内部，不是shell链式执行。

## 7. 性能目标与测量方案

HYPOTHESIS：手机60fps，低端降30fps；JS/纹理内存目标≤160MB；10Mbps/150ms延迟冷启动首次可玩≤5秒；每关重开内存稳定；触控提交响应P95≤100ms（动画可继续）。这些全部**NOT_MEASURED**。

渲染仅2D Sprite/Label，最多18件物品，最多6盘/4章；合批图集最多2×2048²，不启用3D/物理/Spine/远程字体；无运行时下载原创关库。Hint20k状态/500ms上限分帧，回调带revision。设备实测保存型号/OS/浏览器、请求HAR、资源大小、帧时间分位、峰值内存、20次重开对比，不用桌面CPU推断手机速度。

## 8. 移动分支决策（P05/P06）

E08/E09说明发行入口，不保证Cocos原生/TS被指定SDK支持。P05由T13、P06由T16分别先获得书面：SDK及版本、是否支持Cocos JSB、广告/归因/统计/同意管理、最低OS/ABI/目标API、签名归属、APK或AAB、数据访问和测试预算。未收到前状态BLOCKED，不虚构Android命令或SDK成功日志。

若能支持，单独Creator原生导出Android工程，再按原生工具链构建、签名、安装与SDK真机验收；相关工具版本以当时官方要求及发行商确认锁定，不从Web产物重命名为APK。若不支持，采用Unity/C#独立移植候选，需要另行技术评估和人类预算；可共享JSON关卡/规则向量/合法授权图资产，不能说TS原封不动跑C#。iOS还需Mac/Xcode/签名等独立条件，目前UNKNOWN；本轮无移动构建承诺。

修订接口版本：game-spec/tasks为1.1.0，存档合同v2恢复新command_epoch；身份/缓存先于BUSY/版本，失败缓存、128序号窗口、4096终点checkpoint与撤销独立。全部未来实现须移植protocol-vectors.json，不能把当前整数探针当RunStore源代码。T15仅Web P02/P04；P05 T13/T14/T18，P06 T16/T17/T19分别依赖与审批。
