# 开源、算法与资产许可清单

访问日2026-10-21；“有开源仓库”不代表其演示美术、字体、音乐、编辑器或所有依赖都可商用。本轮未复制任何参考游戏代码/地图/图像/音乐，未安装Cocos/TS，交付不含其二进制。需要的游戏规则未来自主实现；不寻找未审的Bloxorz克隆仓库作为捷径。

| 项目/URL | 已核许可/版本 | 计划用途 | 限制、维护与证据 |
|---|---|---|---|
| cocos/cocos-engine，https://github.com/cocos/cocos-engine/releases/tag/3.8.7 | E11：tag3.8.7的LICENSE.md为MIT | 未来2D运行引擎；本轮不分发 | 保存copyright/permission，逐项查third-party notices；官方有release不代表当前无漏洞/编辑器同许可 |
| Creator编辑器与Dashboard，https://docs.cocos.com/creator/3.8/manual/en/ | 完整编辑器/服务条款UNKNOWN | 获批后安装的制作工具 | 引擎MIT不能直接覆盖编辑器/商店/账号服务；T02安装时核条款，不把编辑器打进包 |
| microsoft/TypeScript，https://github.com/microsoft/TypeScript ，许可https://raw.githubusercontent.com/microsoft/TypeScript/main/LICENSE.txt | E12：Apache-2.0；语言兼容基线按E10的4.1.0 | 未来开发类型检查工具 | 发布/使用锁定版本再读取该版本LICENSE/NOTICE；保留需要的声明；main许可不代表版本级完整SBOM |
| python-jsonschema/jsonschema，https://github.com/python-jsonschema/jsonschema ，许可https://raw.githubusercontent.com/python-jsonschema/jsonschema/main/COPYING | E13：MIT；本机实际版本见validation-report | 当前离线规格Schema校验 | 未把库源码/venv打入ZIP；若以后复制库须保留许可/版权；传递依赖在打包时另审 |
| Python标准库，https://docs.python.org/3/license.html | 本轮使用系统已有Python；未打包解释器 | JSON/BFS/SHA/ZIP验证 | 不对Python运行时作重新授权；如嵌入分发需读取对应版本完整PSF及第三方条款 |

算法使用自写FIFO广度优先搜索与整数XOR，未复制论文/网站实现代码。算法思想不是对专有关卡表达的授权；关卡、教程、UI图标和源素材须独立撰写。`validate_spec.py` 是本项目规格核对工具，不含引擎运行、美术、交互或发行功能。它及文档/原创数据的对外许可由权利人决定，本轮未擅自发布公共开源许可。

## 素材与字体

06中的原创几何素材和合成音效目前只是施工清单，尚未制作，版权链状态为待建立。每项未来需assetId、作者/工具、制作日期、源文件hash、第三方输入、license URL/文本、允许商用/修改/再分发范围、署名要求、转授权限制。未知来源即拒收，不能以AI生成一词代替权利审查。外包交付需书面转让/许可范围及素材来源表，未取得不进入release。

默认系统字体，不下载/嵌入第三方字体包；在目标设备系统渲染中英，缺字或不一致由06的真机测试决定是否需要另审字体方案。系统字体存在不代表可将字体文件提取打包；不得拷Windows字体到游戏。

## 平台SDK与许可文本

P02 SDK具体版本及再分发条款UNKNOWN，T11接入前锁版本、源URL、hash和开发者协议；P01包剔除P02与其他广告/统计SDK。P04不在本项目候选包范围，其Bridge不得被默认装入，若以后获批依E07禁第三方统计。

P01 credits不允许URL/邮件/社交帐号，许可证声明仍必须完整合法保留。优先把必要版权/许可放独立非交互 `THIRD_PARTY_NOTICES.txt`，UI credits仅作者名，不设外链；若要求的原文含URL或平台对包内声明有异议，提交前向平台与权利人确认处理方式，**不为过审删掉强制许可文字**。这一边界当前未取得平台书面确认，应列发行MAJOR。

## 未来审计DoD

SBOM包含精确版本、锁文件hash、直接/传递依赖、实际使用文件及许可文本；区分制作工具与进入游戏的运行库。检查GPL/AGPL等义务是否与闭源许可销售冲突，不能未经审查引入；MIT/Apache也须履行相应声明。保留真实维护/安全评估日期，不能用本轮可访问页面当作“维护活跃且安全”的证据。最终资产销售合同明确保留通用工具，仅授游戏必要运行许可；任何买断不得自动扩展至本目录所有制作流程。
