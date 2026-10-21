# G01 开源、素材许可与权利清单

取证日期2026-10-21。此为交付前研究，不是已完成的法律审查或最终SBOM。网页许可不能覆盖未识别的具体文件；不下载对标源码、美术、音乐、角色或关卡。运行引擎、编辑器、SDK、字体、研究工具分别登记。

| 组件/来源 | 精确许可URL与本轮访问 | 可考虑的使用/义务 | 锁版与限制 |
|---|---|---|---|
| Cocos engine v3.8.8 | [LICENSE.md](https://raw.githubusercontent.com/cocos/cocos-engine/v3.8.8/LICENSE.md)，E12成功 | MIT；保留copyright与许可；可考虑商业运行时 | 引擎tag不等于Creator安装包或第三方依赖。此前`LICENSE`路径404，已纠正为LICENSE.md；最终引擎文件hash待锁 |
| Cocos Creator编辑器 | [官方下载](https://www.cocos.com/en/creator-download)，E11成功；猜测legal URL失败 | 选择3.8.8作为候选工具 | **EULA UNKNOWN**；T03需读取安装附带许可/当前官方协议。不得把MIT引擎许可套用到编辑器、云服务或商店素材 |
| TypeScript编译器 | [官方LICENSE](https://raw.githubusercontent.com/microsoft/TypeScript/main/LICENSE.txt)，E14成功 | Apache-2.0；分发工具/改动时带许可、保留适用NOTICE/修改声明；一般仅构建时使用 | main只证当前许可，候选Cocos随附TS确切版本未锁；锁版时对该版本重核；不是TS版本测试 |
| Noto Sans CJK SC候选 | [官方Sans/LICENSE](https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/LICENSE)，E13成功 | OFL-1.1；允许随软件嵌入，附许可与版权，不能单独出售字体；修改/子集核对保留名要求 | 不采用错误的googlefonts根LICENSE路径（404）；实际字体、字重、子集产物/工具/hash未取得；不得外链加载 |
| Python jsonschema | [官方COPYING](https://github.com/python-jsonschema/jsonschema/blob/main/COPYING)，E15成功 | MIT；本轮数据验证工具，运行环境4.26.0 | 未随ZIP打包第三方库；锁版requirements记录版本；最终生产无此运行依赖；环境版本对应源码hash尚未锁 |
| 数据求解算法 | 本包tools/validate.py，独立编写；深度/广度搜索与位掩码的通用思想 | 不借用外部实现，记录本项目作者来源；可供审计复验 | 本脚本为研究验证器，不直接当最终游戏源码；未来TS独立实现后比较向量 |
| 原创关卡/图标/声效 | 关卡初态本包自拟；06的美术音频待生产 | 登记制作人员、日期、源文件、委托授权/IP归属、hash | “AI生成”不是许可，不能假定不存在相似商标或侵权；未制作资产不能标RIGHTS_CLEARED |
| CrazyGamesSDK / PlaygamaBridge / P05 SDK | E03/E04为准入说明，不是完整软件许可 | 只在对应渠道构建使用，经实际协议许可后锁定版本 | SDK条款、域名、数据职责、再分发权、撤回条款均需另查；不把免费SDK称MIT/无条件跨平台许可 |

可用GitHub候选仅引擎/编译器/字体/验证工具的官方仓库。没有采购/采用第三方箭头游戏模板，也不把开源游戏仓库里的图片音频视作自动可商用。本项目体量不需要寻求不明许可的整套解谜源码。

## 维护与来源状态

3.8.8官网有版本记录，网页存在不保证未来维护、无漏洞或对P04旧系统兼容。TypeScript/Noto/jsonschema主分支页面本轮可读，但没有统计最近commit频率、漏洞或响应时间，**维护活跃程度UNKNOWN**，不写“持续维护良好”。施工前固定tag/commit、重核许可证与依赖、记录已知问题；禁止从随手fork或压缩转载下载引擎。

## 交付时的逐文件清单

每条资产/依赖应有：`asset_id,path,source_url,version_or_commit,sha256,author,copyright_owner,license_id,license_file,modification,attribution,territory,redistribution_scope,contract_id,review_status`。原创项source_url填`INTERNAL_ORIGINAL`而非伪外链，附源工程。当前素材生产为NOT_PRODUCED，合同为UNKNOWN，审查状态不得填CLEARED。

最终发布应有离线`THIRD_PARTY_NOTICES`与原文许可，CREDITS可读，不依赖外部网站。P01既禁外链/开发者回传，游戏内许可采用离线正文与名称，不放可点击URL/邮箱；完整来源URL保留在发行档案中供审核，不作为玩家出口。

## 不可接受的权利条件

买断仅能谈具体游戏IP和约定资产。通用规则接口、制造流程、未专属化工具与其他家族内容必须列明保留；运行所需通用部分给必要运行许可，不能默转全部工厂资产。若合同要求转让整个shared机制库、无限免费定制、来源不明资产担保、不可撤回超范围转授权，暂停签约并按11/12判断停止。所有条款需当前正文与专业审查，网页营销不是合同。
