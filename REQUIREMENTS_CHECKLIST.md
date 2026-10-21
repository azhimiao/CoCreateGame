# 原包要求与实际交付对照

以MASTER_HANDOFF第10节及PROMPT_01—03为范围；PROMPT_04是另行批准的后续阶段。日期2026-10-21。

| 要求 | 实际文件/证据 | 验收边界 |
|---|---|---|
| 六家官方准入、联系入口、合作和条款重核 | research/platforms/P01—P06、official-sources.json、claims.json、source-access-log.json | 24官方来源/30论点；公开页面可核，实际进入资格及协议仍未取得 |
| 每家3—5款具体作品 | research/benchmarks/benchmarks.json及P01—P06.md | 每家4张，共24卡；历史目录/评分/渠道版本日期各有口径 |
| 每家至少2款深度流程分析 | 同上的deep_analysis字段及文档 | 每家2份，共12份，均明确间接重建；按PROMPT_01替代路径研究，但完整实玩证据未取得 |
| 有条件时保存真实操作证据 | research/benchmarks/evidence/、research/playthroughs/G04/ | Drive Mad局部输入、Paint Master成功/失败/重试；其余受阻或未操作，0份完整连续首30秒/5分钟 |
| G01—G10独立候选档案 | games/各目录 | 十家族已建；非P0有家族特定研究问题，不将骨架当完整GDD |
| P0每款完整00—12及机器规格/任务 | games/G01、G02、G04 | 每款13份文档+2 JSON+2 Schema；各20关初态/目标/见证 |
| Schema和关卡/任务验证 | validation/preparation-report.json及各项目验证报告 | 60关验解、3个任务DAG、6份Schema；只证明指定规则/数据，不证明游戏已构建或好玩 |
| 独立反方审计及可反证条件 | reviews/及各12_Falsifiability.md | 最终逐项裁决以审计原文为准；可修缺陷修复后必须由审计员复核 |
| 平台适配/许可证/合同冲突 | research/adaptation-matrix.*、contracts-and-rights.md、各08/11 | 10×6矩阵完整；实际依赖资产/合同需要后续取得证据，未假报清理完成 |
| 最新差异、状态和交付入口 | discrepancies.md、STATUS.md、data/preparation-status.json、index.html | 原输入保留，当前状态分开；总览可离线浏览 |
| 可重复检查与完整文件包 | tools/、validation/、deliverables/manifest.json与ZIP | ZIP CRC及逐文件SHA256核对；排除raw、浏览器runtime和临时缓存 |
| 不自动扩范围或进入开发/商业操作 | DELIVERY_PROVENANCE.json | 仅P01—P06/G01—G10；未执行PROMPT_04、未提交、发商务消息、签约或采购付费SDK |

“交付结构与离线校验通过”和“可无条件开工/发行”是不同结论。尚缺外部观测的项目保持REVISION_REQUIRED或研究状态；不得为凑满数量自动给READY。最终审计若仍有规则/接口缺陷，应先修订；不是通过这张清单豁免。
