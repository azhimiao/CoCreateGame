# G02 独立反方审计｜作者1.1定稿复核

2026-10-21。审查者为原独立审查者Jason，未参与G02创作或修订。本轮只读G02作者包及`research/playthroughs/G02`；复核程序和结果留在`reviews/G02-rereview-*`。没有修改作者文件、G04或根STATUS。

**当前结论：REVISE；未闭合BLOCKER为0，未闭合MAJOR为1（对标研究证据）。原首审六项Finding全部独立复核闭合。** 独立检查20关共26,483个可达状态且全部可通关；作者规格验证20关、2 Schema、31规则向量、9协议表、5静态布局和19任务DAG通过；最终准备ZIP 37成员/36载荷完整匹配。当前仍不能GO：后补研究的核心输入为0，真实玩法节点及连续时间窗没有证据。这是研究证据缺口，不是已证明规则规格有错、市场失败，也不把未来引擎/真机测试倒置为当前准备阶段阻断。

原作者修订索引中的`independent_closed=false`和`PENDING_RE_REVIEW`是送审时状态；闭合权限在本报告。作者的核对报告仍保留送审状态，没有被我改写。当前项目仍`REVISION_REQUIRED`、`ready_for_build=false`，本报告不代替人类施工批准。

## 当前冻结Hash

实际检查后再次逐项对比作者目录39个文件，均与复核快照相同。关键输入和最终交付摘要如下：

| 文件 | SHA-256 |
|---|---|
| `game-spec.json` | `c9acded2840cc970a2fdfb3fba27ec4db9f94c7ccf0d5f86fffcea6af21d0516` |
| `tasks.json` | `7dede4c4375b0c063f6c85ea2525990197b5516218810bc9bea09509fb26209c` |
| `game-spec.schema.json` | `b9c88e20252c5623504763345b92f3efeafadecf1c3020bbe832dc0ad5a72d19` |
| `tasks.schema.json` | `f7c28d0e8dcb2a9532cd716d4c8bf684181f8234b73cf2d80d59661e21b3f269` |
| `tools/verify.py` | `6d4fc587800aed08432ee7de8dd3d96fdade0d6566e3f707bceac30762b164f6` |
| `tools/check_contracts.py` | `4f69099b83a2f60b5f6ef9b8ef1fbd30b49b97ff6c1c9469b17093b327b95bb2` |
| `protocol-vectors.json` | `fbaebb961eb76fee9bd4e664df0e4248d98a1172fdb1c99850b4979ce2870282` |
| `layout-cases.json` | `b2018c19bd301599b7d9d8c9679e3fe6f89783f316a52a915bbb2708d788987c` |
| `REVISIONS.md` | `2b5bd9fa710eea8eb66a646c9352f3fcbec9df8013938e0d4c197271291963b0` |
| `revision-index.json` | `172c4763367e0d17eb299c15f714a5b5faf3ae65573a64129d5eb6915e04c12d` |
| `verification/verification-report.json` | `5ac631af446ddf63a6531962f3ff53d7d4704ad5531d55d5cc15216a15a6ca7b` |
| `package-manifest.json` | `e184a40a395c6bd81e660a88433cff39b95622e6b6a486219dcf32f8fd05fc36` |
| `verification/package-check.json` | `fde2b40fc013a7931a75c4055eb952dd91d8dab7e3408ae30d1dd8ee9eefc27b` |
| `G02_Preparation_2026-10-21.zip` | `9b541c8b76bae1030fb7fa81ae65afe782662e3bc10b98f21313d9df6a8c3241` |

完整39文件当前SHA-256见[独立复核结果](F:/CoCreateGame/reviews/G02-rereview-results.json)。ZIP CRC、37个成员精确集合、无重复成员、manifest和36载荷逐字节匹配均通过。它是准备材料ZIP，不是游戏构建。

## 原六项Finding复核

| ID / 首审严重度 | 修订位置与内容 | 独立验法和结论 |
|---|---|---|
| B-G02-01 / BLOCKER：重试回执与BUSY/STALE优先级冲突 | [04 §2.1](F:/CoCreateGame/games/G02/04_Systems_and_Data.md:27)固定envelope/run/epoch→缓存身份→序号窗口→消费→status→revision→规则；同身份异payload为ID_CONFLICT，失败决定也缓存；03、10/R16同步 | 9张协议表通过。另在ANIMATING、PAUSE、WIN、PLAY原样重试，均返回原receipt，整个探针状态无变化；同ID改dst拒绝且不替换；缓存BUSY在恢复PLAY后仍返回原失败。**CLOSED** |
| M-G02-01 / MAJOR：恢复run后的序号/幂等信息未定义 | [04 §6–7](F:/CoCreateGame/games/G02/04_Systems_and_Data.md:89)与机器协议采用同run新epoch、seq从1、缓存清空；保存盘面/revision/128撤销快照；128数值窗口与4096终点checkpoint分离，checkpoint含撤销历史 | 9/10、127/128/129、拒绝/接受/UNDO混合、checkpoint后首条UNDO、旧epoch迟回等向量通过。独立验证恢复保留完整逻辑snapshot，旧epoch零副作用，新epoch序号1可执行。**CLOSED**；真实持久化I/O仍属未来T05/T11验收 |
| M-G02-02 / MAJOR：短屏拖放与滚动争手势，P04核心屏约束未闭合 | [06 §1/3](F:/CoCreateGame/games/G02/06_UI_Art_Audio.md:7)、04 §3、03 §4和07 §5现在规定PLAY无滚动：竖屏三列两行、小横屏六列一行；44 CSS px热区，不整体缩小；GAME/SCROLL/BUTTON owner不转交 | 作者5样例PASS；独立按矩形公式核安全区、六盘、顶件与封箱不重叠及工具区边界。P04官方§5.2允许游戏内滚动、§5.5要求主场景无需额外滚动；核心屏采用无滚动方案。**CLOSED**；未声称真实字体渲染、触控或门户预览通过 |
| N-G02-01 / MINOR：满盘掩盖顶色错误，撤销原向量只是夹具 | [verify.py](F:/CoCreateGame/games/G02/tools/verify.py:203)分开有余量异顶色和满盘同顶色案例；实际SEAL→序列化→新对象恢复物件/封章/动作数并验证重锁 | 31规则向量通过。只删除实际actions函数的同顶色守卫后，新独立用例立即在`same_top_spare_capacity_rejected`失败。**CLOSED**；旧24向量变异PASS保留为历史基线，不再作为当前断言 |
| N-G02-02 / MINOR：L09/T4、L13/T3可绕过，不能把摆入关卡等同掌握 | [05](F:/CoCreateGame/games/G02/05_Levels_Economy.md)、game-spec `feature_coverage`明确为可选盘；[12 §2](F:/CoCreateGame/games/G02/12_Falsifiability.md:22)明确通关不证明掌握，并提出机制解释提问 | 独立删除可选盘后，原解未用该盘且仍逐步合法获胜。**CLOSED**；关闭的是语义过度主张，不是声称玩家已学会 |
| N-G02-03 / MINOR：发行DAG没有机器渠道作用域 | tasks/schema、09、11明确T15仅P02/P04；P05由T13/T14/T18，P06由T16/T17/T19分别走独立条件 | 19节点无环/独占输出；网页条件只允许T15，P05条件不能解锁P06；实际`verified_conditions`仍空。**CLOSED**；没有把网页许可转成移动批准 |

## 唯一未闭合MAJOR：研究证据

**M-G02-03：参考作品核心操作仍未直接观察。** 这是研究证据缺口，不是G02接口/规则规格缺陷。位置：[02 §5](F:/CoCreateGame/games/G02/02_Benchmark_Playthrough.md:46)、[团队观察索引](F:/CoCreateGame/games/G02/evidence/team-browser-observation-index.json)、[原观察报告](F:/CoCreateGame/research/playthroughs/G02/observation.md)。Good Sort Master官方URL为https://playgama.com/game/good-sort-master；Screw Out官方URL为https://www.crazygames.com/game/screw-out-bolts-and-nuts；初轮TapNation Color Water Sort是另一作品，不能混作同一对象。访问日2026-10-21。

13张研究截图的bytes/SHA-256独立核对全部通过，但Good Sort只有Ignore/Play Now两次站点UI输入，未确认运行棋盘；Screw Out只有Only Essential一次站点UI输入和末帧Level 1棋盘，核心点击在截止前没有派发日志。确认核心输入合计**0次**。所以合法放置/拆取、明确非法操作、匹配、暂存占位/满槽边界、胜利、失败和游戏内重试均未观察。480.006秒是包含加载、排障和读图的总尝试窗口，不是连续实玩；首30秒与连续5分钟均NOT_RECORDED。教程手势、静态棋盘与浏览器重启不算规则/游戏内重试证据。

影响是不能用对标实证评估手动封箱/借位的认知负荷，也不能澄清参考游戏的失败边界；不说明G02规则本身错误，更不证明市场失败。没有玩家偏好、稳定榜单窗口、买方采购或实际付款证据；收益与玩家表现仍UNKNOWN。

修复应补获准真实参考的核心输入→状态变化、受控拒绝/匹配/满槽边界、成功/失败/游戏内重试链，并记录官方URL、日期、设备/浏览器、输入日志、前后帧和连续30秒/300秒时轴。受阻样本继续标BLOCKED；不得用静态图或总驻留凑成实玩。市场、玩家和交易证据分开记录。复验由同一审查者逐节点核原始时轴/帧；核心输入仍为0时不得关闭此MAJOR。无需为补研究而先构建G02游戏。

## 可施工路径复述

以下是G02原创HYPOTHESIS规定的理想流程，不是参考游戏的真实时间测量。目标时间25秒/275秒均为设计假设，玩家未必按时完成。

**首30秒理想路径：** 启动BOOT读取资源与双槽，成功到HOME；无档点“开始整理”进入L01，有合法活动档则显“继续Lnn”。坏档进入恢复页，不静默清档。L01三盘容量2，底→顶为T0=`A`、T1=`A`、T2空，需求A×2。点T0顶件选源，再点T1移动一件；T0空、T1=`AA`但不自动消除。再点独立“封箱”按钮，清空T1、记录A章，先判胜利再写完成并解锁L02。结算显示2步，玩家点下一关进入L02。加载、思考或误操作可能使其不能在30秒内完成。

**前5分钟理想连续路径：** 每关成功后玩家主动点下一关；无广告/货币。表中箭头为单件MOVE，“封Tn”为独立SEAL。五关设计目标合计275秒，不含加载与思考差异，不表示实际必达L06。

| 关卡 / 初态（底→顶） | 合法完整路径 | 目标秒数 |
|---|---|---:|
| L01：A / A / 空，容量2 | T0→T1，封T1 | 25 |
| L02：AB / BA / 空，容量2 | T0→T2，T1→T0，封T0，T1→T2，封T2 | 55 |
| L03：AB / CA / BC / 空，容量2 | T0→T3，T1→T0，封T0，T2→T1，封T1，T2→T3，封T3 | 60 |
| L04：AAB / BBA / 空，容量3 | T0→T2，T1→T0，封T0，T2→T1，封T1 | 65 |
| L05：ABC / BCA / CAB / 空 / 空，容量3 | T0→T3，T0→T4，T1→T0，T1→T3，T1→T4，T2→T4，封T4，T2→T0，封T0，T2→T3，封T3 | 70 |

**输入和规则：** 盘内物件底→顶堆叠，仅顶件可取；MOVE一次一件。目标盘须OPEN、未满、接收该色，且为空或顶色相同；同盘移动非法。已选源点其它盘先尝试MOVE，非法保留选择、不自动换源；点同源或盘外取消后才可换源。SEAL必须主动按键，且盘OPEN、可封、非空、同色、数量恰等该色需求；成功清空并永久退盘、记录唯一该色章。锁的`unlock_after`按AND判断，封章可同时打开多锁。胜利为全部盘清空且每种需求色恰封一次；胜利优先于死局判断。只有当前没有任何合法MOVE/SEAL且未胜才DEADLOCK；有合法动作但数学无解不能自动判死。UNDO恢复逻辑盘面、封章、动作数并重新派生锁，保留递增revision/原始事件序号；最多保存最近128步历史。重开需确认，回初态但保留已完成关进度。HINT免费，500ms或20,000状态上限任一达到则UNKNOWN，不自动行动。

**身份、存档与接口：** 命令含`run_id,command_epoch,command_seq,expected_revision,op`及操作字段。处理顺序为校envelope→校run/epoch→查相同身份缓存（同payload原receipt、异payload ID_CONFLICT）→数值序号窗口→消费新序号→状态/BUSY→revision→规则。新epoch旧身份无副作用；首次决定的拒绝也缓存并占窗口，缓存返回不重发事件/保存。Run.dispatch返回不可变receipt与delivery，当前盘面另由readCurrent读。v2主槽`g02.save.v2`、备份`g02.save.v2.backup`：生成新payload/checksum→旧有效主槽写backup→整体写新主槽→回读验hash；读取校验两槽并选有效最高save_seq，双坏先确认而不静默清档。恢复有效盘面/撤销历史后换新epoch并从序号1开始。128收据窗口独立于4096条回放尾段；第4097条前checkpoint为第4096条终点且含完整撤销快照，随后尾段首条UNDO仍能重建。哈希用于损坏检测，不是防作弊；未来真实I/O需故障注入，当前探针不是持久化实现。

**状态、事件、发行：** BOOT→HOME/ERROR；HOME→选关/PLAY；成功MOVE/SEAL先原子提交、更新revision/守恒、派生锁、胜利优先、再死局判断、保存和动画。后台停止gameplay；回前台先暂停，玩家点继续。播放/SDK回调按run/epoch/request身份一次处理。默认本地QA事件最多1000条；生产P04仅Bridge允许字段，禁止GA4/自建统计回传；P02 Basic禁变现，Full必须官方SDK，Basic无SDK按整个游戏包≤50MB（移动首页≤20MB），总量≤250MB/1500文件；内容PEGI-12兼容、不得儿童定向。P01禁广告/外链/开发者回传；不属于G02候选。合同、书面SDK、素材权利、审批与回款仍UNKNOWN。所有这些是档案接口/发行合同，不代表有游戏实现、实际手感或性能已通过。

## 实际验证范围

Python3.11.15/jsonschema4.26.0。为不回写作者报告，将39文件复制到`reviews/G02-rereview-snapshot/`并在副本运行`python -B tools/verify.py --all`：20/20解+BFS、2 Schema、31规则向量、19 DAG、9协议表、5静态布局PASS。作者冻结的`verification/verification-report.json`输入hash与作者树一致。独立复核脚本`python -u -B F:\CoCreateGame\reviews\G02-rereview-check.py`独立重放20关并搜索26,483可达状态；去掉同顶色守卫后专用向量`same_top_spare_capacity_rejected`立即失败；另外复核身份重试、恢复epoch、可选盘消融、静态布局、13张观察图hash和37成员ZIP。结果在[复核结果JSON](F:/CoCreateGame/reviews/G02-rereview-results.json)。全程没有运行Cocos/TS、产品浏览器或真机，也没有把离线探针称为运行时。

## 官方规则、许可与商业边界

2026-10-21重新核对：[CrazyGames技术页](https://docs.crazygames.com/requirements/technical/)规定总≤250MB/1500文件、SDK下首载≤50MB/移动首页≤20MB、无SDK时按总包≤50/20MB；[FAQ](https://docs.crazygames.com/faq/)规定Basic不变现、Full须SDK、内容遵守PEGI-12且排除面向儿童；[Playgama技术页](https://wiki.playgama.com/playgama/game-requirements/technical-requirements)要求Bridge、禁GA4等第三方统计，允许内部内容滚动但要求主场景无需额外滚动。G02档案对应约束已落实；实际构建bytes、SDK回调、HAR和门户验收未跑。

08区分Cocos Engine MIT与Creator编辑器协议、TS、jsonschema和Noto字体许可；最终素材未生产，不能称完全清权。成熟的顶层分类/同色规则与G02主动封箱、盘退场、AND章锁/接收标签差异均作为待证伪设计；没有证明法律首创，也未发现带入参考源码/资产。官方作品页、发行商作品、投稿规则和真实成交分开；没有本作报价、CPI/RPM、付款或净收益数据。17000元例算是含失败/维护的内部假设，不是实际支出/发行商报价。P01/P03仅约束对照；P04不加第三方分析；P05/P06分别需要自身SDK、签名、原生QA、合同和人类批准，不能用网页/P05条件替代。

## 阶段结论

11屏导航/输入、状态错误、存档合同、关卡数据、可关闭弹窗、资产清单、异常处理及19任务DAG已有可独立复述的准备规格。原六Finding现可关闭，不要求作者为此回填审计ZIP。唯一未闭合项是参考核心玩法证据；保留REVISE、不标BENCHMARKED、不判KILL。之后如补研究，仅按影响重开相关Finding；人类批准前仍不进入T02以后开发任务。READY_FOR_BUILD也不由本复核自动触发。

## 首审历史与变异测试

首审Markdown SHA-256：`91349070ca161418b34ec6efa2348f0cd2cdf6f5be9e8e777338057b0411a525`；JSON：`0609491b80f2ad98d5ccc92fdd082ba0187520de653e0738c0a796f1cb84c1f3`。当时结论1 BLOCKER/2 MAJOR/3 MINOR；早期两次脚本退出1且无traceback，根因UNKNOWN，不能回写成从未失败。

历史基线：旧版24向量在删除同顶色守卫后仍PASS，暴露旧目标满案例掩盖顶色问题。旧变异断言只适用旧代码/hash，不作为本轮可运行验收。当前测试的正确期望是：只删除`or (target and target[-1] != colour)`后，`same_top_spare_capacity_rejected`必须失败；本轮实际结果`REJECTED_AS_EXPECTED`。历史24向量PASS保留为发现记录，当前31向量PASS和隔离变异失败是新证据。不要以变异后的完整BFS搜索超限代替针对性断言。

审计复跑命令只写本审计结果文件：`python -u -B F:\CoCreateGame\reviews\G02-rereview-check.py`。最终当前审计JSON与本MD一致：`REVISE`、0未闭合BLOCKER、1项研究MAJOR。
