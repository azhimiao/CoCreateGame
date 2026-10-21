# G02 独立首审修订索引

2026-10-21｜档案1.1｜作者修订完成、**待同一独立审查者复核**。这是修复闭合主张与定位，不修改独立审计、不代签GO。项目状态REVISION_REQUIRED/PENDING_RE_REVIEW，详见STATUS.md。

审计原件只读：reviews/G02-audit.md，SHA256 `91349070ca161418b34ec6efa2348f0cd2cdf6f5be9e8e777338057b0411a525`；reviews/G02-audit.json，SHA256 `0609491b80f2ad98d5ccc92fdd082ba0187520de653e0738c0a796f1cb84c1f3`。已完整读取两份；JSON列1B/2M，3项MINOR来自Markdown，不回填或篡改原件。机器修复索引revision-index.json。

| 审计ID | 修订与唯一行为 | 文件定位 | 实际准备阶段校验 |
|---|---|---|---|
| B-G02-01 | 身份/查重先于BUSY/STALE；精确重试不可变receipt，同ID异payload=ID_CONFLICT；消费后的失败也缓存；缓存0新增事件/保存 | 04§2.1、03输入、10 R16；game-spec.command_protocol | protocol-vectors的retry_identity_before_busy_stale_pause_win、final_seal_retry_in_win；每次缓存/传输拒绝比较全部探针状态无副作用 |
| M-G02-01 | v2恢复保留run/盘面/撤销/revision，换新epoch、seq从1；旧epoch迟回丢弃；数字128序号窗口与4096回放checkpoint独立 | 04§2.1/6/7、07/09 T05；JSON/schema | numeric_9_10、numeric_window_127_128_129、mixed_accept_reject_undo、restore_new_epoch_old_late_callback、checkpoint_4096_independent_of_cache、undo_history_127_128_129、typed_identity_no_string_sort；checkpoint后的首条就是UNDO |
| M-G02-02 | PLAY三列两行/小横屏六列，无滚动；安全区扣除后CSS尺寸不整体缩小；顶部/封箱/工具44；菜单SCROLL、按钮BUTTON、棋盘GAME唯一owner | 03§4、04§3、06§1/3/4、07 P04、10 UI；game-spec.ui.layout_contract | 5静态矩形与文本预算案例，含320×568→304×490/font1.3、568×320→490×304/font1.3；6盘/工具全在界内。实际字体/触控/门户预览未执行 |
| N-G02-01 | 异顶例[B],[A],[AB]容量2/有余量/全接收；满目标另用[A],[AA],[]同顶；真实SEAL→存快照→JSON往返→UNDO恢复/重锁、revision不回退 | tools/verify.py rule_vectors、10 R02/03/11 | 单因理由TOP_MISMATCH/TARGET_FULL、满优先顶色错误序；删除真实actions的same-top一条守卫后隔离例必须检出，不靠全关搜索失败；恢复物件/章/计数/锁 |
| N-G02-02 | L09/T4与L13/T3是可选机制展示；不把过关等同掌握 | 05教学、12研究问句；game-spec.levels.feature_coverage及schema | verify实际删掉可选盘，原完整解不引用该盘且仍逐步合法获胜；独立问何时开T4、T3能否封箱，不虚报教学覆盖 |
| N-G02-03 | T15仅P02/P04；P05 T13/T14/T18、P06 T16/T17/T19各自书面条件/原生QA/移动研究/权利/人类批准 | 07/09/11、tasks.json/schema | 19节点DAG；模拟网页门禁满足仍不能解锁移动，只满足P05仍不能解锁P06；当前真实verified_conditions全空 |

补充交付：新增STATUS.md，更新README/HANDOFF_STATE/00/审计交接入口及manifest状态，不再误示首轮SPEC_DRAFTED。团队同日浏览器观察在02§5和STATUS逐节点登记：13张截图完整性PASS但核心输入0，GoodSort棋盘未确认、ScrewOut仅末帧Level1，玩法/满槽/胜败重试/连续时间窗仍UNKNOWN；不回填作者初轮历史。源报告/hash索引在evidence/team-browser-observation-index.json，原截图仍保留共享研究目录。

复核命令：`python -B games/G02/tools/verify.py --all`；随后在G02运行`python -B tools/package_delivery.py`。报告记录真实离线结果与输入hash，打包检查记录CRC、逐成员相符、manifest SHA256及ZIP hash。Python探针只用注入判决和整数假状态，不是游戏运行时；静态布局不等于真实渲染；所有Cocos/SDK/真机/性能/实际核心试玩/商务仍未完成。
