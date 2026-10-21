# G04 Session事件合同｜修订r2

2026-10-21；规则版本仍1.0.0，未改20+2关玩法。本文为HYPOTHESIS施工数据合同；Python模型只核对合同，不是TS/Cocos实现。对应Hypatia G04-M02，修复待独立复核。

## 规则事实、Session富化与提交

`reduceCommand(Level,RuleState,op)`纯函数只返回`{accepted,state,facts:RuleFact[]}`。fact仅type/payload，没有attemptId/seq/source/assisted/stars，也不发布到总线。同一规则输入的输出在任何Session中完全相同。event-contract.schema.json的$defs.RuleFact列出每个载荷；StateCommitted携带**包含failure的完整RuleState**。最后胜利事实叫RuleWon{used,par}，失败叫RuleFailed{reason}。

`reduceSession(Content,Session,Command,Progress)`是纯应用事务。Command={op:U/R/D/L/X/UNDO/RESTART/HINT_CONFIRMED,source:keyboard/touch/mouse/system/qa}；source由InputRouter/调用者显式给定，不进入RuleCore。RESTART另由应用注入新的唯一attemptId，不使用随机数决定关卡。当前attemptId来自createSession；nextSeq初始1，从会话恢复值继续；assisted在HINT_CONFIRMED时永久置true直至重开。

接受前检查activeAttemptToken、当前会话和暂停/输入锁。旧attempt/token返回STALE_ATTEMPT，无规则调用、事件、保存或结算。锁内移动丢弃为BUSY（本地输入诊断，不发布规则事实）；UNDO/暂停可中断动画。规则非法返回CommandRejected事实，可富化为一个本地事件，但RuleState/history/路线/totalAccepted不动。Session元数据nextSeq与规则步数不是同一个计数。

有效命令事务：保存动作前history并调用规则→确定新RuleState/acceptedCommands/totalAccepted→若由PLAYING进入WON，且本attempt尚未winCommitted，则调用**纯**commitWin(progress,session)，计算stars与新记录，置winCommitted=true→reduceSession按facts顺序产生富化payload的eventDrafts→Controller为整个批次预留seq并把nextSeq推进后的Session连同Progress原子提交→广播已编号批次一次→安排存档/渲染。nextSeq在提交内推进，不能先保存旧seq再广播。commitWin只由这一入口调用；progression模块只提供纯函数，不监听总线再次结算。WON提交后的活动存档为null，进度同一事务保存；下一局生成新attempt。重复终局dispatch或SDK/动画回调均不能再次触发RuleWon/commitWin。

## 唯一发布者与精确载荷

运行时`SessionController`是ApplicationState唯一写者、SessionEvent唯一发布者。纯reduceSession仅生成富化payload的eventDrafts，不广播；Controller提交前从nextSeq逐项取号，并在同一次提交内推进nextSeq，提交后一次性广播。seq不足容纳整个批次则拒绝事务并要求受控重开，不能发布半批次。EventBus只分发已编号的不可变事件，没有“代补发”能力。Rules、Renderer、Audio、Boot、存储和SDK adapter均不得直接发布SessionEvent或直接改进度；AppStateMachine只向Controller请求转换，不另持权威副本。

SessionEvent={v:1,seq:1..9007199254740991,attemptId,levelId,source,type,payload}。attemptId与levelId取**发生该事务的Session**；source取command。RuleWon改名LevelWon并加当前session.assisted与computeStars结果，RuleFailed改名LevelFailed，其余事实保留type/payload。StateCommitted含最终RuleState。示例：同为L01的第二个R，两Session只有assisted=false/true、attemptId/nextSeq不同，RuleWon事实均{used:2,par:2}；最终LevelWon分别assisted=false/stars=3与true/stars=2，其attemptId/seq由各自Session唯一决定。session-contract-vectors.json固定该反例。

Session专有事件：UndoApplied{restored:RuleState}；AttemptRestarted{previousAttemptId,newAttemptId}；HintConfirmed{assisted:true}；SaveDegraded{reason:QUOTA|SECURITY|TIMEOUT|IO}。UNDO恢复history与acceptedCommands并undoCount+1，assisted/nextSeq/totalAccepted不倒退。RESTART对旧attempt只使token失效，不再向旧局发事件；新attempt.nextSeq=1，新局发布AttemptRestarted(seq=1)，source仍为该重开command.source。空UNDO/终局UNDO仅本地解释，无状态事件。SaveDegraded由Controller接收adapter失败后发，source=system；一次相同故障只提示一次，恢复后再失败可重发。

VIEW_LAYER/InspectCell/暂停覆盖层焦点是Presentation通知，不套此SessionEvent信封；应用级BOOT/SDK状态有独立生命周期通知，不虚构不存在的levelId。SessionController控制pauseReasons和平台gameplay状态翻转，映射只发允许字段。P01构建不注册网络遥测订阅者；本地富事件及attemptId从不开发者回传。P02也只映射获准平台SDK事件，不能整个event payload上传。

## owner与集成

T03规则工程师独占rules/、session/与tests/rules、tests/session：RuleCore、SessionReducer、SessionController、EventBus接口。Controller依赖注入内容/纯commitWin/存储/平台能力；T03用测试替身，不反向import未建好的UI或SDK。T08交SaveCodec/T09交纯ProgressReducer；T07在依赖T03/T08/T09后负责app/CompositionRoot、AppStateMachine、唯一正式Boot.scene及meta，注入真实模块。T02只拥有独立BuildProbe.scene及meta，不写Boot。T10/T11只交adapter，不能另建Session总线或启动场景。

Boot顺序：构造唯一Controller→校验内容→选编译profile并初始化adapter→恢复合法存档→进入HOME；只有玩家开始/继续才PLAYING。重复SDK ready/超时迟回带bootGeneration，旧generation忽略；不第二次构造Controller/创建局/结算。T07集成验收检查一个Boot根节点、一个Controller、一个订阅注册/销毁对，T12测真实资源与生命周期。tasks的required_artifacts与write_scope可离线逐项验证唯一owner，**当前没有生成上述源码或场景**。
