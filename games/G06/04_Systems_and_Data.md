# G06｜Systems_and_Data

SPEC_NOT_COMPLETE · RESEARCH_SKELETON · 2026-10-21 · ready_for_build=false。当前只交研究问题与验收方法，未完成该施工模块。

## 本家族待研究问题

车辆/轮胎/货物/约束/机关怎么建模？同tick接触损坏与抵达如何裁决？重放需要保存哪些物理状态？

## 补完时必须提交的验收证据

引擎中立实体与事件表、单位制和碰撞层；定义同构建重放范围及跨设备容差，不能声称seed使所有物理平台完全确定。

## 当前空缺与阻断

BLOCKER：状态、判定优先级、随机及回放契约缺失。

参考页证据只能支持[01_Market_Evidence.md](01_Market_Evidence.md)的对应陈述；不能把其说明当成本模块的实测结果。原创变体按[00_Project_Charter.md](00_Project_Charter.md)中的 HYPOTHESIS 单独核验，停止条件见[12_Falsifiability.md](12_Falsifiability.md)。
