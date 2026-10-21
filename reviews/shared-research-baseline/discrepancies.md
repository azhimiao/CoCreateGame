# 本次重核与原包差异

访问日期：2026-10-21。总纲保留为历史基线；本文件和 `research/claims.json` 记录补充/修正，不把旧说法偷偷覆盖。

| 编号 | 原有或容易误读的说法 | 本次核查后采用 | 证据与工程影响 |
|---|---|---|---|
| D01 | CrazyGames至少7天且500次才结束，容易误认为不足500永久延长 | 不足500 plays最迟21天结束；plays不是unique players | [Basic指南](https://docs.crazygames.com/resources/basic-launch-metrics/)，C04；独立记录天数与plays |
| D02 | 六家商务条件均未公开，可能把所有分成写UNKNOWN | Playgama公开两种分成流：合作站点分发月净收入分段，与站内/iframe固定比例不同；仍非净回款 | [支付FAQ](https://wiki.playgama.com/playgama/faq/payments-and-statistics.md)，C20/C21；净额定义及流量仍未知 |
| D03 | CrazyGames没有公开结算门槛/账期 | 官网有100欧元最低结算、合同NET60；较早处理是目标，非到账保证 | [Payouts](https://docs.crazygames.com/payouts/)，C06 |
| D04 | TapNation约两周评估，可能被写成统一反馈保证 | publishing页称两周评估，submit页称7工作日回复；响应与完整评估不是同一指标，暂不合并成SLA | [流程](https://www.tap-nation.io/publishing/)、[表单](https://www.tap-nation.io/submit/)，C25/C27 |
| D05 | TapNation概念阶段可投，因此可假设无数据直接填写 | 现表单标收入、D1、平均时长为必填；未测只能如实未测，不能捏造0%/行业值，是否允许N/A待确认 | 同D04表单；概念准入不等于字段兼容已证实 |
| D06 | Playgama适配列表含Poki/CrazyGames，可认为自动发行 | 官方明确不代投这两家，SDK支持和审核发行分开 | [Welcome](https://wiki.playgama.com/playgama)，C16；不出同时混装SDK构建 |
| D07 | 通用统计抽象可以统一回传自有服务器 | Coolmath禁止回传；Playgama禁止嵌GA4等统计；Poki默认阻止外部请求 | C02/C13/C18；研究QA仅离线，渠道构建按白名单 |
| D08 | 同一网页UI无差别可用各渠道 | Poki要求桌面16:9及多设备；CrazyGames允许竖屏桌面配侧边背景并有包体限制 | [Poki要求](https://developers.poki.com/guide/requirements-quality)、[Crazy技术](https://docs.crazygames.com/requirements/technical/) |
| D09 | Azur Block/Arrow/Sort是3个具名发行作品 | 原JSON明确它们只是品类占位；由本次P05真实具名目录卡替代作证据，保留原JSON为输入基线 | `research/benchmarks/P05.md`；不能推断品类采购承诺 |
| D10 | AI作品被Poki全面禁止 | 官网允许审慎AI辅助，拒绝缺乏原创/低质/未测内容，并可能要求创作过程记录 | [内容政策](https://developers.poki.com/guide/content-player-safety)，C12；保留人工编辑及来源账本 |

未查到的金额、签约条款、真实收入、实际回复、玩家留存继续UNKNOWN。更具体的公开条款优先于笼统旧摘要；签约时实际协议优先于宣传页。
