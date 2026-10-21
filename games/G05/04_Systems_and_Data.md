# G05｜Systems_and_Data

SPEC_NOT_COMPLETE · RESEARCH_SKELETON · 2026-10-21 · ready_for_build=false。当前只交研究问题与验收方法，未完成该施工模块。

## 本家族待研究问题

输入缓冲、土狼时间、台面/危险/开关事件以什么tick判定？关卡复位如何避免重复机关？

## 补完时必须提交的验收证据

输入/碰撞/触发事件先后表与同帧冲突例子；列可回放的状态字段、复位事务和版本要求。缓冲等数值须标自有设计并另测。

## 当前空缺与阻断

BLOCKER：tick、碰撞形状和事件顺序未定义，不制造GameSpec。

参考页证据只能支持[01_Market_Evidence.md](01_Market_Evidence.md)的对应陈述；不能把其说明当成本模块的实测结果。原创变体按[00_Project_Charter.md](00_Project_Charter.md)中的 HYPOTHESIS 单独核验，停止条件见[12_Falsifiability.md](12_Falsifiability.md)。
