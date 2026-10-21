# 对标方法、证据口径与本次缺口

> 本文保留本批研究完成时的观察快照。后补 Paint Master 的有效操作、单关成功、失败和重开见 [跨批次实际操作汇总](../observation-summary.md)；以下“未实玩”只描述本批采集，不覆盖后补结果。全项目仍没有完整连续首30秒/5分钟记录。

访问日期统一为 **2026-10-21**（Asia/Shanghai）；浏览器日志保存实际UTC时间。只写 `F:\CoCreateGame\research\benchmarks\`。已读根目录MASTER_HANDOFF.md、AGENTS.md及data/platforms.json；用户指定不写STATUS、不写games，优先于通用更新STATUS约定。没有游戏实现、付费安装、投稿、签约或对外发信。

## 交付与计数

- 六平台每家4张具名官方证据卡，共24条平台—作品记录；每家2份深析，共12条。
- 24条按标题暂归23组：Piece of Cake在P02/P04各有官方关联证据，但开发者显示名、渠道发行时间、控制描述不同，版本/权利主体等价UNKNOWN。
- **完整直接试玩0；完整首30秒0；完整首5分钟0。确认核心输入的局部直接操作1款（Drive Mad）。**
- Level Devil为PARTIAL_ENTRY_ONLY：地图、弹窗、首次关卡场景，不具备角色位移前后对照，不计实玩完成。Paint Master为LOAD_ATTEMPT_ONLY：游戏区域空白。浏览器共尝试3款，日志中的多次命令不算更多作品。
- 12份完整流程结构均标SECONDARY_RECONSTRUCTION，其中Drive Mad附局部直接操作；并非另有12份直接回放。24卡中23款没有确认核心输入。官方视频实际观看0。

## 选样与范围

优先采用platforms.json列出的具名游戏。P01、P02、P03、P04与P06各保留包内四例，准确纠正Playgama Good Sort和Piece of Cake、CrazyGames Deadly Descent的真实URL。P05把Block/Arrow/Sort品类占位换成Color Sort Puz、Tower Craft、Stack Ball、Bottle Jump 3D，全部有Azur官网具名作品/历史案例证据，另用发行商商店核实包名及描述。P05/P06目录是历史样本，不是2026最新下载榜或采购榜。

家族映射是分析判断，不是官方分类。game_id恒为数组，元素只能G01—G10；空数组表示NONE并说明。Blocky Blast、Stack Ball、Bottle Jump不强行归类。Tiny Fishing只映射G07成长/离线邻接，Thief Puzzle只映射G04机关/路径邻接。样本没有覆盖G10，不增加平台或候选来补数量；G10仍有待另行具名补证。

## 可机读结构与追溯

benchmarks.json顶层为metadata、summary、sources、benchmarks、gaps。每卡含platform_id/game_id/name/source_url/accessed_at/published_at/evidence_type/metric_definition/deep_analysis_source。来源ID只用于引文，不是新游戏ID。每条已知陈述附source_ids和verification；每个深析维度分别存known、unknown、hypotheses。未知值显式写UNKNOWN，不用空字符串、0或相邻作品参数代替。

published_at是文章/页面发布日期；无明确日期即UNKNOWN。game_release_date单独表示官网列出的本渠道版Release，只有月份时不补日。updated_at是页面或商店更新日期，不能冒充首发。accessed_at为本次请求日期，不保证web后台缓存也在当天刷新；CG-ARROW的缓存/重定向专门记录。

来源仅采用官方平台、发行商文章及发行商商店描述；商店是身份/操作的辅助证据，不新增发行目标。Fancade域Wiki标DEVELOPER_HOSTED_COMMUNITY_WIKI，托管官方不等于每个编辑者是开发者，只交叉确认输入，保留版本差异。不用玩家评论确立游戏规则，也没有使用第三方收益估算。官方文案也可能矛盾或有营销修辞，矛盾不擅自“修好”。

## 流程重建和时间纪律

12份深析每份包含首次30秒、首次5分钟、核心输入、成功、失败、重试、中期循环、UI、广告经济、设备。没有连续轨迹，30秒/5分钟字段一律UNKNOWN；“首次30秒”下的链只表示根据官方规则重建的操作依赖，不表示30秒内确曾发生。未知关数、教程次序、动画和经济均逐项列出。自拟验收路径单列HYPOTHESIS，不是对标观察结论。

本次没有观看官方视频，页面出现Video/Gameplay Video/Trailer不当成观看，不写视频秒数。官方教学交叉证据优先：Suika有游戏教学+官方攻略；Drive Mad有Poki教学+开发者域Wiki；Color Sort Puz有2023官方案例+署名商店；Stack Ball有官网目录+署名商店；TapNation两深析有官网教学+官网直链商店（Guess另有官方案例）。Paint Master、Arrow Escape、Screw Out、Arrow Puzzle、Good Sort主要是单一平台教学，明确保留独立交叉来源缺口；同站翻译不是独立证据。

## 浏览器证据

使用现有 `F:/beautiful/node_modules/playwright-core` 和本机缓存Chromium 149.0.7827.55（目录chromium-1228），不改F:\beautiful，不安装浏览器。Windows桌面headless，viewport1365×900；没有Android/iOS真机。正常访问平台页面、发送鼠标/键盘事件、保存可见截图和命令日志，没有注入关卡状态或复制专有游戏源码。

Poki英文URL实际浏览时自动转到同站/zh/页面（保留最终URL）。第一次截图的广告休息/Preparing和空白不能证明广告真播放，更不能当普遍平台阻断。Drive Mad后来加载，ArrowRight保持2000ms前后车辆位置可见变化；后图接近格纹终点但没有结算，不能宣称过关。Level Devil在弹窗及入口花费多次输入，最后仅见首关场景，停止继续操作；不把命令名character-moved当作位移已证实。Paint Master未见运行棋盘。

evidence/session.json保留命令、实际URL、canvas数量、页面错误和截图相对路径。截图是本次页面观察而非商店宣传图。证据文件名是采集时标签，不是通过断言；以可见画面和这份裁决为准。没有视频录像，不能用离散截图补出未观察到的中间过程。

浏览器已通过context.close正常关闭；随后退出仍等待stdin的采集脚本进程，未发现本次浏览器/profile进程残留。临时profile/cache/tmp仅在evidence/runtime下；绝对路径已核对，但自动审批以“blocked by policy”拒绝递归删除，没有给出更具体原因。因此该本机目录仍在，**交付打包必须排除evidence/runtime/及其全部子项**，不得收录session cookies/cache。清理结果另存evidence/cleanup.json；delivery_manifest.json只枚举可交付文件。browser-probe.cjs和session.json及截图保留；旧名browser-session.json统一更名为session.json，不改写已采集事件。

## 指标与反证

页面存在性→平台关联；评分/投票→页面用户反馈；历史案例→发行和运营经验；商店下载档位→某商店累计安装门槛；任何一项都不等于当下采购、真实新作成功率、净收入或开发者到账。未建立热榜名次或DAU序列。Playgama的daily leaderboard人数与匿名榜名口径不明，未当活跃用户数；正文性能“完美/无延迟”未当实测。

Color Sort Puz案例2023-02-09自述累计总收入超过150万美元、支出超过100万美元，属于历史项目公司口径；成本范围、税、回收顺序、开发者份额不全，禁止相减作为利润。该案例中两次免费撤销加激励广告三次和商店无限撤销矛盾，当前规则UNKNOWN。Guess Their Answer的实时PvP与离线宣传、答案“人群”样本与授权都不明。Screw Out暂存满即失败/再拆才失败边界不明。均不应自动流入施工规则。

## 终审可用结论与未完成项

存在性和官方描述可引用；**P0没有本次直接可观察的G01/G02核心规则轨迹，G04 Paint Master也没有实玩**。这构成后续施工阻塞，不可把本库标READY_FOR_BUILD。其他agent的research/playthroughs/G04可由主控交叉引用，本轮未读取/修改其目录，不能把其未来结果计入本次数量。

接下来优先补G01/G02合法/非法操作、失败和重试的直接证据；再补G04的覆盖/机关规则；补每深析连续首30秒/5分钟、明确版本、实际广告触发与真机输入；解决单源教学与版本冲突。市场需求、收益、合同及独立质量评审仍独立进行，不从这里推导开发许可。
