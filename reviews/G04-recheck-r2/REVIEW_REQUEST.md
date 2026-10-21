# 给独立审计Agent的只读交接

请仅阅读本目录完成审计，不读取原对话或依赖根目录上下文。游戏ID G04；spec1.0.0；状态REVISION_REQUIRED（r2修订待独立复核），ready_for_build=false。本轮交付只含准备资料与离线规格验证，不应生成最终游戏源码、上架、发邮件或签约。原独立审查者Hypatia的权威报告位于F:/CoCreateGame/reviews/G04-audit.md/json（本目录相对../../reviews/G04-audit.md/json）。作者本轮只读该报告，不代签；T00回写仅这两个文件，见tasks。

建议读序：README → 00/01/02 → 03/04/game-spec → 05/06/07/08 → 09/tasks → 10/11/12 → SELF_REVIEW。Schema、qa-vectors、validator、validation-report和evidence-register供可重核。首次复述请先独立作答，再参考作者自查，避免把自查当通过结论。

## 要求独立复述

1. 玩家从首次进入到首胜/首败、复玩、解锁、退出和回归的全部输入和屏幕是什么？有哪些目前没有真实观察？
2. 正式B0与G01的核心决策差异是什么？哪些来自官方事实，哪些仅原创HYPOTHESIS？
3. 用一个位型与两扇互补门解释移动/X/开关如何结算；门、开关、升降、出口可否同格？
4. 目的格按哪个bits预检？旧pending、新开关、脚下关闭、信标、目标、预算的严格先后是什么？哪种错误不扣步？
5. X1/X2分别改了什么？关掉实验能否恢复同几何B0？空等/碰墙能否推进延迟？
6. FAILED/WON能否撤销？assisted、星级、完成记录各如何回滚/保留？出错存档与更新关卡怎么恢复？
7. 哪个模块唯一写RuleState？事件/动画/SDK重复回调如何避免重复结算？接口参数足不足以独立实现？
8. 是否能只用JSON重建全部20关？合法解、par与预算是否一致？是否有绕过教学的捷径或未定义死局？
9. 每屏、触控/键盘、色形、pending、音画清单是否还有让工程师必须猜测的地方？
10. P01网络/外链/广告禁令，P02无SDK Basic全包50/20MB与Full SDK、250MB/1500文件、PEGI-12/儿童定向排除是否被正确分包？P04未来条件是否禁GA4？
11. 任务DAG是否无环/有清楚批准门？源码/素材许可、排他/转授权/底座保留、真实净回款缺口是否明确？
12. 有哪些证据能反驳本项目、导致修订或淘汰？哪些测试实际跑过，哪些不能称已验证？

## 重跑与交付报告

在本目录运行 `python -B validate_spec.py`，现有依赖Python3.11+、jsonschema4.26.0；依赖缺失请报告，不把无法执行写成通过。验证会更新本目录report，先保留原件hash以便对照；若需严格只读，用原report与脚本审查或在获准副本运行。pack-preparation.py可在目录内重建ZIP，审计通常不必重打包。

返回：总体结论（可继续准备/REVISION_REQUIRED/建议KILLED）、独立复述、逐条BLOCKER/MAJOR/MINOR（文件/字段/反例/影响/修复验收）、验证命令与实际输出、未测项。不要因为档案数量齐全直接给READY_FOR_BUILD；任何语义阻断均需改版重验，游戏ID及施工批准仍由人类决定。

初次独立审计已发生且结论REVISE；本文件当前请求r2独立复核，不能据此声称复核已通过。

## r2定向复核输入

M02：04、EVENT_CONTRACT、event-contract.schema、session-contract-vectors、tasks的required_artifacts；检查RuleFact不依赖Session、富化来源、预留seq与一次提交、唯一发布者、Boot写域及依赖。M03：SAVE_CONTRACT、save-envelope.schema、save-fixtures、validate_contracts；检查所有字段/默认/边界、单Settings权威、CJ1 UTF8字节/中文SHA、失败UNDO、坏档/未知版/冲突/内容更新分支。M01：02的P00—P22与observation-index钉住外部研究；局部观察真实但连续30秒/5分钟仍缺，不求作者代关。minor1复算06六种几何；minor2读05四对同解与20题删门；minor3检查T00精确外部路径与schema。主控已闭合的campaign语义与TS4.1.2未回退。

SELF_REVIEW是未读后补证的历史快照，当前状态读STATUS；现行hash读validation-report.input_sha256，ZIP读archive-verification。若独立审计必须零写作者目录，请复制本包载荷至自己的获准审计沙箱再跑验证，或只读核对现有报告hash；不要在作者目录重写报告。复核不得把T02以后尚未获批的引擎/真机测试一概当准备规格不可实现，也不得把缺市场/实际试玩证据变成PASS。
