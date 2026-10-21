# G04｜折光机关 Layer Relay｜准备交付

冻结日2026-10-21；spec1.0.0；P0批次；候选P01 Coolmath、P02 CrazyGames。状态 **INDEPENDENT_REVIEW**，`ready_for_build=false`。所有原创规则/关卡/体验与收益预算为HYPOTHESIS。未开发最终游戏，未创建Cocos项目，未投稿/发信/签约，未修改本目录外文件或根STATUS。

## 产物与读序

00章程、01官方证据、02对标间接流程、03完整GDD、04系统/接口/存档、05二十关/经济、06每屏UI/音画、07技术/平台分包、08许可、09任务计划、10QA、11发行合同、12证伪，共13份实质文档。

`game-spec.json` / `tasks.json` 与本地 `game-spec.schema.json` / `tasks.schema.json`；`evidence-register.json`（官方URL/2026-10-21访问/证据类型/口径/反证）；`qa-vectors.json`（21条固定预期）；`validate_spec.py`（纯离线规格核对）；`validation-report.json`（实际运行结果、hash和逐步trace）。

SELF_REVIEW是作者自查，REVIEW_REQUEST供另一个Agent只读本目录盲审。当前未发生独立审计，不把自查冒作通过。

## 实际验证与重跑

已有环境Python3.11.15/jsonschema4.26.0，依赖版本在requirements-spec.txt。命令：`python -B validate_spec.py`。

两份Schema验证、20正式关+2实验夹具验解及最短步、21固定规则向量、4个Schema负例、16任务DAG均通过；两个同几何B0对照另验解。X1为9步/对照5步；X2为9步/对照7步，只说明规则差异，不是体验提升。

官方参考为Bloxorz、Liquid2、PaintMaster；本轮依据官方说明间接重建，未实玩，首30秒/5分钟均UNKNOWN。Cocos3.8.7版本已查官方，PATH未检出命令，安装状态UNKNOWN；没有运行引擎、TS、浏览器/真机、玩家实验或平台审核。

## 压缩交付

`G04_Preparation_2026-10-21_v1.0.0.zip` 内含整个准备交接所需文件，根目录为G04/；不包含zip自身、虚构游戏包或最终源码。`DELIVERY_MANIFEST.json`记录每个载荷文件bytes/SHA-256，`archive-verification.json`记录ZIP的CRC/成员与哈希核验和外部zip SHA-256。

重打包：先 `python -B validate_spec.py`，再 `python -B pack-preparation.py`。后者会要求report的输入hash匹配当前文件，禁止把旧PASS报告打包成新验证。只在G04目录内写ZIP、manifest、验包报告。验包报告在ZIP外，避免循环hash；manifest在ZIP内外均有。

## 未关闭与下一步

BLOCKER：独立审计未完成；人类未批准G04具体施工档案。MAJOR：缺少直接对标试玩/玩家观察；难度排序未验证且L20存在短路线；Cocos/SDK/真机/实际包体未验证；完整许可/合同/报价/净回款UNKNOWN。详见SELF_REVIEW。

下一动作是独立Agent按REVIEW_REQUEST复述并找反例。档案修订后重验；是否READY_FOR_BUILD与是否施工由审计结果和人类决定。本轮不自动进入开发，也不因已完成ZIP宣称产品可发行。
