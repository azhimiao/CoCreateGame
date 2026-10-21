# G04 市场与技术证据台账

统一访问日 **2026-10-21**。全部来源为官方游戏托管页、官方规则或官方项目仓库；没有第三方收益估值。网页访问不等于运行游戏。逐条可机器读取的记录见 `evidence-register.json`，包括 URL、发布日期、口径、置信度、反证与复核要求。以下中文为概括，不复制游戏内容、源码或关卡。

| ID | 官方 URL | 已核实事实与口径 | 证据类型 / 限制 |
|---|---|---|---|
| E01 | https://www.coolmathgames.com/0-bloxorz | 方向键移动方块至孔；有软/重开关与不同桥状态，掉落重开 | 官方玩法说明；只支持存在性与规则，未实玩，收入 UNKNOWN |
| E02 | https://www.coolmathgames.com/0-liquid-2 | 方向键/A、D 旋转场景，把白色液体引至橙色区域；可额外收集 | 官方玩法说明；不是液体仿真参数或完整关卡回放 |
| E03 | https://www.coolmathgames.com/hi/0-paint-master | 目标图案、行列刷涂与后涂覆盖；点击耗步，耗尽结束；有有限魔法刷 | 官方本地化玩法说明；英文入口访问失败，说明可读，未实玩 |
| E04 | https://www.coolmathgames.com/submit-a-game | 接受 thinking HTML5，愿为喜欢作品购买非独家托管许可；无广告、外链、开发者回传统计和姓名输入 | 官方投稿规则；不证明会买 G04，也无报价/采购量 |
| E05 | https://docs.crazygames.com/faq/ | 拒绝不符 PEGI-12、面向儿童、缺英文、克隆等内容；Basic/Full 为不同阶段 | 官方准入 FAQ；不表示本游戏已审通过 |
| E06 | https://docs.crazygames.com/requirements/technical/ | 总量≤250MB、≤1500文件；初始≤50MB、移动首页≤20MB；无SDK按总量计；Full必须SDK，Basic禁止广告 | 官方技术规则；MB压缩口径未完全定义，见07保守测量 |
| E07 | https://wiki.playgama.com/playgama/game-requirements/technical-requirements | 禁嵌入 GA4 等外部统计，统计用 Bridge 内置模块 | 官方技术规则；仅条件性边界，不扩展 G04 候选渠道 |
| E08 | https://docs.cocos.com/creator/3.8/manual/en/ | 官方 3.8 系列手册存在，含 2D/Web/TS 工作流 | 官方技术文档；不是本地安装/性能证据 |
| E09 | https://forum.cocos.org/t/topic/170142 与 https://github.com/cocos/cocos-engine/releases/tag/3.8.7 | Creator 3.8.7 发布公告日期为 2025-08-22，官方引擎有同名 release | 官方发布；选作固定基线，不声称是 2026 最新版本 |
| E10 | https://docs.cocos.com/creator/3.8/manual/en/scripting/language-support.html | 文档明确 TS 支持基线4.1.0与独立类型检查需求 | 官方语言限制；文档未证明已选项目编译器/SDK组合可用 |
| E11 | https://raw.githubusercontent.com/cocos/cocos-engine/3.8.7/LICENSE.md | 此 tag 的引擎主许可为 MIT | 官方源码许可；不涵盖整个编辑器、商店、第三方资源 |
| E12 | https://raw.githubusercontent.com/microsoft/TypeScript/main/LICENSE.txt | TS 仓库许可证 Apache-2.0 | 官方工具许可；本轮未安装/打包 TS |
| E13 | https://raw.githubusercontent.com/python-jsonschema/jsonschema/main/COPYING | jsonschema 主许可 MIT | 官方工具许可；仅离线校验器依赖，不进入游戏包 |
| E14 | https://docs.python.org/3/license.html | Python主许可PSF，另有第三方声明 | 官方运行时许可；本轮不分发解释器，不能替代对应安装版本的完整审计 |

E01/E02/E04—E08/E10—E14 页面的可靠独立发布日期为 `UNKNOWN`（不把抓取日当发布日期）；E03 页显示 release 2026-10-08，更新元数据出现不同抓取值，更新日不据此作趋势判断。Bloxorz 页面 release 元数据不能独立确认作品首次发行史，本项目不使用该日期论证“新作”。

## 这些证据能够与不能支持什么

至少两个真实逻辑机关样本已经确认：Bloxorz 支持“状态依赖的可通行性”，Liquid 2 支持“改变整体条件再规划路径”；Paint Master 进一步支持“次序影响终态”的比较。它们不足以证明玩家需要本设计、G04 已达成原创性法律标准或渠道正在采购此机制。

P01 的投稿规则直接对应可进入性。P02 的技术规则对应包体/SDK/受众门槛。两类都不是用户关注或商业化证据。本轮没有保留可比的榜单窗口/排名快照，**不作热门、新作增速或成功概率结论**；也没有授权报价、支付凭证、开发者净收益、单游戏 DAU 或 RPM。

## 反面证据与竞争解释

1. Bloxorz 是已存在的长寿逻辑范式；存在一个经典作品不代表新机关解谜会有新流量。以同质地图套原作规则有克隆风险。
2. Liquid 2 的连续旋转/物理，与本项目离散双层规则有体验距离。不能把它的操作乐趣当成本设计的验证。
3. Paint Master 的覆盖次序与有限步数容易解释；双层位型则可能带来更大认知负荷。G04 必须通过盲测证明理解成本可接受。
4. Liquid 2 页面有内嵌广告/兼容性提示；这是具体在库作品页面现象，不推翻 E04 对新投稿版本的无广告要求，也不证明当前浏览器实际不能运行。
5. 无任何实际付款数据。“可非独家许可”只是一条可能交易路径，不可写成已商业化资产。

## 复核周期与证据缺口

投稿、SDK接入、签约当日重核全部平台规则；引擎/工具安装时重核 tag、完整许可与文件哈希。实验统计必须来自明确受众、设备和样本数，不能复用其他平台成功率。后补Paint Master已有离散操作实证（E15，02逐节点），初版E03“未实玩”为历史抓取范围；连续试玩录像、首30秒/5分钟、手机适配、玩家误读、P01报价、P02审查与净回款仍 **UNKNOWN**；缺口列入12及审计请求。
