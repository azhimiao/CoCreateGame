# 当前发行候选检查｜120关旅程

2026-10-22。候选包不代表平台上线批准。

| 检查 | 状态 | 依据 |
| --- | --- | --- |
| 120关唯一几何、无技能全解、身体跟随 | PASS | campaign-levels.py --verify；48种合法随机顺序/关 |
| 规则、运动、技能历史、异常存档 | PASS | 36项单元测试 |
| 120关全部真实点选 | PASS（减少动态） | 3,268次真实蛇头输入，browser-report.json |
| 默认运动清盘 | PASS | 旅程12/60/108/120关；原五盘128条蛇 |
| 技能/解锁/分页/续玩/最佳星级 | PASS（浏览器） | campaign-smoke.cjs；取消/确认/撤销/刷新/重玩 |
| 八种移动视口/触摸章节滚动与选关/两种英文包 | PASS（模拟） | artifacts/mobile/report.json、release-audit.json、dense-browser-report.json |
| SDK与网络 | PASS（mock/本地） | Coolmath无网络；CrazyGames官方URL init/start；无广告 |
| 两页面、当前截图、真实动效录像、ZIP字节一致 | 已提供 | index.html + phase.html，delivery三个候选ZIP |
| 物理手机、多浏览器、盲测难度、名称检索 | 待完成 | 没有通过证据 |
| Coolmath平台SDK / CrazyGames实环境SDK / 平台审核 | 待完成 | 仅有本地候选和mock；未投稿 |

实际规则复核来源（2026-10-22观察）：https://docs.crazygames.com/requirements/technical/ 、https://developers.coolmathgames.com/ 。Coolmath平台有意向后需其简单SDK，当前等待该平台对接资料；具体权利条款仍须正式沟通确认。
