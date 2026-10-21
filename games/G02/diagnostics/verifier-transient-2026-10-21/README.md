# G02 冻结校验器一次性失败诊断

2026-10-21 19:26 +08:00。供主线程、Jason、Hypatia引用；仅新增本诊断目录，没有修改冻结源码、JSON、布局、原报告、manifest或ZIP，没有重新打包。

结论：**5次独立副本/新进程重复全部退出0、PASS；19:23错误未复现，原因UNKNOWN。** 不据此宣称原错误没有发生，也不归因于环境、解释器、硬件或探针污染。未识别可定位源码缺陷，因此不提猜测性补丁。

原事故以主线程validation/G02-transient-failure.json为准，本目录保留root-transient-failure.snapshot.json。19:23在ablation的solve(baseline)→step→actions中发生TypeError，原调用栈没有局部变量/内存快照。主线程19:24未改源码重跑PASS，原G02-verifier.log已被成功日志覆盖；不把当前日志误当19:23原始日志。

本次从冻结ZIP逐成员读出5份独立副本，每份启动前核对37个包内成员hash；使用当前Python3.11.15/jsonschema4.26.0、PYTHONUTF8=1，以新进程运行与root validator相同的`python -B <副本>/tools/verify.py --all`。5次分别约4.53/4.47/4.50/4.46/4.58秒，stdout、stderr、逐次verification报告和时间见diagnosis.json及run-1…5文件；没有第6次完整verify。

另有一次轻量命名空间检查，只import冻结副本并调用rule_vectors()，不执行完整verify。31向量PASS；调用前后模块全局名称、actions函数/代码对象、builtins.enumerate身份及输出均相同，没有全局enumerate覆盖，trace/profile均None，见namespace-probe.json。代码顺序亦可核：报告的ablation失败点在verify()构造返回值、调用rule_vectors()及其exec变异探针之前。此事实与本次未见污染不能解释或否定原始一次性错误。

诊断前后39个冻结文件SHA256全部一致。ZIP仍为`9b541c8b76bae1030fb7fa81ae65afe782662e3bc10b98f21313d9df6a8c3241`；诊断是包外补充记录，不纳入已审ZIP，不使原审计失效。独立原六项修复结论不由本诊断改写；对标核心证据MAJOR仍保留，不因此签Ready或声称游戏构建/运行时通过。

按主线程限定，停止继续重复或扩展排查。资料交付可披露本记录，最终综合结论由主线程和独立审查者确定。若以后自然复发，应先保留失败副本、完整stderr/JSON、Python可执行文件hash，并在现场采集actions帧的i、sealed、stacks以及enumerate解析来源，再决定是否存在最小源码修法；本轮没有这些原始现场数据，不编造根因。
