"""Render the final preparation report from actual audit and validation records."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8'))


def main():
    validation = read('validation/preparation-report.json')
    if validation['result'] != 'PASS':
        raise ValueError('Resolve preparation artifact errors before final delivery')
    status = read('data/preparation-status.json')
    priority = [g for g in status if g['id'] in {'G01', 'G02', 'G04'}]
    if any(g['audit_verdict'] not in {'GO', 'REVISE', 'KILL'} for g in priority):
        raise ValueError('Independent decisions are not final')
    sources = len(read('research/official-sources.json'))
    claims = len(read('research/claims.json'))
    cards = read('research/benchmarks/benchmarks.json')['benchmarks']
    deep = sum(isinstance(c.get('deep_analysis'), dict) for c in cards)
    ready = [g['id'] for g in priority if g['ready_for_build']]
    readiness = ('可施工档案：' + '、'.join(ready) + '。开发仍等待项目选择及档案版本批准。' if ready else
                 '本轮没有无条件 READY_FOR_BUILD 项目。三套档案已交付并经审查；未关闭的证据问题见逐项审计，不能用数据校验替代。')
    rows = ['| 项目 | 独立裁决 | 未关闭 BLOCKER / MAJOR | 结论与依据 |',
            '|---|---|---|---|']
    for g in priority:
        note = g['decision_note'].replace('|', '／').replace('\n', ' ')
        rows.append(f"| {g['id']} {g['title']} | {g['audit_verdict']} | {g['unresolved_blockers']} / {g['unresolved_majors']} | {note} [审计](reviews/{g['id']}-audit.md) |")
    report = f'''# AI Game Foundry｜准备阶段交付报告

日期：2026-10-21，Asia/Shanghai。已完成原包 PROMPT_01—03 的研究、P0档案、独立审查及本轮修订交付。裁决可以是 REVISE；这不等于游戏已获批或全部外部证据已经取得。原包 PROMPT_04 留作选定项目后的实际开发阶段。

## 已交付

- 六渠道官方档案：{sources}个官方准入/技术/商务来源、{claims}条带来源定位和指标定义的论点，保留访问记录、差异及权利边界。
- 每渠道4张具体作品卡、2份深析，合计{len(cards)}卡/{deep}析。12份深析均标记为间接重建；后补浏览器操作另存带时间、命令、截图及hash的记录。
- G01/G02/G04各13份00—12施工文档、机器规格、任务DAG与Schema，各20关初态/目标/解序列，合计39份主体文档、60个正式关卡。实验关与正式关分开。
- 另外七家族均交付具名候选、来源、原创假设、停止线及家族特定研究缺口；不是七套完整GDD，也没有伪造其机器规格。
- 10×6渠道适配矩阵、组合成本模型、共享机制边界、许可证及合同冲突研究。
- 非作者独立审计、可修缺陷的修订及复核记录、离线总览与可重现检查/打包脚本。

## 逐款裁决

{chr(10).join(rows)}

{readiness}

作者不能代签自己的独立审查。首轮Finding、当时文件快照、反例和复核结论都保留；应以审计末次复核及 `reviews/decisions.json` 阅读当前未关闭项。

## 实际验证与未取得的证据

`validation/preparation-report.json` 的 **PASS** 仅指准备产物：文件结构、来源关系、UTF-8/JSON、Schema、任务DAG、60关离线验解、独立裁决一致性和操作截图hash。三款作者的有限规则模型还由非作者独立实现交叉核对，详细范围及边界见审计。没有把无解与验证护栏漏检混为同一问题。

封装复查曾出现一次G02 TypeError及两次异常进程退出，期间5个隔离新进程均PASS；没有修改冻结项目源码。最终以已有Python3.13.3、工作区内隔离副本和faulthandler完成综合PASS。配置多项变化，根因仍UNKNOWN，成功检查不能解释或抹去前面的异常；环境、失败摘要和次数见 [执行诊断补记](validation/G02-execution-diagnostic-summary.md) 及 [完整时间线](validation/verifier-execution-history.json)。这是离线检查执行诊断，没有据此断言游戏运行时缺陷。

离线总览另以1440×1000、768×1024和390×844检查10项目展示、P0筛选、文档弹层、本地链接、横向溢出及脚本错误，结果见 `validation/ui/report.json`。这是资料总览验证；不是三款游戏的移动适配或真机验收。

对标实际取得和未取得的节点见 `research/observation-summary.md` 及 `research/playthroughs/`。有效输入、加载尝试、官方规则重建与UNKNOWN各自标记；离散截图和页面驻留时间不替代连续首30秒/5分钟记录。没有以评分、历史下载或发行商案例推算新作收入或成功率。

没有执行游戏引擎构建、真人盲测、真实留存/收入实验；没有投稿、对外商务联系或签约。本团队准入资格、实际合同、报价、净回款、买量预算和市场竞争效果仍未取得。后续可先按审计节点补证，再由用户选择游戏ID、档案版本和实验预算；未取得的数据不填行业均值或假零值。

## 阅读、复查与打包

先打开 [离线总览](index.html)，再看 [要求与交付对照](REQUIREMENTS_CHECKLIST.md)、[独立审计索引](reviews/README.md)、[实际操作汇总](research/observation-summary.md)。原输入的 `projects.json` 状态保留；当前结果以 `data/preparation-status.json` 为准。

Python依赖见 `requirements-research.txt`。从根目录运行：

```text
python tools/validate_preparation.py
python tools/finalize_status.py
python tools/write_delivery_summary.py
python tools/build_delivery.py
```

在线来源重核另运行 `python tools/recheck_sources.py`；浏览器总览复查运行 `node tools/check_offline_index.cjs`，需已有Playwright和Chromium，环境路径可配置。更改验证/UI记录后重跑打包以纳入最新文件。

最终ZIP位于 `deliverables/AI_Game_Foundry_Prepared_2026-10-21.zip`。内部 `manifest.json` 列逐文件SHA256，外部 `deliverables/archive-verification.json` 核对ZIP CRC、成员集合及全部内容hash。原始长网页回执raw、浏览器运行缓存runtime和临时文件排除在ZIP及离线文档载荷之外。截图只作研究证据，不能作为自有产品素材。
'''
    (ROOT/'DELIVERY_REPORT.md').write_text(report, encoding='utf-8')
    current = f'''# STATUS

日期：2026-10-21（Asia/Shanghai）。当前阶段：PREPARATION_DELIVERED。

## 已完成

- 原包范围保持：P01—P06、G01—G10；输入/原演示保留，当前产物单列。
- {sources}个官方来源、{claims}条论点，六渠道档案、10×6适配矩阵、权利/许可证/组合成本及差异核对。
- {len(cards)}张作品卡、{deep}份明确标注间接重建的深析；后补实际操作及受阻记录独立归档。
- G01/G02/G04各13份施工文档及20关机器数据、任务DAG、Schema、验解器；三套非作者独立审计及修订复核。
- 七个非P0家族的候选研究与明确研究缺口；不将其称为完成GDD。
- 准备资料结构/数据校验PASS；离线总览多视口检查和ZIP逐文件校验另有报告。

## 当前项目状态

{chr(10).join(rows)}

{readiness}

## 未完成的后续阶段

真实玩家体验、引擎/真机、SDK集成、市场指标、外部合作/合同/报价与回款均未验证。对标未取得的流程节点和完整时间窗继续标缺；不填成已实玩。未执行PROMPT_04。

## 下一动作

按独立审计的未关闭证据节点补证；之后选择游戏ID、档案版本和实验预算，才进入实际开发。具体文件与边界见 [交付报告](DELIVERY_REPORT.md) 和 [要求对照](REQUIREMENTS_CHECKLIST.md)。
'''
    (ROOT/'STATUS.md').write_text(current, encoding='utf-8')
    print('Wrote final report and STATUS from audited records; no development authorization implied.')


if __name__ == '__main__':
    main()
