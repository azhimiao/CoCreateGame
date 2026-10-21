# G03｜Systems_and_Data

SPEC_NOT_COMPLETE · RESEARCH_SKELETON · 2026-10-21 · ready_for_build=false。当前只交研究问题与验收方法，未完成该施工模块。

## 本家族待研究问题

物品实例与配方类别如何分离？合成、预留、交单是否同一事务？订单刷新时已预留物品怎样处理？

## 补完时必须提交的验收证据

实体/事件表、资源守恒式、交付幂等及拖放回滚例子；列生产器销毁和存档迁移反例。字段必须追溯到选定规则。

## 当前空缺与阻断

BLOCKER：缺类型、事务边界和存档版本，不生成 game-spec.json。

参考页证据只能支持[01_Market_Evidence.md](01_Market_Evidence.md)的对应陈述；不能把其说明当成本模块的实测结果。原创变体按[00_Project_Charter.md](00_Project_Charter.md)中的 HYPOTHESIS 单独核验，停止条件见[12_Falsifiability.md](12_Falsifiability.md)。
