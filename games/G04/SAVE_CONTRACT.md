# G04 SaveEnvelope / Progress / Settings｜修订r2

本合同、save-envelope.schema.json和save-fixtures.json是同一权威规格；规则版本1.0.0。校验工具仅处理离线JSON，不实现浏览器双槽I/O。Settings只存在信封settings，Progress或ActiveSession出现settings一律SCHEMA_INVALID，不能静默择一。所有对象拒绝额外字段、重复JSON键和未配对Unicode代理项。

## 完整字段、默认值和边界

| 对象 | 完整字段 / 默认与限制 |
|---|---|
| SaveEnvelope | schemaVersion=1；ruleVersion="1.0.0"；profile为local-qa/P01/P02-basic-nosdk/P02-basic-sdk/P02-full；contentHash小写64位SHA256；revision=1..9007199254740991；updatedAt严格UTC `YYYY-MM-DDTHH:mm:ss.sssZ`合法公历时点；progress；settings；activeSession=null或下述对象；checksum小写64位 |
| Settings | sfx=true；music=false；reducedMotion=false；locale="zh-CN"（另可en）；contrast="standard"（另可high）。五字段都必需，默认只用于创建新档，不用于填补坏档 |
| Progress | records恰20条、严格G04-L01…L20顺序；highestUnlocked为1..20；lastCommittedAttemptId=null或合法attemptId。completed集合从records派生，不能另存一份 |
| ProgressRecord | levelId；completed:boolean；bestStars:0..3；bestUsed:null或1..128。未完成必须0/null；完成必须1..3/非null。记录是历史最高星与最低最终路线步数，可来自不同局；无每局奖励或货币 |
| ActiveSession | levelId；levelName（当前内容中文/英文原始关名、非玩家姓名）；variant=B0/X1/X2；attemptId形如a-加32位小写hex；assisted:boolean；nextSeq=1..MAX_SAFE_INTEGER；totalAccepted/undoCount=0..MAX_SAFE_INTEGER；acceptedCommands最多128项U/R/D/L/X；ruleState。不得存history或引擎/UI对象；恢复时重建history |
| RuleState | position:[layer0..1,x0..4,y0..4]；bits/pending=0..7；nextBeacon=0..6；used=0..128；status=PLAYING/WON/FAILED；failure=null/FLOOR_CLOSED/BEACON_ORDER/MOVE_LIMIT。只有FAILED时failure非null。ActiveSession的status只允许PLAYING/FAILED，WON已原子写进度且activeSession=null |

新档records全未完成，highestUnlocked=1、lastCommittedAttemptId=null、activeSession=null、revision=1，五设置用上表。revision每次**成功形成新保存事务**加1，不等于步数/事件seq；取当前有效最高值+1，同一待写快照重试用同revision。到MAX_SAFE_INTEGER不得回绕：保留最后有效档、转内存并提示需迁移，不自动清档。updatedAt调用方注入，仅显示，时钟回退不影响选择/奖励。nextSeq到上限时同样停止持久事件序列并要求受控重开新attempt，不回绕。

highestUnlocked=最长completed连续前缀长度+1，上限20；例如L01完成为2，全通为20。完成记录可不连续（未来内容迁移保留旧完成），不会凭后面的完成跳开缺口。completed关可重玩，首次未通关仍需highestUnlocked门禁。bestStars/bestUsed按历史含义保留，不用新版par倒改旧成绩；没有排行榜/反作弊担保。新胜利取max星/min步，并设置lastCommittedAttemptId。只允许当前WON且!winCommitted的Session事务调用commitWin；相同attempt幂等。实验只在local-qa可开启，胜利不写正式records、不解锁campaign；P01/P02不能恢复实验活动局。

## 逐命令恢复与错误优先级

1. 原始槽UTF-8≤262144 bytes，无BOM；严格解析，重复键、非法UTF-8或代理项、非JSON/非安全整数数值拒绝JSON_INVALID。整数值不允许小数部分；数学上等于整数的1.0在CJ1中规范为1；非有限数拒绝。
2. schemaVersion非1→UNSUPPORTED_SCHEMA，ruleVersion非1.0.0→UNSUPPORTED_RULE；保留原字节、拒覆盖，只能经确认开启临时新档。不能先按旧schema丢字段“兼容”。
3. 完整Schema（包括真实日期、空bestUsed和Settings位置）→SCHEMA_INVALID；canonical checksum不等→CHECKSUM_MISMATCH；profile不等当前构建→PROFILE_MISMATCH。不会从checksum失败的槽捞设置。哈希是损坏检测，不是防作弊签名。
4. 校验records顺序/条件、推导highestUnlocked；不符→PROGRESS_INVALID。contentHash变化且前述全有效→CONTENT_CHANGED：保留合法历史records/settings，丢弃activeSession与history，提示关卡更新；确认后写新hash、新attempt，不把旧路线套新图。本版campaign ID冻结；若未来ID变化须显式迁移表，不能猜映射。
5. 同内容活动局：levelId确实存在、levelName/variant精确匹配；B0属于campaign，X1/X2属于独立实验；profile权限满足。普通未完成局必须已解锁；已完成可重玩。初态逐条执行acceptedCommands：每条必须accepted，终局不能继续追加；history逐步保存前态。逐字段比较position、bits、pending、nextBeacon、used、status、failure，全部相同才接受；used必须等路线长度、不得超level.move_limit、mask/坐标符合当前Level。totalAccepted>=路线长度、undoCount<=totalAccepted，不能把raw统计当规则预算。非法路线/任一字段不等→REPLAY_MISMATCH；元数据不合理→SESSION_INVALID。
6. FAILED合法恢复，history最后一项为导致失败前的完整PLAYING态；恢复后UNDO弹此快照并pop路线，failure恢复null；assisted和nextSeq不回退。WON活动档一律拒绝，不靠重放重复补结算。合法activeSession也不恢复pointer/动画/选格/暂停音频；回HOME由玩家继续。

双槽：逐槽按上述返回状态，选当前内容OK且revision最大；同revision同checksum视同一快照，优先A；同revision不同checksum返回SLOT_CONFLICT，不用active指针随意选，要求玩家选A/B有效快照。CONTENT_CHANGED是可解释更新分支，不能被旧active指针当当前内容OK自动加载；确认迁移后再写。单坏回有效槽；双坏保留原字节，用户确认前只用内存默认新档。未知版本槽存在时不覆盖其字节，可继续另一已知有效槽但必须提示版本冲突。真实写旧槽→回读→切指针、配额/安全/关闭中断均留T08/T12做获批后的I/O故障注入。

## CJ1规范化JSON字节与固定向量

对已解析数据值规范化：对象键按Unicode标量序递归升序，数组保持顺序；本Schema所有键为固定ASCII，因此JS默认sort与Python码点序一致。无多余空白，无末尾换行，无BOM。null/true/false为JSON小写；安全整数用十进制最短表示（0不是-0、无指数/小数点）；不使用浮点计算存档数值。

字符串不做NFC/NFD或其它Unicode归一化；中文及U+2028/2029直接UTF-8，不转成反斜杠u。仅双引号、反斜杠及U+0000…001F转义；\b/\t/\n/\f/\r用短形式，其余控制字符用小写四位\u；斜线/HTML字符不额外转义。输入JSON原来用\u中文也先解码，再按此规则写出同一规范字节。禁止未配对代理项；输入键只允许Schema字段，动态非ASCII键不进产品存档。

checksum=`SHA256(CJ1(envelope去掉checksum字段))`，小写hex。完整写槽字节是CJ1(含checksum的信封)，两者区分。contentHash是game-spec.json原始文件bytes，不是CJ1；文档/Schema校验工具变化不等于规则玩法升级，但game-spec元数据变化会产生新contentHash，按上述内容更新分支处理。

save-fixtures.json提供固定中文嵌套排序向量的canonical_utf8/hex/checksum、含中文关名的PLAYING活动档、合法FAILED活动档与恢复前态；每例另含预计payload字节hash。另有checksum损坏、Progress私藏settings、终态伪造、空bestUsed冲突、未知schema/rule、错误profile、内容更新等预期分支。validate_contracts.py用Python标准编码器与手写递归编码两路比较；可用Node时实际以JSON.stringify+递归排序+crypto核对同字节/摘要，否则明确UNKNOWN，不声称TS或浏览器存储跑过。
