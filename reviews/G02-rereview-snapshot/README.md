# G02 完整准备交付包｜签章收纳台

2026-10-21｜版本1.1｜**REVISION_REQUIRED / PENDING_RE_REVIEW / ready_for_build=false**。

本包是准备施工档案，不是可玩游戏。00—12共13份文档、game-spec/tasks及各自本地Schema、20个原创关卡与完整合法解、离线验证脚本和实际报告齐备。全部写入限定games/G02，未修改根/共享STATUS或其它项目；无最终TS游戏源码、Cocos工程、Web构建、APK、对外投稿/邮件/合同。

## 阅读入口

先读STATUS.md与REVISIONS.md：独立首审REVISE，六项作者修订待同一审查者复核；不是GO。再按00→01→02确认范围与证据，03→04确认玩法/接口，05核对20关，06看11屏/资产，07—10看工程/许可证/任务/测试，11—12看发行与证伪。`game-spec.json`中的初态/胜利条件/solution可机器读取。文件`05_Levels_Economy.md`与其同源导出。

对标为Good Sort Master: Triple Match与TapNation的Color Water Sort Puzzle Games，均通过官方web说明研究；**作者初轮未实际试玩**，官方说明间接重建，30秒/5分钟真实轨迹UNKNOWN。原创机制/关卡/预算/玩家指标均HYPOTHESIS；形式验证不能替代体验验证。

## 复核命令（离线）

依赖Python3.11+、jsonschema4.26.0（requirements-preparation.txt，当前环境已具备）。从根目录：

```powershell
python -B games/G02/tools/verify.py --all
```

从任何目录用绝对路径：

```powershell
python -B F:\CoCreateGame\games\G02\tools\verify.py --all
```

报告`verification/verification-report.json`明确overall_status、输入hash、环境、20关最短解/逐步hash、31个规则/抽象输入向量、19节点DAG、9组协议表、5组静态布局、渠道门禁隔离和两项消融。异常会写FAIL及traceback并退出1。原先主控空stdout失败反馈未在本机重现；主控已确认根validator复核PASS。以**当前输入hash+退出码+报告状态**为准，不读旧报告冒充本次成功。

如需从作者数据重建（通常审计不必）：在本目录依次`python -B tools/author_data.py`、`python -B tools/render_levels.py`、`python -B tools/verify.py --all`。只生成研究JSON/Schema/表格，没有游戏代码生成。不要在本轮运行不存在的npm/Cocos构建；这些未来验收命令均标NOT_RUN。

## 压缩包和完整性

`G02_Preparation_2026-10-21.zip`是交付包，根目录为`G02/`。`package-manifest.json`列全部载荷SHA256，ZIP/manifest本身不递归收录；`verification/package-check.json`记录ZIP可读、内容逐字节相符、CRC/hash检查与实际大小。重新打包：

```powershell
python -B tools/package_delivery.py
```

脚本先复验规格，再检查13文档和必需文件、建立manifest、ZIP、内存中回读全部成员；只写G02，排除ZIP自身、旧打包检查结果和__pycache__。打包不会构建/上架/联系外部。文件改动后必须重跑打包，避免ZIP过期。

## 审计门禁

独立首审已在共享`reviews/G02-audit.md/.json`给出REVISE，原件hash与六项修订证据见REVISIONS.md（本Agent不写审计目录）；详见INDEPENDENT_AUDIT_REQUEST.md。SELF_REVIEW是作者自检，**不是独立审计**。真实阻断：独立修订复核、人类施工批准、实际对标操作、未编译工具链、真人理解/体验、移动SDK条件/合同、最终资产清权。Cocos/移动包体/FPS/收益均未验证；不擅自READY，不自动开始开发。

项目状态以STATUS.md为入口，HANDOFF_STATE同步简表；根STATUS及其它项目目录未修改，主控须依据此真实状态同步根索引，不能继续显示首轮SPEC_DRAFTED或当作已GO。protocol-vectors.json是注入判决的离线协议表；layout-cases.json只验证CSS矩形/文本预算，均不等于游戏运行验证。

团队同日浏览器补证单列于02第5节/STATUS：GoodSort未确认棋盘、ScrewOut末帧Level1，但核心输入0；13截图hashPASS不等于核心实玩。下一接收者为同一独立审查者Jason。
