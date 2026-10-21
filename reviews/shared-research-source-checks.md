# 共享研究独立来源核查

独立核查日期：2026-10-21，Asia/Shanghai。对象为 `shared-research-baseline/` 保存的作者材料版本，快照时间 17:56:41+08:00。网页由审计员另外打开并读取相应正文，不以作者的 HTTP 200 或 hash 代替语义核查。下表记录可复查的 URL、正文定位与口径；网页公布/生效日期如无明确说明均为 **UNKNOWN**，不是访问日期。官方宣传和文件描述不代表本团队获得批准、真实交易或实际回款。

| 来源 / claims | 独立打开的官方 URL、正文定位 | 核查结果与限制 |
|---|---|---|
| S01 / C01–C02 | [Coolmath 投稿](https://www.coolmathgames.com/submit-a-game)，Submission / game requirements | 支持非独家托管许可采购、HTML5 思考类、无暴力脏话，专用版本移除广告、外链、开发者回传及姓名输入；展示时可以尚未全部改好。不是具体报价或采购承诺。 |
| S03 / C03 | [CrazyGames Introduction](https://docs.crazygames.com/)，Launching on CrazyGames | 支持 Basic 限量测试且禁广告及 IAP，Full 再做完整集成/QA。数据较好获得的是后续邀请，未保证正式发布。 |
| S19 / C04 | [Basic Launch Guide](https://docs.crazygames.com/resources/basic-launch-metrics/)，The process and your dashboard | 至少 7 天且至少 500 plays；未达 500 则 21 天自动结束。500 是游玩次数，不能换成独立玩家数。 |
| S20 / C05 | [Technical](https://docs.crazygames.com/requirements/technical/)，File Size & Count Limits | 250MB / 1500 文件、初始 50MB、移动首页资格初始 20MB 均有正文支持；无 SDK 时以总大小计。接 SDK 后按加载开始至首次进入可玩状态的 Gameplay start 事件计初始量。 |
| S21 / C06 | [Payouts](https://docs.crazygames.com/payouts/)，Payment Timeline & Thresholds | 支持 €100 付款门槛、NET 60、争取次月 10 日前处理；实际到账另受支付路径影响。页面还区分 €10 开票门槛，不能与付款门槛混同。 |
| S22 / C07–C08 | [FAQ](https://docs.crazygames.com/faq/)，Can I publish… / Do I still own… / Step A | 支持保留所有权、已有其他发行仍须有发行权；初审拒绝原因列 PEGI-12 不符及内容针对儿童。此处是平台内容要求，不能推导儿童绝不能玩，也不能证明获得官方分级。 |
| S06 / C09 | [Poki testing](https://developers.poki.com/guide/how-testing-works)，Player fit / What to aim for | 支持 500 玩家试验、平均时长 3+ 分钟、25%+ plays 超 3 分钟，C2P 到 Web fit 才测。后续另建议 C2P 65%+、平均 5+ 分钟，经营模拟 10+；不是跨平台通用成功率。 |
| S07 / C10 | [Poki share](https://developers.poki.com/guide/share)，Build or video link / Show us… | 可访问无登录浏览器构建或玩法视频；3 张实机截图，单张最多 5MiB。首次游戏/无注册公司的回答选项存在，不等于本团队已获准。 |
| S08 / C11 | [Poki partnership](https://developers.poki.com/guide/revenue-deal-types)，Web exclusive / Non-exclusive | Web 排他含浏览器、Discord、YouTube Playables；列明移动商店、Steam、主机不属于该示意排他。默认 5 年等内容为 indicative，协议决定。非独家为可选一次性许可、无同等分成推广。 |
| S16 / C12 | [Poki content](https://developers.poki.com/guide/content-player-safety)，Originality / Working with AI / Oversaturation | 允许审慎 AI 辅助，要求原创与测试，可能要求创作过程记录；性能达标并不覆盖原创/题材饱和拒绝。未发现“AI 全面禁止”的支持。 |
| S23 / C13 | [Poki Requirements](https://developers.poki.com/guide/requirements-quality)，Hard requirements / Technical standards | 支持多设备、16:9、存储异常仍可玩、本地资源、SDK 事件交替。Web Fit 及发行要求集成；广告播放期间、暂停/回到游戏等另有事件限制，不能仅测试“发过事件”。 |
| S24 / C14 | [Poki payouts](https://developers.poki.com/guide/payouts-billing)，How you get paid / What determines… | 银行转账/PayPal及协议决定金额有支持；该页没有可用于本项目的统一固定费率。 |
| S10 / C15 | [Playgama quick start](https://wiki.playgama.com/playgama/quick-start)，Step 1–5 | 支持注册接受条款、接 Bridge、上传 QA、审核、报表结算。没有单款流量保底。 |
| S11 / C16 | [Playgama Welcome](https://wiki.playgama.com/playgama)，SDK 段落末尾 warning | 明确不代投 Poki/CrazyGames；同时说开发者可尝试带 Bridge 自行上传。后一句不构成目标平台批准，也不等于应同时混装多个 SDK。 |
| S25 / C17 | [Submitting a game](https://wiki.playgama.com/playgama/submitting-a-game)，Game Archive / Distribution | ZIP 根 `index.html`、解压后文件合计不超 300MB、可排除分发平台、需 QA 和审核，有支持。 |
| S26 / C18 | [Technical Requirements](https://wiki.playgama.com/playgama/game-requirements/technical-requirements)，第 1–4 项 | Bridge 必需、不得依赖外部注册、禁止 GA4 等外部统计，有支持；正文允许 Bridge 内置 analytics，标自 Bridge 2.3.0 起可用。并非所有统计事件都要删除。 |
| S27 / C19 | [General FAQ](https://wiki.playgama.com/playgama/faq/general)，Who owns… / legal documents | 保留权利并授平台合作站点发布的 sublicense，注册接受 terms，有支持；FAQ 不是已经逐条审查的实际条款。 |
| S28 / C20–C21 | [Payments and Statistics](https://wiki.playgama.com/playgama/faq/payments-and-statistics.md)，How much… / withdraw / individual | 合作站点月 Net Revenue 分段 70% / 80% / 90%，站内及 iframe 伙伴流固定 50%，$100 提现门槛，个人按国家法域个案处理，有支持。净额扣除及本团队可支付性仍未知。 |
| S29 / C22 | [FAQ](https://wiki.playgama.com/playgama/faq)，末段 | `developer.success@playgama.com` 的确公开列出；未发送邮件。 |
| S13 / C23–C24 | [Azur publishing](https://azurgames.com/publish-with-us/)，Game Submission Form / What’s next / Write us | 视频、APK等字段、先内部评估再买少量流量看留存/CPI、首阶段两天反馈、公开发行邮箱有支持。公开页还提 Facebook 与 App Metrics 集成；当前版本/具体 SDK/预算仍须另外确认。 |
| S14 / C25–C26 | [TapNation publishing](https://www.tap-nation.io/publishing/)，Buy-out option / How It Works | 概念/原型/build、两周评估、匹配后协商条件、后续可能买断，均有支持。不是本项目买断报价、付费测试预算或合同承诺。 |
| S30 / C27 | [TapNation submit](https://www.tap-nation.io/submit/)，Your game / 页首 | 收入、D1、平均时长带必填标识；称 7 个工作日个人回复。表单没有在可见正文定义这些数值的样本、窗口或 D1 算法；不得据此填写杜撰测量。 |

## 另外取得的官方反证与边界

1. [Poki for Developers 测试条款 PDF](https://app.poki.dev/2024.03.13_Terms_and_Conditions_Poki_for_Developers.pdf) 是从当前 Requirements 的 Terms & Conditions 链接打开的，共 7 页。**文件名包含 2024.03.13，不据此认定其是当前最终商业协议或已知生效日期。** §1.4–1.5 区分使用测试平台与另行商议的长期合作；§4.2–4.3 不保证执行测试、测试不付报酬；§5.1 为测试目的的全球 Web 许可，非所有权转移；§3.3 限制把其预览链接用于竞争平台，并禁止第三方 trackers。后续必须核准适用版本。
2. [Poki 外部资源政策](https://developers.poki.com/guide/external-resources-policy)，Possible exceptions / Getting a resource approved：部分统计可逐案申请 CSP 批准，Google 产品不可批准；需公开托管且游戏内可访问的隐私政策。这与上述 PDF §3.3 的 trackers 禁止表述存在需要澄清的适用边界，不能以技术 CSP 可开放就断言合同许可已获得。当前采用零外部统计能规避此设计依赖；仍应记录两处原文来源及待确认项。
3. [Playgama terms](https://developer.playgama.com/terms) 本次匿名网页读取只获得需 JavaScript 的壳页，**未读到条款正文**。不能将 HTTP 可访问当成完成合同审阅；本轮没有注册或提交。

## 方法失败记录

Playgama 六个 `.md` 变体（quick-start、站点根、submitting-a-game、technical-requirements、faq/general、faq）在 web 工具直接读取失败，随后读取其无后缀官方 URL 成功；支付 FAQ 的 `.md` 成功。这是访问方式差异，不是已证明作者引用失效。猜测的 Poki `/terms-and-conditions` 和 `/guide/external-resources` 未取到正文，随后通过 Requirements 页的实际链接取得上述 PDF 和正确 policy 地址。未删去失败结果，也未将它们列为政策内容证据。

## 本地独立检查

证据基线及结果见 [manifest-and-checks.json](F:/CoCreateGame/reviews/shared-research-baseline/manifest-and-checks.json)。27 条 claim 均能连接到 22 个唯一 source，URL 一致，无重复 ID。作者访问日志 22 个 HTTP 200 只证明作者记录的请求结果。Playgama 累进公式在假设 N=0/1000/1001/3000/3001/5000 时，分别得到 0/700/700.8/2300/2300.9/4100 美元，与官方逐段表达式一致；这些是算术检查输入，**不是实际收入**。

未运行会写回作者目录的研究脚本；未运行项目验解、未声明审过三款规格；本地截图为既存作者证据的视觉抽查，不是审计员本人完成的实玩。
