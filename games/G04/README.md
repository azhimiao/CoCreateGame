# G04｜折光机关 Layer Relay｜修订待独立复核

2026-10-21；spec/规则1.0.0，合同r2。状态REVISION_REQUIRED，ready_for_build=false。Hypatia已独立审计给REVISE；本包是作者修订，不代签GO，下一步交原审查者复核。当前状态见[STATUS.md](STATUS.md)，修复逐项见[REVISIONS.md](REVISIONS.md)。仅P01 Coolmath/P02 CrazyGames候选；未开发最终游戏或创建Cocos项目。

00—12共13份实质文档保持完整；game-spec/tasks及各自Schema为机器规格。新增EVENT_CONTRACT/SAVE_CONTRACT、event-contract.schema/save-envelope.schema、session-contract-vectors/save-fixtures，明确规则事实与Session元数据、唯一发布/Boot归属、完整存档/唯一Settings/CJ1规范字节。observation-index固定研究来源、64帧hash，02逐节点解释Paint Master局部真实输入；第三方截图留在外部研究目录，不作生产素材打包。

SELF_REVIEW是**未读后补观察、未收到独立报告的历史快照**；当前证据不能沿用其“全未实玩/未独立审计”描述。参考研究的Paint Master为PARTIAL，确认局部输入→单关成功→故意失败→菜单重开→再输入；连续首30秒/5分钟仍UNKNOWN，Bloxorz/Liquid2核心输入未确认。原创规则、体验、受众偏好与收益均HYPOTHESIS或UNKNOWN。

实际重跑：在本目录执行python -B validate_spec.py；依赖requirements-spec.txt，实际Python3.11.15/jsonschema4.26.0。原20+2关/21向量/两个B0对照、campaign负例及16任务DAG继续通过；新增完整存档/事件Schema、2合法/12损坏或迁移样本、严格JSON/双槽模型、不同Session富化、唯一owner、响应式几何与删门消融。Node20.11.0实际只做JSON/crypto字节hash核对。validation-report逐项记录结果与所有规格源hash，不是引擎或产品性能报告。

压缩交付：G04_Preparation_2026-10-21_v1.0.0.zip（内根G04/）。命令先python -B validate_spec.py，再python -B pack-preparation.py；manifest.status为REVISION_REQUIRED，并包含STATUS及所有新增合同文件。DELIVERY_MANIFEST记录载荷bytes/SHA256，archive-verification在包外记录ZIP SHA256、CRC/成员/所有载荷一致；不把准备包体当游戏包体。验证输入hash不匹配则拒包。

审计权威路径相对本目录../../reviews/G04-audit.md/json，即F:/CoCreateGame/reviews/G04-audit.md/json；T00只允许原审计员回写，作者不改。复核入口REVIEW_REQUEST。M02/M03与minor1/2/3为作者修复待审，M01只部分补证，不能凑READY。G04产品Cocos/TS/SDK/真机/性能/玩家/发行合同与收入未验证；安装状态UNKNOWN。人类尚未批准G04及施工档案，修订或审计GO都不会自动授权开发/投稿。
