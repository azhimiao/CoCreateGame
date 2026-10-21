# G02 开源、资产与权利清单

2026-10-21。只审核下列候选用途，本轮没有把第三方游戏源码/音画下载进成品。本目录原创文档、关卡及校验脚本未被擅自授予对外开源许可；所属权依用户/团队既有安排，不声称能转授第三方权利。维护“有官方版本/许可可查”与“已锁定可构建”严格分开。

## 1. 源码与工具候选

| 组件/用途 | 来源及许可证URL（均访问2026-10-21） | 条件与当前结论 |
|---|---|---|
| Cocos Engine 3.8.8，未来游戏运行时 | https://github.com/cocos/cocos-engine/tree/v3.8.8 ；https://raw.githubusercontent.com/cocos/cocos-engine/v3.8.8/LICENSE.md | MIT；保留版权与许可，第三方依赖逐项核；版本候选可查，未编译，不能把整个Creator说MIT |
| Creator编辑器，未来本地制作工具 | https://raw.githubusercontent.com/cocos/cocos-engine/v3.8.8/licenses/EDITOR_license_and_terms_en.txt | 独立编辑器协议，含闭源部分和工具再分发限制；本轮未安装/捆绑编辑器 |
| TS5.6.3，独立类型检查候选 | https://github.com/microsoft/TypeScript/tree/v5.6.3 ；https://raw.githubusercontent.com/microsoft/TypeScript/v5.6.3/LICENSE.txt | Apache-2.0；分发对应代码时保留许可/声明，修改留痕；版本存在不证明与Creator兼容 |
| Python jsonschema，离线工具 | https://github.com/python-jsonschema/jsonschema ；https://raw.githubusercontent.com/python-jsonschema/jsonschema/main/COPYING | MIT；本机实际4.26.0，依赖见requirements；未随游戏发布，不复制整个venv进ZIP |
| 本目录BFS/重放，原创离线校验 | tools/verify.py、tools/author_data.py | 自行实现有限状态广度搜索，未复制商业求解器代码；一般算法思想不等于采用某库源码 |

当前官方仓库可访问不等于维护响应/安全性保证；最后维护提交准确日期UNKNOWN，T03/T06再锁commit、依赖、包hash、安全公告。没有引入不明水排序开源项目、GPL/AGPL求解器或商业模板。无需为简单离散状态从参考游戏抽取算法实现。

## 2. 图像、字体、声音

字体候选Noto Sans SC，源 https://github.com/google/fonts/tree/main/ofl/notosanssc ，许可 https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/OFL.txt （2026-10-21访问，OFL-1.1）。随字体分发版权/OFL；字体不能单独出售；改名/子集遵守保留名称条件，别把字体自身改许可。字体许可证不替本游戏提供商标权。当前未打入字体二进制，子集源、hash和许可文本是T06前置验收。

图标、邮片、托盘、背景、Logo、音乐和七音效全部按06原创生产，当前未生产；不使用来源UNKNOWN素材。外包创作需书面商业使用、修改、再许可、衍生、跨平台与署名条件。自录音确认无第三方旋律/采样；若以后改用CC0或付费素材，逐个保存原URL/作者/许可快照/购买凭证/日期/hash，不能只写“来自免费资源站”。生成式素材如后续获准使用，保留生成服务条件与编辑来源，不能保证绝对不侵权；现阶段无生成图入包。

参考游戏URL用于研究，**不授予复制**源码、美术、音乐、人物、商品包装、具体关卡排列、宣传图或UI独特表达的权利。E01/E02官方截图不进入G02美术库或营销图；本轮ZIP只含文字说明，无商业游戏截图再分发。

## 3. 制造系统与合同冲突

游戏运行许可与“把Creator/引擎再包装成可再分发开发工具”是两类用途。E17对游戏开发工具再分发有条款限制；当前仅设计G02游戏，不能据引擎MIT推断AI Foundry工具平台可任意捆绑编辑器。若未来出售通用制造工具/可编辑模板/打包编辑器，须单独厘清协议和取得所需权利；不能把本游戏许可审查当整个公司工具许可结论。

发行合同中附表明确：本游戏专属关卡/音画/品牌可以按约许可；通用RuleCore、Schema、求解器、制造流程、第三方运行时版权应保留或仅授必要运行许可，不能承诺独占所有底层思想。买方要求完整源码时必须排除第三方编辑器、账号、SDK密钥和不能转让的素材；需给运行所必需的相容许可而非转让他人版权。

## 4. 最终发行前许可验收

T06填写每项台账：asset/component_id、版本/commit、作者、原URL、访问/创作日、原始文件hash、运行输出hash、许可标识、随附文本路径、修改说明、适用平台/地区/期限、是否可再许可、采购凭证。本轮只提供候选清单，实际条目/二进制为UNKNOWN，不标“全部清权”。

最终包应带`THIRD_PARTY_NOTICES.txt`及需要随附的许可原文，credits显示可阅读纯文本；当前文档包不捆绑这些候选运行库/素材，因此不能伪造已完成NOTICE。任何素材来源不明、合同要求超出许可、或同一权利被排他授出，停止该产物发布并REVISION_REQUIRED；不靠更换文件名规避。
