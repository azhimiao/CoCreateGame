# G02 市场与证据台账

访问日统一为 **2026-10-21（Asia/Shanghai）**。以下均通过 web 读取官方站点；只保存必要的事实摘要与 URL，不把搜索摘要当实际试玩。`OFFICIAL_DESCRIPTION` 是官方说明，`OFFICIAL_REQUIREMENT` 是准入规则，`PORTFOLIO` 是历史发行，`CATALOG_DISPLAY` 是展示信号；均不是交易证据。页面未给发布日期则 UNKNOWN。正式提交/采购当日重核。

## 1. 可重新核查的事实

| ID | 官方 URL（访问日均如上） | 类型 / 发布或更新日 | 支持的有限结论 / 指标口径 |
|---|---|---|---|
| E01 | https://playgama.com/game/good-sort-master | OFFICIAL_DESCRIPTION；页面标发布 2024-10、更新 2026-06 | Good Sort Master: Triple Match：同一货架凑三个相同物，清完过关；桌面拖动、移动触控。是单作说明，不是营收数据 |
| E02 | https://www.tap-nation.io/games/color-water-sort-puzzle-games/ | OFFICIAL_DESCRIPTION + PORTFOLIO；发布日期 UNKNOWN | Color Water Sort Puzzle Games：管中分类液体、考虑空间，过关宝石可用于提示，官方称无时间限制；未给数值经济 |
| E03 | https://www.tap-nation.io/games/ | PORTFOLIO；发布日期 UNKNOWN | 目录链接到 E02，能核对 TapNation 发行样本身份；不证明当前采购需求 |
| E04 | https://docs.crazygames.com/requirements/technical/ | OFFICIAL_REQUIREMENT；发布日期 UNKNOWN | 总文件≤250MB、≤1500；首载≤50MB，移动首页资格首载≤20MB；无SDK按总包量算；Full SDK必须 |
| E05 | https://docs.crazygames.com/faq/ | OFFICIAL_REQUIREMENT；发布日期 UNKNOWN | Basic SDK可选且不变现；Full SDK必须；初审要求符合PEGI-12，排除面向儿童内容 |
| E06 | https://wiki.playgama.com/playgama/quick-start | OFFICIAL_REQUIREMENT；发布日期 UNKNOWN | Bridge接入→上传→QA→审核→报表/结算；不构成单作收入保证 |
| E07 | https://wiki.playgama.com/playgama/game-requirements/technical-requirements | OFFICIAL_REQUIREMENT；发布日期 UNKNOWN | 禁嵌入GA4等外部统计；可用Bridge内建统计（页面写从2.3.0起）；横竖屏/存档/关闭弹窗要求；§5.2允许内容内滚、§5.5主场景无需额外滚动，G02不主张大场地例外 |
| E08 | https://azurgames.com/publish-with-us/ | OFFICIAL_SUBMISSION；发布日期 UNKNOWN | 表单要视频/APK，先内部判断再有条件公开流量测试；涉及留存/CPI；SDK实际条件须书面确认 |
| E09 | https://www.tap-nation.io/publishing/ | OFFICIAL_SUBMISSION；发布日期 UNKNOWN | 接收概念/原型/现有包，页面描述评估、合作及可选买断；不等于录用或保底款 |
| E10 | https://www.coolmathgames.com/submit-a-game | OFFICIAL_REQUIREMENT；发布日期 UNKNOWN | HTML5思考型，禁广告/外链/开发者回传统计；不是本轮G02新增候选 |
| E11 | https://developers.poki.com/guide/revenue-deal-types | OFFICIAL_DEAL_DESCRIPTION；发布日期 UNKNOWN | Web独家与非独家模式不同，默认独家描述五年；最终按实际合同，不用于擅自扩渠道 |
| E12 | https://www.cocos.com/en/creator-download | OFFICIAL_RELEASE；3.8.8页面标2025-12-16 | 候选Cocos Creator 3.8.8确有官方发布记录；不声称最新版本或本机可用 |
| E13 | https://docs.cocos.com/creator/3.8/manual/en/scripting/language-support.html | OFFICIAL_TECH_DOC；发布日期 UNKNOWN | 3.8语言页写TS 4.1.0能力/限制和legacy decorator；不能从页面推导本机编译器准确版本 |
| E14 | https://docs.cocos.com/creator/3.8/manual/en/editor/publish/publish-in-command-line.html | OFFICIAL_TECH_DOC；发布日期 UNKNOWN | CLI参数与成功退出码36；不是执行日志 |
| E15 | https://docs.cocos.com/creator/3.8/manual/en/editor/publish/android/index.html | OFFICIAL_TECH_DOC；发布日期 UNKNOWN | Android为独立原生发布流程；网页包不等于合格APK |
| E16 | https://raw.githubusercontent.com/cocos/cocos-engine/v3.8.8/LICENSE.md | LICENSE；文件日期 UNKNOWN | 对应引擎仓库MIT文本，保留版权声明；不涵盖编辑器全部权利 |
| E17 | https://raw.githubusercontent.com/cocos/cocos-engine/v3.8.8/licenses/EDITOR_license_and_terms_en.txt | LICENSE；文件日期 UNKNOWN | Creator编辑器另有协议，含闭源部分；通用制造工具再分发需另审 |
| E18 | https://raw.githubusercontent.com/microsoft/TypeScript/v5.6.3/LICENSE.txt | LICENSE / VERSION_TAG；文件日期 UNKNOWN | TS 5.6.3官方版本标签可核，Apache-2.0；仅作为外部类型检查候选 |
| E19 | https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/OFL.txt | LICENSE；文本版权2014—2021，文件日期UNKNOWN | Noto Sans SC候选字体OFL-1.1，需随附许可和遵守保留字体名 |
| E20 | https://raw.githubusercontent.com/python-jsonschema/jsonschema/main/COPYING | LICENSE；文件日期 UNKNOWN | jsonschema工具MIT；本轮环境4.26.0，仅用于离线Schema验证 |
| E21 | https://www.crazygames.com/game/color-water-sort-3d | OFFICIAL_DESCRIPTION；页面标2024-12发布、2025-01更新 | Famobi的Color Water Sort 3D是另一独立作品；不能与TapNation的E02合并身份 |
| E22 | https://playgama.com/ | CATALOG_DISPLAY；发布日期 UNKNOWN | 访问时Playgama Top区有Good Sort Master；动态展示顺序，不保存固定名次，不推单作增长或付款 |

E04 主控补充的硬约束已独立读取原页核对。注意 MB 口径采用平台原文；未来包检查保守按 1MB=1,000,000 bytes 验证未压缩文件总和和请求实际传输量，保存两者，不能用压缩包大小替代。

## 2. 两个核心真实样本及反证

Good Sort Master 与 G02 同属物件归类，参考价值是限位整理和读图；不复制货架布局、食物图标或关卡。Color Water Sort 与 G02 同属分类空间规划，参考价值是顶部可取与容量推理；不推断其倒水单位等于 G02 的单件单位。E01/E02 的规则只有说明级证据，内部精确碰撞、撤销、难度曲线和实际首局体验 UNKNOWN。

市场正面信号：两种分类表达存在于目标发行网络及历史目录。反面解释：成熟样本证明供给和同质竞争，不能证明新作剩余需求；无真实玩家点击/流失/收益数据，原创“封箱后失去容器”可能损害轻松感；同类经验也可能令评审认为新意不足。需第12份实验和真实渠道答复才能收敛。

## 3. 明确的 UNKNOWN 与不支持的结论

当前购买价、单作净收入、RPM、CPI、D1/D7、素材点击率、当前采购预算、同类新作成功率、实际付款、用户数口径、准确热榜名次全部 UNKNOWN。不引用公司总下载数估算 G02；不以评分票数当活跃玩家，不以首屏推荐当成交。二手攻略中声称的倒水细节、广告频率、宝石数值均未采用。

研究证据足够提出施工草案，不足以标 BENCHMARKED 的实际试玩完成，也不足以宣称游戏已被市场验证。参考实际试玩与独立审计缺口分别登记，不用设计假设填补事实。

团队同日浏览器后补作为单独DIRECT_BROWSER_OBSERVATION纳入02第5节：research/playthroughs/G02/observation.md，GoodSort未确认棋盘、ScrewOut末帧Level1但确认核心输入0。13图hashPASS仅完整性，未补合法/非法/匹配/满槽/胜败重试/连续30秒及5分钟。作者初轮web-only叙述保留，不回填历史；E01/E02仍为官方说明级核心规则。
