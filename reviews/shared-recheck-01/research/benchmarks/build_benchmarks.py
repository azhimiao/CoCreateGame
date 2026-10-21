"""Research artifact generator; writes only beside this file. No game implementation."""
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent
DATE = '2026-10-21'
U = 'UNKNOWN'
S = {}

def source(sid, url, title, kind='OFFICIAL_GAME_PAGE', published=U, updated=U, note='已通过 web 读取官方正文；不代表执行游戏。'):
    S[sid] = dict(source_id=sid, source_url=url, title=title, accessed_at=DATE,
                  published_at=published, updated_at=updated, evidence_type=kind,
                  access_method='web', access_note=note, video_watched=False)

source('CM-PAINT','https://www.coolmathgames.com/hi/0-paint-master','Paint Master 官方说明（印地语页面）',updated='2026-10-20',note='英文主链接在 web 工具不可读；同站印地语正文可读，浏览器亦实到。官方本地化文本不等于独立来源。')
source('CM-RODHA','https://www.coolmathgames.com/0-rodha-2','Rodha 2 官方说明',updated='2026-10-15')
source('CM-SUIKA','https://www.coolmathgames.com/0-suika-watermelon-game','Suika Watermelon Game 官方说明',updated='2026-07-08')
source('CM-SUIKA-GUIDE','https://www.coolmathgames.com/blog/suika-watermelon-game-strategy','How to Play Suika Watermelon Guide','OFFICIAL_TUTORIAL','2024-01-17')
source('CM-TINY','https://www.coolmathgames.com/0-tiny-fishing','Tiny Fishing 官方说明',updated='2026-08-04')
source('CG-ARROW','https://www.crazygames.com/it/game/arrow-escape-puzzle','Arrow Escape: Puzzle 官方意大利语教学页',note='web 返回具名作品正文，但标示抓取缓存为约五个月前；英文/德文/罗马尼亚文直达曾跳转 Brain 类别，当前可玩性 UNKNOWN。不能以访问日期冒充内容刷新日期。')
source('CG-SCREW','https://www.crazygames.com/game/screw-out-bolts-and-nuts','Screw Out: Bolts and Nuts 官方教学',updated='2026-05-26')
source('CG-CAKE','https://www.crazygames.com/game/piece-of-cake-merge-and-bake','Piece of Cake: Merge and Bake 官方教学',updated='2025-05-28')
source('CG-DESCENT','https://www.crazygames.com/game/deadly-descent-bzs','Deadly Descent 官方教学',updated='2026-01-20')
source('PK-LEVEL','https://poki.com/en/g/level-devil','Level Devil 官方教学',updated='2026-09')
source('PK-DRIVE','https://poki.com/en/g/drive-mad','Drive Mad 官方教学',updated='2026-09')
source('FC-DRIVE','https://www.fancade.com/wiki/Drive_Mad','Drive Mad：Fancade 域内 Wiki','DEVELOPER_HOSTED_COMMUNITY_WIKI',note='开发者官方域托管的可编辑 Wiki；贡献者身份未核实，且明确区分 Fancade 内版本与独立 Web 版本；仅交叉确认输入，不借用具体关卡序号。')
source('PK-MONKEY','https://poki.com/en/g/monkey-mart','Monkey Mart 官方教学',updated='2026-03')
source('PK-BLOCK','https://poki.com/en/g/blocky-blast-puzzle','Blocky Blast Puzzle 官方教学',updated='2026-03')
source('PG-ARROW','https://playgama.com/game/arrow-puzzle','Arrow Puzzle 官方教学',updated='2026-06')
source('PG-SORT','https://playgama.com/game/good-sort-master','Good Sort Master: Triple Match 官方教学',updated='2026-06')
source('PG-CAKE','https://playgama.com/game/piece-of-cake-merge--bake','Piece of Cake: Merge & Bake 官方教学',updated='2026-08')
source('PG-FARM','https://playgama.com/game/my-perfect-farm-idle-tycoon','My Perfect Farm: Idle Tycoon 官方教学',updated='2026-10')
source('AZ-CATALOG','https://azurgames.com/games/','Azur 官方历史作品目录','OFFICIAL_HISTORICAL_PORTFOLIO')
source('AZ-SORT-CASE','https://azurgames.com/blog/how-unconventional-setting-affects-the-success-of-a-hyper-casual-game-in-an-occupied-niche/','Azur Color Sort Puz 历史运营案例','PUBLISHER_HISTORICAL_CASE_STUDY','2023-02-09')
source('AZ-SORT-STORE','https://play.google.com/store/apps/details?hl=en_US&id=com.Pizzart.CrowdSort','Color Sort Puz: Sorting games — CASUAL AZUR GAMES','PUBLISHER_STORE_LISTING',updated='2025-10-06')
source('AZ-STACK-STORE','https://play.google.com/store/apps/details?id=com.azurgames.stackball','Stack Ball - Crash Platforms — CASUAL AZUR GAMES','PUBLISHER_STORE_LISTING',updated='2026-10-08',note='本次打开正文 Updated on 为 Oct 8, 2026；搜索索引及其他语言曾显示更早日期，采用已打开英语正文，不混拼版本。')
source('AZ-TOWER-STORE','https://play.google.com/store/apps/details?id=com.quantumgames.skyscraper','Tower Craft: Build Skyscraper — CASUAL AZUR GAMES','PUBLISHER_STORE_LISTING',updated='2026-10-08')
source('TN-THIEF','https://www.tap-nation.io/games/thief-puzzle-to-pass-a-level/','Thief Puzzle 官方历史作品页','OFFICIAL_HISTORICAL_PORTFOLIO')
source('TN-THIEF-CASE','https://tap-nation.io/blog/thief-puzzle-a-case-study-of-a-hyper-casual-puzzle-mobile-game/','Thief Puzzle 官方案例','PUBLISHER_HISTORICAL_CASE_STUDY','2026-06-02')
source('TN-WATER','https://www.tap-nation.io/games/color-water-sort-puzzle-games/','Color Water Sort Puzzle Games 官方历史作品页','OFFICIAL_HISTORICAL_PORTFOLIO')
source('TN-WATER-STORE','https://play.google.com/store/apps/details?id=com.playspare.watersort3d','Color Water Sort Puzzle Games — TapNation','PUBLISHER_STORE_LISTING',updated='2026-10-16')
source('TN-GUESS','https://www.tap-nation.io/games/guess-their-answer/','Guess Their Answer 官方历史作品页','OFFICIAL_HISTORICAL_PORTFOLIO')
source('TN-GUESS-CASE','https://tap-nation.io/blog/guess-their-answer-a-case-study-of-a-top-trivia-mobile-game/','Guess Their Answer 官方流程案例','PUBLISHER_HISTORICAL_CASE_STUDY','2026-06-01','2026-06-02')
source('TN-GUESS-STORE','https://play.google.com/store/apps/details?id=com.qoni.guesstheiranswer','Guess Their Answer - IQ Games — TapNation','PUBLISHER_STORE_LISTING',updated='2026-09-23')
source('TN-HERO','https://www.tap-nation.io/games/hero-making-tycoon/','Hero Making Tycoon 官方历史作品页','OFFICIAL_HISTORICAL_PORTFOLIO')

def fact(text, *refs, verification='OFFICIAL_DESCRIPTION'):
    return dict(text=text, source_ids=list(refs), verification=verification)

CARDS=[]
def card(pid, slug, name, gids, sid, release, summary, rationale, counter, extra=(), mapping_note='', metrics=()):
    ids=[sid,*extra]
    c=dict(benchmark_id=f'{pid}-{slug}', platform_id=pid, game_id=gids, name=name,
           source_url=S[sid]['source_url'], accessed_at=DATE, published_at=S[sid]['published_at'],
           game_release_date=release, game_release_date_scope='官方页面所列本渠道版本；不当作全球首发。' if release!=U else U,
           evidence_type='OFFICIAL_HISTORICAL_PORTFOLIO' if pid in ('P05','P06') else 'OFFICIAL_GAME_PAGE',
           metric_definition='官方具名作品/教学页的存在与玩法说明；不是采购榜、游玩量、留存、收入或开发者净回款。',
           source_ids=ids, platform_association=dict(source_ids=[sid],status='OFFICIAL_PAGE_CONFIRMED',
           statement='发行商具名历史案例/作品关系' if pid in ('P05','P06') else '该平台官方具名游戏页'),
           mapping=dict(status='ANALYST_FAMILY_MAPPING' if gids else 'NONE',
                        explanation=mapping_note or ('按玩法骨架映射现有候选家族；不表示已批准开发。' if gids else '不强行归入G01—G10，保留为该发行商历史经验的边界样本。')),
           official_summary=summary, selection_rationale=dict(status='ANALYST_INFERENCE',text=rationale),
           counter_evidence=counter, known=[fact(summary,sid)],
           unknown=dict(current_procurement_demand=U, single_game_revenue=U, developer_net_receipts=U,
                        license_price=U, retention=U, active_players=U, causal_reason_for_popularity=U,
                        full_version_parity=U), metrics=list(metrics), ranking_status='NOT_MEASURED',
           direct_play=dict(status='NOT_ATTEMPTED',completed_playthrough=False,confirmed_gameplay_input=False,
                            complete_first_30_seconds=False,complete_first_5_minutes=False,evidence_paths=[]),
           deep_analysis_source=[],deep_analysis=None, recheck='在游戏实测/设计冻结前重核；动态评分与页面版本可变化。',
           research_status='EVIDENCE_COLLECTED',ready_for_build=False)
    CARDS.append(c);return c

def metric(name,value,definition,sid,window=U):
    return dict(name=name,value=value,metric_definition=definition,source_url=S[sid]['source_url'],accessed_at=DATE,
                observation_or_reporting_window=window,independently_audited=False)

paint=card('P01','paint-master','Paint Master',['G04'],'CM-PAINT','2026-10-08',
 '按行列刷色并用覆盖顺序复现目标图案；每次刷色耗一步，过关补步，步数耗尽结束。',
 '直接贴近G04的覆盖依赖和顺序规划；有官方输入、失败条件与辅助规则。',
 ['本地化页有广告声明及通用兼容性提示，不能据此推断实际广告频次或引擎。','浏览器只见游戏区域空白，未观察棋盘，不能把说明当亲测。'],
 metrics=[metric('rating','4.3/5; 624 votes','访问时页面用户评分与投票数，统计窗口未公开；不是游玩量。','CM-PAINT')])
rodha=card('P01','rodha-2','Rodha 2',['G05'],'CM-RODHA','2026-10-15',
 '左右定向跳跃、空中二段跳，避开危险抵达传送门；旗帜为检查点，通关获得金币并可用广告增加奖励。',
 '检验G05的动作输入、检查点和失败恢复；属包内具名参考。',
 ['官方文本明确有广告奖励，不能将其推广为所有Coolmath游戏的广告规则。','页面出现通用Flash不兼容提示，不足以认定本作品使用Flash；未操作验证。'])
suika=card('P01','suika-watermelon','Suika Watermelon Game',['G09'],'CM-SUIKA','2024-01-16',
 '拖动并松开投放水果，同类碰撞合成为更大水果，以高分为目标；箱体装满结束。',
 'G09的投放、碰撞与空间压力有教学页和官方攻略交叉支持。',
 ['研究对象仅是Coolmath所载版本；不宣称是其他同名Suika作品的相同实现。','官方攻略的水果顺序与数量不是物理参数、随机分布或完整数值表。'],extra=['CM-SUIKA-GUIDE'])
tiny=card('P01','tiny-fishing','Tiny Fishing',['G07'],'CM-TINY','2020-09-22',
 '点转盘抛钩、拖动鱼钩捕鱼、回到水面结算现金并升级钩具；官方说明离线仍有收益。',
 '用来研究短操作与升级/回访连接，G07仅作邻接对标。',
 ['捕鱼是主动操作，不等于工人/订单自动化经营。','单鱼收益、升级价格曲线及离线收益上限均UNKNOWN。'],mapping_note='仅映射G07的升级与离线成长部分，不能替代完整自动化经营对标。')
arrow=card('P02','arrow-escape-puzzle','Arrow Escape: Puzzle',['G01'],'CG-ARROW','2026-02',
 '沿箭头朝向移除未被阻挡的箭头，按依赖顺序清空棋盘；官方功能文案写单击/触碰，Controls另写拖动。',
 '优先保留包内G01参考，同时暴露控制文本与页面可用性的不确定性。',
 ['英文和若干语言链接重定向到Brain目录；意大利语正文来自web缓存，当前可玩性UNKNOWN。','同页一触一动与拖动描述有歧义；未亲测不能裁定。','不得把Playgama Arrow Puzzle的扣生命规则移植到本作品。'])
screw=card('P02','screw-out','Screw Out: Bolts and Nuts',['G02'],'CG-SCREW','2025-03',
 '点击拆除彩色螺丝，匹配顶部颜色容器；不匹配螺丝占有限暂存槽，填满导致失败风险。',
 'G02的拆除遮挡、有限缓冲与容器刷新有官方详细教学。',
 ['正文对暂存满的表述存在满即失败/满后再拆失败的边界差异，须实际检查。','官方点数道具价格不能证明现实货币、广告兑换或单位时间收益。'])
cakecg=card('P02','piece-of-cake','Piece of Cake: Merge and Bake',['G03'],'CG-CAKE','2024-10',
 '生成并合成食物满足顾客订单，获得资金修复咖啡馆并推进故事；拖动对象进行合成。',
 '可研究G03从合成到订单与装修的完整价值链。',
 ['正文说清空所有匹配，但订单/持续生成结构不等于传统清盘胜利条件。','与Playgama同名作品存在开发者名称、发布时间和控制说明差异，不能认定版本完全一致。'],extra=['PG-CAKE'])
descent=card('P02','deadly-descent','Deadly Descent',['G06'],'CG-DESCENT','2025-08',
 '用WASD或方向键控制可损坏车辆，穿过障碍抵达终点；C切镜头，移动端有屏幕按钮/方向盘。',
 '为G06补充损坏与速度控制型驾驶对标。',
 ['车辆损坏仍可能行驶，不能把任何碰撞都定义为失败。','所谓真实物理/移动端流畅是平台文案，未测帧率或真机。'])
level=card('P03','level-devil','Level Devil',['G05'],'PK-LEVEL','2023-12',
 '左右移动并跳跃抵达出口，地板、尖刺等突发陷阱引发失败，后续会增加控制变化。',
 'G05可研究惊讶反馈与重复尝试，但具体关卡表达不得复制。',
 ['官方教学不是本次玩家轨迹；本次只进入首关画面，未证明通过、死亡或重试。','加载与新内容弹窗造成中断，不能把按键/菜单操作算完整试玩。'])
drive=card('P03','drive-mad','Drive Mad',['G06'],'PK-DRIVE','2022-07',
 '只控制前进和刹车/倒车，利用加减速控制车辆平衡并抵达终点。',
 'G06以很少输入形成物理判断；有官方教学、开发者域Wiki及局部按键前后截图。',
 ['开发者域Wiki明确区分内置版与独立Web版；不移用其关卡39/43/45细节。','两秒按键只证实局部控制，不能声称完整五分钟、通关或已量出手感。'],extra=['FC-DRIVE'])
monkey=card('P03','monkey-mart','Monkey Mart',['G07'],'PK-MONKEY','2022-11',
 '移动猴子到作物、货架和收银台附近自动执行工作，售货收入用于升级、雇员和扩店。',
 'G07体现移动、自动工作、运输和经营反馈的衔接。',
 ['官方controls区竟只列全屏点击，须用正文与实际操作补齐移动键。','工人产率、定价、离线收益与设备性能未测。'])
block=card('P03','blocky-blast','Blocky Blast Puzzle',[],'PK-BLOCK','2024-04',
 '拖放形状填满行列以消除，保留可放置空间；官方说明含续命广告和存块等功能。',
 '包内真实热门参考，用作同平台空间决策的边界样本。',
 ['摆块消行并非Arrow、Sort或物理合成；不为覆盖指标强塞入十家族。','未实测广告续命、跳过次数和计分规则。'],mapping_note='NONE：静态摆块消行，和G04图层/机关、G09物理合成均不等价；不新增候选。')
pgarrow=card('P04','arrow-puzzle','Arrow Puzzle',['G01'],'PG-ARROW','2026-04',
 '触碰前方通路畅通的箭头使其离场，按顺序清空棋盘；官方教学说点击被阻挡箭头会扣生命。',
 'G01可比较依赖解锁与错误操作惩罚，和CrazyGames具名作品分别存档。',
 ['生命总数、扣完后的付费/广告恢复未知。','页面排行榜daily人数定义不透明，不采作DAU、游玩量或留存。'])
pgsort=card('P04','good-sort-master','Good Sort Master: Triple Match',['G02'],'PG-SORT','2024-10',
 '拖动货架物品，把三个相同物品放在同一架位触发消除，清空所有物品过关。',
 'G02的货架空间、三件匹配和视觉收纳区别于倒水和螺丝排序。',
 ['官方FAQ声称无计时和生命；尚未核对具体运行版本，不将其写成已测数值。','页面的零延迟/低端设备完美运行/无物理开销是宣传性断言，未验证。'])
cakepg=card('P04','piece-of-cake','Piece of Cake: Merge & Bake',['G03'],'PG-CAKE','2025-03',
 '合并食材、扩大制作空间、修复咖啡馆与解锁区域；官方列HAPPY GAMES STUDIO及Defold。',
 '同名跨平台作品保留各自关联证据，用于G03版本比较。',
 ['本页写桌面右键交互，CrazyGames写左键；未试不能消除差异。','可按标题暂列同名作品组，但正式身份、权利主体和版本等价UNKNOWN。'],extra=['CG-CAKE'])
farm=card('P04','my-perfect-farm','My Perfect Farm: Idle Tycoon',['G07'],'PG-FARM','2026-08',
 '种植收获、饲养动物、销售产物，再投入雇员和区域扩张；官方列Tapfire。',
 'G07的生产、搬运、出售、扩张链可与Monkey Mart作结构比较。',
 ['页面PC/Android/iOS指可访问设备，不自动证明独立原生商店包。','标题Idle不能证明离线收益，产出周期、售价和广告点均UNKNOWN。'])
azsort=card('P05','color-sort-puz','Color Sort Puz: Sorting games',['G02'],'AZ-SORT-CASE',U,
 'Azur在2023年具名说明与Pizzart合作发行：把倒水排序表现为彩色人群在通道间移动。',
 '替换包内行业品类占位；具名官方案例与同包名商店页共同证明发行关系和规则。',
 ['2023案例说撤销改为每关两次免费再看激励广告，商店文案仍写无限撤销，当前实现UNKNOWN。','商店一段允许空容器/同色，另一段只写空容器，合法移动边界有自相矛盾。','历史收入为厂商自述总收入，非审计净利润、开发者到手或2026新作预期。'],extra=['AZ-SORT-STORE'],
 metrics=[metric('reported_total_revenue','> USD 1.5 million','2023案例自述项目累计总收入；收入期间、税费和渠道拆分未完整披露；非开发者净收益。','AZ-SORT-CASE','截至2023-02-09案例时点'),metric('reported_total_spend','> USD 1 million','同期案例自述累计支出，成本覆盖范围未完整披露，禁止相减得净利。','AZ-SORT-CASE','截至2023-02-09案例时点')])
aztower=card('P05','tower-craft','Tower Craft / Tower Craft: Build Skyscraper',['G07'],'AZ-CATALOG',U,
 'Azur官网具名列Tower Craft；同发行商商店说明为点击建塔、现金与升级选择的放置建设游戏。',
 '补充G07的垂直建设/点击增长历史样本。',
 ['官网目录没有发行日期及单作商业指标。','商店下载档位是Android累计安装门槛，不是近期新增、活跃或开发者回款。'],extra=['AZ-TOWER-STORE'])
azstack=card('P05','stack-ball','Stack Ball - Crash Platforms',[],'AZ-CATALOG',U,
 'Azur官网具名Stack Ball；同发行商商店说明为穿过旋转彩色平台到达底部，撞黑色平台通常破碎重来。',
 '作为Azur具名短回合动作发行经验样本，避免拿品类名称冒充作品。',
 ['非横向陷阱平台跳跃、非物理合成，不能强行映射G05/G09。','商店500M+为Android累计安装档位，统计窗口不公开；与采购意愿、净收入无关。'],extra=['AZ-STACK-STORE'],
 mapping_note='NONE：垂直破平台时机街机；十家族外边界样本，不新增游戏家族。')
azbottle=card('P05','bottle-jump','Bottle Jump 3D',[],'AZ-CATALOG',U,
 'Azur官网明确列出在室内障碍间翻转水瓶的具名街机作品。',
 '第四个可核查Azur官方作品，展示动作发行经验但不假造其偏好。',
 ['目前只有官方目录短介绍，精确输入、失败/重试、经济和首发日期UNKNOWN。','水瓶跳跃不是驾驶；不能为了覆盖G06而强行归类。'],mapping_note='NONE：翻瓶动作；只证明历史具名作品关联，不能推导P0解谜采购需求。')
thief=card('P06','thief-puzzle','Thief Puzzle: to pass a level',['G04'],'TN-THIEF',U,
 '伸长盗贼手臂绕过环境和陷阱取到目标；官方案例描述短关成功/失败及奖励、装扮。',
 'G04的路径与机关环境邻接参考；强视觉角色表达不可直接复刻。',
 ['不等于图层覆盖；G04只能借鉴机关观察及路径规划。','厂商案例下载与榜位为历史自述，非本次独立审计，也非2026最新榜。'],extra=['TN-THIEF-CASE'],mapping_note='G04邻接：环境机关/路径逻辑，不能代替Paint Master的覆盖依赖。')
water=card('P06','color-water-sort','Color Water Sort Puzzle Games',['G02'],'TN-WATER',U,
 '把彩色液体按同色与容量限制倒入试管，每关完成获得宝石并可换提示；官方说明无时间限制。',
 'G02有发行商官网教学、官网直链商店与一致包名三者关联。',
 ['无时间限制不等于不能陷入无合法移动。','Play Pass与普通广告版不同，不能从商店广告标识推出每关必播或无广告。'],extra=['TN-WATER-STORE'])
guess=card('P06','guess-their-answer','Guess Their Answer',['G08'],'TN-GUESS',U,
 '根据题目输入大众可能给出的答案，以匹配常见回答获得分数并和对手比较；案例说明硬币与装扮成长。',
 'G08唯一直接对应包内群体答案玩法的具名参考。',
 ['厂商同时称实时对战与离线单人，当前对手真人/机器人机制UNKNOWN。','大众答案的问卷来源、样本量、授权与地区语言分布UNKNOWN；不能当公开调查数据。','官网案例内榜位类别/年份混杂，未采纳其全球第一或收入排行作选品结论。'],extra=['TN-GUESS-CASE','TN-GUESS-STORE'])
hero=card('P06','hero-making-tycoon','Hero Making Tycoon',['G07'],'TN-HERO',U,
 '土豆人经种植和自动装备生产线变为职业英雄，与怪物战斗；离线产出资源用于升级工厂。',
 'G07的自动生产、战斗消耗与离线回访有官方具名描述。',
 ['产线站数、各职业成本、战斗失败惩罚与离线封顶UNKNOWN。','官网宣称怪物/机械数量不是已检查的完整内容清单。'])

def section(known=(), unknown=(), hypotheses=()):
    return dict(known=list(known), unknown=[{'value':U,'field':x} for x in unknown],
                hypotheses=[dict(status='HYPOTHESIS',text=x) for x in hypotheses])

def deep(c, sections, cross, missing, probe):
    # All 12 timing narratives are reconstructions, including games with partial browser evidence.
    c['deep_analysis_source']=[dict(source_id=s,source_url=S[s]['source_url'],accessed_at=DATE,
                                  published_at=S[s]['published_at'],evidence_type=S[s]['evidence_type'],
                                  role='官方说明/教学交叉核查，非本次回放') for s in cross]
    c['deep_analysis']=dict(mode='SECONDARY_RECONSTRUCTION',
        timing=dict(first_30_seconds=U,first_5_minutes=U,basis='未录制从首次可操作起连续30秒/5分钟轨迹；下面按官方规则重建可能顺序，不是定时回放。'),
        sources_crosscheck=dict(source_ids=cross,result='已核对官方说明；冲突/单一来源限制逐项保留。',gaps=missing),
        sections=sections, next_direct_probe=dict(status='HYPOTHESIS',actions=probe,
            acceptance='保存输入前后状态、失败及重试截图/日志；从首次可操作计时，不把加载或广告等待计入游戏时长。'),
        video_evidence=dict(watched=False,observed_timecodes=[],reason='本次未观看官方视频；页面Video/Gameplay Video标题或Trailer按钮不构成已观看证据。'))
    c['research_status']='EVIDENCE_COLLECTED_WITH_RECONSTRUCTION'

deep(paint,{
 'first_30_seconds':section([fact('可核实操作链：观察顶部目标→点右侧行刷/底部列刷→对应行列着色且覆盖旧色→比较目标；这只是说明重建。','CM-PAINT')],['首次加载到可操作的时间','首关图案、初始步数、教程遮罩顺序','第一操作发生在第几秒']),
 'first_5_minutes':section([fact('可重建循环：完成图案→进入下一关并补步→继续规划覆盖顺序；不是五分钟内实际完成关数。','CM-PAINT')],['五分钟实际通过关数和难度变化','每关补步量、关卡生成规则','是否跨关沿用剩余步数及具体结算顺序']),
 'core_input':section([fact('行/列边缘的画刷是点击/触碰输入；新颜色覆盖旧层。','CM-PAINT')],['同一画刷能否连续重复、动画中输入是否排队','误触撤销与键盘支持']),
 'success':section([fact('画布匹配目标即完成一关。','CM-PAINT')],['匹配检测在动画前还是后、最后一步恰好匹配如何优先结算']),
 'failure':section([fact('可用步数耗尽会结束游戏。','CM-PAINT')],['错误图案是否额外扣分','用完步数与胜利同时发生的优先级']),
 'retry':section([],['结束后的重试按钮、恢复点、广告续关与是否重置Magic Brush']),
 'mid_term_loop':section([fact('完成关卡增加可用步数；魔法刷可直接把一行/列变成目标对应颜色，不耗步，每局限用三次。','CM-PAINT')],['局的定义、三次额度重置时机','总关数、后期机制、分数曲线']),
 'ui':section([fact('官方说明位置：目标在顶部、Move圆形计数在右侧、Magic Brush在右下；这些尚未在棋盘实测。','CM-PAINT')],['实际棋盘尺寸、动效时长、音频、触控命中范围']),
 'ads_economy':section([fact('页面说明含嵌入式视频广告；不提供频次和奖励兑换表。','CM-PAINT')],['实际广告是否出现、触发与时长','金币/IAP/开发者收入']),
 'devices':section([fact('官方列Browser、Mobile，并给出移动主页添加说明。','CM-PAINT')],['Android/iOS真机、横竖屏行为','加载性能；本次桌面仅观察到空白游戏区'])
},['CM-PAINT'],['仅同站本地化官方教学，缺独立开发者教学/已观看官方视频。','浏览器未加载棋盘，所有玩法仍是间接重建。'],['选一行刷与一列刷并比较交点覆盖','耗尽步数，检查失败/重试','验证Magic Brush额度与重置边界'])

deep(suika,{
 'first_30_seconds':section([fact('可核实链：观察当前与下一水果→拖到投放横坐标→松开→等待落下/碰撞→同类合并。时间未观测。','CM-SUIKA','CM-SUIKA-GUIDE')],['首屏教程、起手水果与随机种子','第一次合成耗时、首局初始分数']),
 'first_5_minutes':section([fact('官方攻略建议看下一水果、把大果靠近并管理剩余空间；可以在卡住时使用推挤。','CM-SUIKA-GUIDE')],['五分钟实际得分与果序','投放间隔、队列概率、暂停/恢复行为']),
 'core_input':section([fact('鼠标或手指拖动定位，松开投放；左右按钮可整体推水果。','CM-SUIKA','CM-SUIKA-GUIDE')],['能否键盘控制、投放与碰撞动画中是否锁输入']),
 'success':section([fact('目标是尽可能高分和合出更大水果；不是已证实的逐关胜利。','CM-SUIKA')],['分数公式、单果分值和西瓜后是否有终局动画']),
 'failure':section([fact('箱体装满至边缘会结束。','CM-SUIKA')],['越线检测区、高度容忍、滞留时间、碰撞回弹越线如何判定']),
 'retry':section([],['结束后的重来入口、保留最高分、广告续命、推挤次数重置']),
 'mid_term_loop':section([fact('合并→腾出/占用新空间→放下一果→争取更高阶果；官方教程列左右各五次推挤。','CM-SUIKA','CM-SUIKA-GUIDE')],['随机分布、摩擦/弹性、长局存档、难度随时间变化']),
 'ui':section([fact('攻略说明右侧有水果阶次索引，并提示关注下一水果；推挤按钮在下方/左右。','CM-SUIKA-GUIDE','CM-SUIKA')],['本次具体布局截图、分辨率适配、音频/震动']),
 'ads_economy':section([],['广告位置/频次/续命','可购货币、IAP、真实单款收益']),
 'devices':section([fact('官网支持浏览器与移动设备；触控与鼠标说明均存在。','CM-SUIKA')],['实际手机帧率、合成高峰性能、触摸拖动偏移'])
},['CM-SUIKA','CM-SUIKA-GUIDE'],['两个同平台官方页面互相补充，仍不是独立玩家观察；未观看视频、未直接操作。'],['拖放同阶果并保存合成前后状态','逐步堆到箱口核对实际失败边界','核查推挤次数及重新开始'])

deep(arrow,{
 'first_30_seconds':section([fact('说明可重建：找朝向前方无阻挡的箭头→触碰/拖动该箭头→腾出通路→再选箭头。','CG-ARROW')],['加载、教程、首棋盘、首个合法/非法动作的实际反馈','触碰与拖动到底哪个生效']),
 'first_5_minutes':section([fact('可重建短关清盘后进入后续关；官方说关卡短并非本次测得时长。','CG-ARROW')],['五分钟关数、难度、广告中断','生命、计时器、提示首次出现条件']),
 'core_input':section([fact('箭头只能沿尖端朝向、在前方清空后移除；同页输入文字有触碰/拖动歧义。','CG-ARROW')],['点击被挡箭头后是否消耗资源','触发在按下、松开还是拖动阈值']),
 'success':section([fact('移除棋盘全部箭头。','CG-ARROW')],['结算奖励、关卡计数、特殊障碍是否需清除']),
 'failure':section([],['失败条件、是否有生命/倒计时/步数','死锁时自动判负还是提示']),
 'retry':section([],['重试按钮、付费/广告恢复、是否回滚一步']),
 'mid_term_loop':section([fact('按阻挡关系决定清除次序；后续复杂度变化未提供可复现数据。','CG-ARROW')],['箭头数量曲线、障碍种类、提示/关卡包解锁']),
 'ui':section([],['实机箭头命中区、生命/关号/提示按钮','颜色是否编码规则、色弱可达性']),
 'ads_economy':section([],['所有道具价格、广告点、IAP、收益']),
 'devices':section([fact('缓存官方页列桌面、移动、平板浏览器和CrazyGames App；不能等同本次兼容性通过。','CG-ARROW')],['当前可玩性、重定向原因、触控实际效果'])
},['CG-ARROW'],['官方页面为缓存正文，部分直达重定向；当前运行版本未核实。','无开发者独立教学或观看过的官方视频；不能用另一Arrow作品填补失败规则。'],['先确认具名游戏仍可进入，再比较点击和拖动','选一个被挡箭头观察是否扣资源','清盘、失败、重试各记录一次'])

deep(screw,{
 'first_30_seconds':section([fact('说明可重建：看顶部颜色容器→选可触及且匹配的螺丝→点击拆下→填入容器/暂存区。','CG-SCREW')],['实际教程、首关容器数、暂存槽初值','首次拆除动画与响应时间']),
 'first_5_minutes':section([fact('拆完固定某片形状的螺丝后该片移除；填满一个颜色容器后换色，继续处理遮挡。','CG-SCREW')],['五分钟通关数和露出顺序','物理掉落是否改变剩余螺丝可选性']),
 'core_input':section([fact('左键拆螺丝，颜色匹配优先入顶部容器，不匹配占额外孔位。','CG-SCREW')],['不可见/被遮挡螺丝能否点','动画期间多点能否排队']),
 'success':section([fact('完成要求的螺丝分类可完成该关；FAQ说明同色三颗填满容器后刷新。','CG-SCREW')],['顶部目标填满与全部板片移除哪个先触发胜利']),
 'failure':section([fact('有限不匹配暂存区满会触发失败风险；正文对满即失败或满后再拆有表述差异。','CG-SCREW')],['失败检测准确时机、槽数、是否留一次补救动作']),
 'retry':section([],['失败弹窗、复活/重试、恢复哪个状态','是否保留已用道具或本关奖励']),
 'mid_term_loop':section([fact('匹配→容器刷新→利用暂存腾挪→拆除更多形状；教学列磁铁、钻孔、锤子、跳关工具。','CG-SCREW')],['每关产出点数、道具发放、后期颜色/遮挡曲线']),
 'ui':section([fact('官方教学把目标容器置顶、形状和螺丝置下；未取得实机布局。','CG-SCREW')],['各道具按钮位置、槽位反馈、动画时长']),
 'ads_economy':section([fact('教学所列道具点数价格：磁铁1500、钻孔1200、锤子1800、跳关3000；仅平台文字快照，不是已测经济。','CG-SCREW')],['点数获取速率、付费货币、广告兑换、IAP、开发者收益']),
 'devices':section([fact('官方列Unity 2022、竖屏及桌面/移动/平板浏览器。','CG-SCREW')],['实际引擎构建、触控、掉板物理性能、内存'])
},['CG-SCREW'],['只有平台教学单一来源；没有独立开发者教学/已观看视频。','未直接试玩，暂存失败边界须列为P0规则阻塞。'],['用不匹配螺丝填满暂存，验证失败时机','连续拆三颗同色观察容器刷新','记录板片移除和剩余目标变化'])

deep(level,{
 'first_30_seconds':section([fact('说明链：选关→左右移动/跳跃→避开突发陷阱→争取出口。实际初始30秒未知。','PK-LEVEL')],['从首次可操作起的连续30秒轨迹','首个陷阱触发条件、输入延迟','本次最后按键是否已在角色可控时生效']),
 'first_5_minutes':section([fact('官方描述围绕失败后学习陷阱、再尝试与新陷阱推进。','PK-LEVEL')],['实际五分钟死亡数、通关数、重试间隔','菜单与弹窗占用时长不算玩法时长']),
 'core_input':section([fact('官方列A/D或左右方向移动，W/上/空格跳跃；移动端屏幕按钮。','PK-LEVEL')],['本次角色位移是否由按键导致、跳跃高度、输入缓冲']),
 'success':section([fact('抵达关卡出口门。','PK-LEVEL')],['具体碰撞阈值、通关过场、结算奖励']),
 'failure':section([fact('陷坑、尖刺与其他突然变化可导致失败。','PK-LEVEL')],['本次首关实际失败条件及死亡动画','关卡各陷阱位置/参数；不得复制原关卡表达']),
 'retry':section([fact('官方教学说明多次尝试、学习陷阱是核心体验。','PK-LEVEL')],['实际重试键、复活延迟、是否回到小段开头']),
 'mid_term_loop':section([fact('官方举例后续控制反转、平台变化等，属于厂商描述。','PK-LEVEL')],['解锁顺序、难度曲线、编辑器内容与主线的关系']),
 'ui':section([fact('官方页面有具名教学与键位说明。','PK-LEVEL')],['主线菜单到角色关卡的完整可复现首局序列','各图标实际功能、音频、触摸按钮布局']),
 'ads_economy':section([],['实际播广告、触发频率、跳关/提示经济','本次休息文案不能证明广告已播放']),
 'devices':section([fact('官方列desktop、phone、tablet；本次访问环境为Windows桌面Chromium，1365×900。','PK-LEVEL')],['Android/iOS真机、后台/前台与点击事件对游戏的影响'])
},['PK-LEVEL'],['本次只有菜单/弹窗输入和首次关卡场景，尚无可归因的角色位移前后对照。','开发者博客检索可发现但打开遇429，没有用它支持玩法；未观看视频。'],['后续由授权研究者记录角色移动/跳跃前后状态','失败与重试各一次','连续计时观察30秒及五分钟'])

deep(drive,{
 'first_30_seconds':section([fact('官方规则链：前进→控制坡道/腾空角度→稳定落地→到终点；本次只证明两秒向前操作片段。','PK-DRIVE')],['完整首30秒及首次教程','起手是否有统一关名、胜利触发实际时点']),
 'first_5_minutes':section([fact('官方描述随关卡变换路面和车辆挑战，以平衡而非一直加速推进。','PK-DRIVE')],['五分钟实际关数、失败数、广告中断','不得把官方关数当本次已玩数量']),
 'core_input':section([fact('Poki教学为右键前进、左键后退；Fancade域Wiki补充左侧刹车/倒车，右侧加速。','PK-DRIVE','FC-DRIVE')],['加速度、刹车力、悬挂参数、设备触控命中区']),
 'success':section([fact('官方教学以抵达终点为目标。','PK-DRIVE')],['本次截图靠近格纹终点但没有结算画面，不能认定过关']),
 'failure':section([fact('开发者域Wiki说倒扣落地会损坏车辆，但不同Web版本的边界须实测。','FC-DRIVE')],['本次实际翻车/落水、失败过场','车体损坏的阈值与可恢复角度']),
 'retry':section([],['失败后自动还是按键重开','重置延迟、跳关/广告条件']),
 'mid_term_loop':section([fact('少量输入反复调整车辆平衡、应对新路线；独立Web与Fancade内版本不同。','PK-DRIVE','FC-DRIVE')],['具体版本解锁/杯赛与存档规则','本次未测试任何中期赛道']),
 'ui':section([fact('官方教程支持仅前进/后退两种输入。','PK-DRIVE')],['截图所见暂停、VS、新世界按钮的实际功能','失败界面、键位重映射、音频']),
 'ads_economy':section([],['实际广告播放、跳关奖励、IAP或货币','只观察到平台广告占位，不据此计算游戏广告频率']),
 'devices':section([fact('Poki列桌面、手机、平板；本次Windows桌面Chromium1365×900可加载并执行局部键盘输入。','PK-DRIVE')],['手机触控/性能、低配设备、物理回放确定性'])
},['PK-DRIVE','FC-DRIVE'],['Fancade官方域Wiki是可编辑补充，非独立审计且有版本差异。','局部按键片段不涵盖完整开局、胜负、重试或五分钟。'],['短按/长按前后车姿对照','主动翻车并记录重试','从新档完整计时首五分钟'])

deep(pgarrow,{
 'first_30_seconds':section([fact('说明重建：识别箭头尖端→找无阻挡前方路径→点箭头→箭头移除并打开其他路径。','PG-ARROW')],['真正首屏、教程、棋盘和起始生命','首次输入/反馈时长']),
 'first_5_minutes':section([fact('清空一板完成关卡，可继续后续板；官方另提每日挑战与提示。','PG-ARROW')],['五分钟关数、每日挑战开启时机','新障碍、难度曲线、广告出现时点']),
 'core_input':section([fact('官方Controls为触碰路径畅通的箭头；教学明确被挡时会扣一条生命。','PG-ARROW')],['按下/松开触发、快速连点处理','箭头外形折线是否都参与阻挡']),
 'success':section([fact('移除全部箭头完成该关。','PG-ARROW')],['奖励、剩余生命是否影响结算']),
 'failure':section([fact('点被阻挡箭头损失生命。','PG-ARROW')],['生命总数、耗尽结果、空点是否惩罚','无解棋盘如何处理']),
 'retry':section([],['重试入口、生命恢复、广告/货币续关、是否重新生成']),
 'mid_term_loop':section([fact('规划移除顺序、使用提示、进入后续挑战。','PG-ARROW')],['提示内容及价格、关卡包总数、日常奖励']),
 'ui':section([],['本次实际棋盘、生命计数、提示、日常入口和动画','颜色与方向的冗余可读性']),
 'ads_economy':section([],['全部广告触发点、免费/付费提示、内购','排行榜不构成经济指标']),
 'devices':section([fact('官方列竖屏与PC/Android/iOS浏览访问；列出多语言。','PG-ARROW')],['实际触控、设备/性能、存档跨设备行为'])
},['PG-ARROW'],['仅Playgama官方教学一源；同站其他语言不是独立交叉证据。','没有直接G01规则观察，也未观看官方视频；必须补实玩。'],['各点一次畅通与被挡箭头并记录状态','耗完生命记录重试','完整清盘一次并记录下一关'])

deep(pgsort,{
 'first_30_seconds':section([fact('说明重建：看架上重复物→拖动物件到同一架位→集齐三个相同物→三件消失。','PG-SORT')],['首关物件种类、槽位、初始布局','引导手势顺序及响应时长']),
 'first_5_minutes':section([fact('重复移动与三件消除，使阻挡物移开，直至架上清空并进入下一关。','PG-SORT')],['五分钟通关/卡住次数','移动合法性、是否有隐藏层、何时补充新物件']),
 'core_input':section([fact('桌面鼠标拖动；手机触碰拖动，在同一架位凑三个相同物。','PG-SORT')],['满槽、回退、交换、层后物件能否拖','自动吸附阈值']),
 'success':section([fact('移除全部架上物品完成关卡。','PG-SORT')],['重复物数量不足时如何收尾、是否有额外任务']),
 'failure':section([fact('官方FAQ声称没有倒计时/生命系统。','PG-SORT')],['无合法移动是否弹失败','无生命不等于不会死锁或有无限撤销']),
 'retry':section([],['重开、撤销、洗牌及死锁补救','重开是否相同布局']),
 'mid_term_loop':section([fact('官方说后续架位布局/物件更丰富；不能把宣传举例当关卡数据表。','PG-SORT')],['真实关卡引入序、随机关与固定关比例']),
 'ui':section([fact('官方描述货架格位和食品物件；未实测具体布局。','PG-SORT')],['遮挡、拖动影子、可落位高亮、成功/失败弹窗']),
 'ads_economy':section([],['广告触发、辅助道具、货币、IAP','移除广告是否影响辅助功能']),
 'devices':section([fact('官方列Unity、竖屏和PC/Android/iOS浏览器。','PG-SORT')],['低配帧率、内存、存档、手机触控','Microsoft Store官网直链打开仅JS壳，未用于确认玩法'])
},['PG-SORT'],['单一平台教学；官网所链Microsoft Store只有JS壳，未获得可用的独立说明。','无G02直接操作轨迹；页面性能宣称不当实测。'],['拖入三件同物记录消除','填满架位测试非法拖动与死锁','验证无计时/生命是否属当前版本'])

deep(azsort,{
 'first_30_seconds':section([fact('案例/商店支持的链：观察彩色人群所在通道→选源→选空或同色容器→人群移动；未测时间。','AZ-SORT-CASE','AZ-SORT-STORE')],['实际首屏、教程、通道容量与首次动作','人群批量移动数量、合法规则文本冲突']),
 'first_5_minutes':section([fact('按颜色归并并推进后续关卡；卡住时可撤销/重开；这是描述重建。','AZ-SORT-STORE')],['五分钟实际关卡数、广告量','2023案例修改是否仍在当前包内']),
 'core_input':section([fact('商店列单指点击排序；说明可将动作排队，无需等动画结束。','AZ-SORT-STORE')],['连续点击排序队列、不可达目标反馈','同色容器/仅空容器这两段矛盾的运行结果']),
 'success':section([fact('把人群按颜色归到各自容器。','AZ-SORT-STORE','AZ-SORT-CASE')],['空槽允许数、胜利是否要求每个非空容器装满']),
 'failure':section([fact('商店宣传无计时，并允许卡住时撤销或重开。','AZ-SORT-STORE')],['死锁自动检测、失败计数与任何体力系统']),
 'retry':section([fact('商店明确可撤销/重开。2023案例曾把每关免费撤销改成两次，激励广告增加三次。','AZ-SORT-STORE','AZ-SORT-CASE')],['无限撤销商店文本与限次案例哪个适用当前版','重试是否重置免费额度']),
 'mid_term_loop':section([fact('案例说运营中继续平衡关卡，曾试隐藏底部颜色的Boss关但老玩家有抵触。','AZ-SORT-CASE')],['该试验是否最终上线、当前机制顺序','新用户与老用户差异']),
 'ui':section([fact('商店说明有夜间模式、撤销和关卡重开。','AZ-SORT-STORE')],['当前按钮布局、无障碍、动画和人群碰撞是否只做表现']),
 'ads_economy':section([fact('商店标广告/IAP；2023案例给出特定撤销激励广告实验。','AZ-SORT-STORE','AZ-SORT-CASE')],['当前广告频率与兑换、IAP价格','历史累计收入不等于净利，开发者分成UNKNOWN']),
 'devices':section([fact('关联商店包名com.Pizzart.CrowdSort，署名CASUAL AZUR GAMES。','AZ-SORT-STORE')],['最低OS、真机性能、历史与当前APK一致性','未安装移动App、未试玩'])
},['AZ-SORT-CASE','AZ-SORT-STORE'],['官方历史案例+发行商商店互相支持身份与骨架，但撤销/合法移动文案冲突。','未看官方Trailer，不以按钮存在充当观看。'],['核查当前APK版本与撤销额度','分别选空/同色/异色容器观察合法性','记录胜利、死锁、重开与广告前后状态'])

deep(azstack,{
 'first_30_seconds':section([fact('官方可核实骨架：球在旋转平台上跳动，穿过彩色平台向底部推进；避免普通状态撞黑平台。','AZ-CATALOG','AZ-STACK-STORE')],['首次触控究竟按住还是点按、第一关布局','正式教程与首次落下时长']),
 'first_5_minutes':section([fact('官方描述可选择加速破坏或停下等待机会；重复下落挑战。','AZ-STACK-STORE')],['五分钟过关数、失败数、广告','火球出现顺序与触发阈值']),
 'core_input':section([fact('商店确认速度/等待策略，但正文没有充分说明准确手势。','AZ-STACK-STORE')],['核心触控按住/松开规则','是否能控制平台转向，输入窗口']),
 'success':section([fact('穿过平台到达下方终点。','AZ-CATALOG','AZ-STACK-STORE')],['最后层触发、结算奖励、下一关入口']),
 'failure':section([fact('普通状态撞到黑色平台使球破碎，须重新开始下落；火球高速状态可击破黑平台。','AZ-STACK-STORE')],['碰撞判定、火球阈值/时长','破碎与广告续命关系']),
 'retry':section([fact('商店说失败后重新下落。','AZ-STACK-STORE')],['实际按钮、关卡/层数恢复、复活与等待']),
 'mid_term_loop':section([fact('重复判断旋转安全区、推进到底部；未验证关卡生成或解锁。','AZ-STACK-STORE')],['皮肤、货币、难度、永久成长是否存在']),
 'ui':section([],['实际关号、进度、火球指示、失败/重试按钮','商店截图不是亲测UI']),
 'ads_economy':section([fact('发行商商店标明广告和应用内购买。','AZ-STACK-STORE')],['广告位置与频率、IAP条目/价格、RPM、净收益']),
 'devices':section([fact('官网具名目录与Android包com.azurgames.stackball同属Azur关系证据。','AZ-CATALOG','AZ-STACK-STORE')],['Android最低版本、iOS同款关系、真机性能','未安装、未执行核心输入'])
},['AZ-CATALOG','AZ-STACK-STORE'],['目录与商店交叉验证作品/目标，手势仍UNKNOWN。','完全间接重建，不能从同名仿作教学补手势。'],['先获取准确按住/松开手势','普通球/火球分别碰黑平台','胜负、重试及广告各存一次证据'])

deep(water,{
 'first_30_seconds':section([fact('官网/商店支持：观察颜色与空余空间→选源管和目标管→在允许条件下倒色→继续归并。','TN-WATER','TN-WATER-STORE')],['第一关管数、每管容量、具体点击/滑动手势','新手教程与首次倒色时长']),
 'first_5_minutes':section([fact('把颜色归到各自管中完成关卡，获宝石后可换提示，再继续关卡。','TN-WATER','TN-WATER-STORE')],['五分钟关数、宝石实际收益、首个难点','每次倒单格还是连续同色段']),
 'core_input':section([fact('官方给单指/滑动控制；目标有容量且顶色兼容才允许倒入。','TN-WATER','TN-WATER-STORE')],['空管例外的精确定义、满管点击反馈','手势是点击两管还是拖动、动画中输入']),
 'success':section([fact('每管聚合同色，解完当前谜题。','TN-WATER-STORE')],['允许未满的纯色管或必须满管','胜利与最后一段动画结算顺序']),
 'failure':section([fact('官方说无倒计时，也提醒避免把自己卡住。','TN-WATER','TN-WATER-STORE')],['无合法移动是否自动失败、体力、步数限制']),
 'retry':section([],['撤销、重开、额外管及失败后恢复状态','宝石/广告能否换撤销；未凭玩家评论认定']),
 'mid_term_loop':section([fact('关卡→宝石→提示→更复杂谜题，官方说有大量关卡。','TN-WATER')],['确切关卡顺序、颜色数量曲线、提示算法','宝石供应与消耗数值']),
 'ui':section([fact('官方页面提供多关宣传截图，但本次没在运行App中复现。','TN-WATER')],['实际试管布局、提示/撤销按钮、色弱方案','音频、触控尺寸']),
 'ads_economy':section([fact('Google Play标广告/IAP，并另有Play Pass分发说明；官网说宝石可换提示。','TN-WATER-STORE','TN-WATER')],['普通版/Play Pass实际广告差异','每关奖励、提示成本、IAP价格、开发者分成']),
 'devices':section([fact('官网直接链接发行商商店包com.playspare.watersort3d。','TN-WATER','TN-WATER-STORE')],['最低Android/iOS条件、真机横竖屏、恢复存档','未安装或执行移动版'])
},['TN-WATER','TN-WATER-STORE'],['官网与其直链商店互相支持身份、倒色与宝石提示；两者仍属同一发行商描述。','无实际操作与视频轨迹，容量/倾倒段数不能猜。'],['空管/同色/异色/满管分别试一次','构造无合法移动并记录补救','核查通关宝石和提示扣款'])

deep(guess,{
 'first_30_seconds':section([fact('案例重建：显示问题→输入大众可能回答→匹配常见答案得分；不是事实知识判对错。','TN-GUESS','TN-GUESS-CASE')],['开局教程/昵称、键盘、首题、实际计时长度','本地语言词表和第一答案接受规则']),
 'first_5_minutes':section([fact('官方案例链：限时输入多个答案→与对手分数比较→领取硬币/进度→开启新题。','TN-GUESS-CASE')],['五分钟题数、赛制、首次广告/商店入口','对手真人或AI、网络掉线流程']),
 'core_input':section([fact('案例明确为键入答案；商店/官网也使用this-or-that营销措辞，不据此认定全部为二选一。','TN-GUESS-CASE','TN-GUESS-STORE')],['拼写纠错、同义词、重复答案、敏感词处理','移动输入法遮挡及发送入口']),
 'success':section([fact('匹配更常见回答得更多分，并以分数争胜/提高排名。','TN-GUESS','TN-GUESS-CASE')],['每题得分公式、平局、局数、晋级门槛']),
 'failure':section([],['无匹配答案反馈、超时/分数落败具体结算','断网判负、无效输入惩罚']),
 'retry':section([fact('案例描述继续新题/新比赛的复玩循环。','TN-GUESS-CASE')],['重赛同题还是新题、免费次数、广告复活']),
 'mid_term_loop':section([fact('胜局与硬币用于角色/装扮等成长；题库复玩和排名是案例所述长期目标。','TN-GUESS-CASE')],['题库授权/调查来源、题目去重、难度','每种语言人群答案分布与公平性']),
 'ui':section([],['题目/倒计时/对手分数/键盘的实际摆放','答案反馈动画、昵称隐私、音频']),
 'ads_economy':section([fact('发行商案例列装扮/去广告/题包IAP，商店标广告与内购。','TN-GUESS-CASE','TN-GUESS-STORE')],['当前商品价格、广告位置/频率、奖励与价格曲线','不使用玩家评论推导固定广告节奏']),
 'devices':section([fact('发行商官网与商店包com.qoni.guesstheiranswer相连；官方案例声称支持离线单人。','TN-GUESS','TN-GUESS-CASE','TN-GUESS-STORE')],['离线/在线模式切换、真实PvP机制','真机键盘、最低系统与性能'])
},['TN-GUESS','TN-GUESS-CASE','TN-GUESS-STORE'],['官网/案例/商店交叉说明骨架，实时PvP与离线宣传的实现边界未核实。','数据来源与对手身份不能从营销文案推定；未观看Trailer。'],['记录一道题的输入、接受/拒绝答案和计分','测试重复/同义词/拼写错误','完整一局胜负、复玩与离线模式'])

def add_browser_observation(c,text,paths,confirmed=False,status='PARTIAL'):
    c['direct_play'].update(status=status,confirmed_gameplay_input=confirmed,evidence_paths=paths,
                            observed_scope=text,session_log='evidence/session.json',complete_first_30_seconds=False,
                            complete_first_5_minutes=False)
    c['known'].append(fact(text,'BROWSER-SESSION',verification='DIRECT_OBSERVATION_LIMITED'))

add_browser_observation(paint,'桌面访问官方印地语页面，等待后游戏区仍空白，未见iframe/canvas；未执行棋盘输入。',
 ['evidence/screenshots/p01-paint-master-loaded.png'],False,'LOAD_ATTEMPT_ONLY')
add_browser_observation(level,'进入了地图菜单、新内容YES/NO弹窗和首次关卡场景；最后截图有角色与出口，但没有角色位移前后对照，不能确认核心输入生效；不计完成试玩。',
 ['evidence/screenshots/p03-level-devil-loaded.png','evidence/screenshots/p03-level-devil-after-wait.png',
  'evidence/screenshots/p03-level-devil-front-space.png','evidence/screenshots/p03-level-devil-character-moved.png'],False,'PARTIAL_ENTRY_ONLY')
add_browser_observation(drive,'在官方Poki网页运行区执行ArrowRight按住2000ms，前后截图显示车辆从起点平台移动至格纹终点附近；未记录结算、失败或重试，不能认定通关。',
 ['evidence/screenshots/p03-drive-mad-ready.png','evidence/screenshots/p03-drive-mad-forward-2s.png'],True,'PARTIAL_GAMEPLAY_CONFIRMED')

S['BROWSER-SESSION']=dict(source_id='BROWSER-SESSION',source_url='evidence/session.json',title='本次浏览器命令与截图日志',
 accessed_at=DATE,published_at=U,evidence_type='DIRECT_OBSERVATION_LIMITED',access_method='existing_playwright_core_and_cached_chromium',
 access_note='运行浏览器正常页面，不注入游戏状态、不抓专有源码；只确认截图可见内容；从未读取cookies。',video_watched=False)

PLATFORMS=[('P01','Coolmath Games'),('P02','CrazyGames'),('P03','Poki'),('P04','Playgama'),('P05','Azur Games'),('P06','TapNation')]

def counts():
    return dict(cards=len(CARDS),platforms=len(PLATFORMS),unique_title_groups=23,
      unique_title_groups_caveat='Piece of Cake两条仅按同名暂列一组，身份/版本等价UNKNOWN；其余不因家族相似合并。',
      deep_analysis_platform_records=sum(c['deep_analysis'] is not None for c in CARDS),
      complete_direct_playthroughs=0,complete_direct_first_30_seconds=0,complete_direct_first_5_minutes=0,
      partial_confirmed_core_input_games=1,partial_entry_only_games=1,load_attempt_only_games=1,
      browser_attempted_games=3,secondary_reconstruction_deep_analyses=12,
      secondary_reconstruction_with_partial_gameplay_supplement=1,official_videos_watched=0,
      cards_without_confirmed_core_input=23,
      per_platform={p:dict(cards=sum(c['platform_id']==p for c in CARDS),deep_analyses=sum(c['platform_id']==p and c['deep_analysis'] is not None for c in CARDS)) for p,_ in PLATFORMS})

def ref_links(ids):
    return '；'.join(f'[{s}]({S[s]["source_url"]})' for s in ids)

LABELS={'first_30_seconds':'首次30秒','first_5_minutes':'首次5分钟','core_input':'核心输入','success':'成功','failure':'失败','retry':'重试','mid_term_loop':'中期循环','ui':'UI与反馈','ads_economy':'广告与经济','devices':'设备与运行'}

def render_platform(pid,name):
    cs=[c for c in CARDS if c['platform_id']==pid]
    out=[f'# {pid}｜{name} 具名作品证据卡',f'访问日期：{DATE}。4张卡、2份深析；深析均为 **SECONDARY_RECONSTRUCTION**，时间字段UNKNOWN。',
         '移动发行商目录仅作历史发行样本；所有作品存在性/评分均不能证明当前采购、成功率或开发者回款。'
         if pid in ('P05','P06') else '本页记录官方具名游戏与教学，不宣称热榜排名、采购需求或收益。',
         '机读权威数据：[benchmarks.json](benchmarks.json)；口径：[methodology.md](methodology.md)。',
         '| 作品 | G01—G10映射 | 深析 | 直接观察范围 |','|---|---|---|---|']
    for c in cs:
        out.append(f'| {c["name"]} | {", ".join(c["game_id"]) or "NONE"} | {"有" if c["deep_analysis"] else "无"} | {c["direct_play"]["status"]} |')
    for c in cs:
        out += ['',f'## {c["name"]}',f'记录键：`{c["benchmark_id"]}`。家族：{", ".join(c["game_id"]) or "NONE"}；{c["mapping"]["explanation"]}',
                f'官方精确URL：[{c["source_url"]}]({c["source_url"]})。访问：{DATE}；主来源发布日期：{c["published_at"]}；渠道版本发行：{c["game_release_date"]}。',
                f'证据类型：`{c["evidence_type"]}`。指标口径：{c["metric_definition"]}',
                f'官方短摘要：{c["official_summary"]}',f'选择理由（分析推断）：{c["selection_rationale"]["text"]}',
                '来源：'+ref_links(c['source_ids'])+'。','反证/边界：']
        out += ['- '+t for t in c['counter_evidence']]
        out += ['','已知：']+[f'- [{f["verification"]}] {f["text"]}（{ref_links(f["source_ids"])}）' for f in c['known']]
        if c['metrics']:
            out += ['','指标快照（不得外推）：']
            out += [f'- {m["name"]}：{m["value"]}。{m["metric_definition"]} 窗口：{m["observation_or_reporting_window"]}。' for m in c['metrics']]
        out += ['','商业UNKNOWN：本作净收入、授权费、分成、采购意愿、实际回款、成功概率均UNKNOWN。',
                '直接观察：'+c['direct_play'].get('observed_scope','未执行本作；官方描述不是亲测。')]
        for p in c['direct_play']['evidence_paths']:
            out.append(f'- [本次截图：{Path(p).name}]({p})')
        d=c['deep_analysis']
        if d:
            out += ['', '### 深度流程分析', '**SECONDARY_RECONSTRUCTION**。'+d['timing']['basis'],
                    '教学交叉来源：'+ref_links(d['sources_crosscheck']['source_ids'])+'。']
            out += ['- 证据缺口：'+g for g in d['sources_crosscheck']['gaps']]
            for k,v in d['sections'].items():
                out += ['',f'**{LABELS[k]}**']
                out += [f'- 可核实描述：{f["text"]}（{ref_links(f["source_ids"])}）' for f in v['known']]
                if not v['known']:out += ['- 可核实描述：UNKNOWN（本项没有足够官方细节或直接证据）。']
                out += ['- UNKNOWN：'+x['field']+'。' for x in v['unknown']]
                out += ['- HYPOTHESIS：'+x['text'] for x in v['hypotheses']]
            out += ['','**自拟待测路径（HYPOTHESIS，不是原作轨迹）**']
            out += [f'{i}. {a}。' for i,a in enumerate(d['next_direct_probe']['actions'],1)]
            out += ['', '官方视频：观看0；没有虚构视频时间码或回放。']
        out += ['', '**结论：EVIDENCE_COLLECTED；关键规则/经济未知，不能READY_FOR_BUILD。**']
    out += ['','## 本页来源登记','URL及日期逐条保存于JSON；更新日期和渠道版发行日期均不冒充文章发布日期。']
    for sid in dict.fromkeys(s for c in cs for s in c['source_ids']):
        s=S[sid];out += [f'- {ref_links([sid])}：发布日期 {s["published_at"]}；更新 {s.get("updated_at",U)}；访问 {DATE}。{s["access_note"]}']
    return '\n\n'.join(out).replace('|\n\n|', '|\n|')+'\n'

METHODOLOGY='''# 对标方法、证据口径与本次缺口

访问日期统一为 **2026-10-21**（Asia/Shanghai）；浏览器日志保存实际UTC时间。只写 `F:\\CoCreateGame\\research\\benchmarks\\`。已读根目录MASTER_HANDOFF.md、AGENTS.md及data/platforms.json；用户指定不写STATUS、不写games，优先于通用更新STATUS约定。没有游戏实现、付费安装、投稿、签约或对外发信。

## 交付与计数

- 六平台每家4张具名官方证据卡，共24条平台—作品记录；每家2份深析，共12条。
- 24条按标题暂归23组：Piece of Cake在P02/P04各有官方关联证据，但开发者显示名、渠道发行时间、控制描述不同，版本/权利主体等价UNKNOWN。
- **完整直接试玩0；完整首30秒0；完整首5分钟0。确认核心输入的局部直接操作1款（Drive Mad）。**
- Level Devil为PARTIAL_ENTRY_ONLY：地图、弹窗、首次关卡场景，不具备角色位移前后对照，不计实玩完成。Paint Master为LOAD_ATTEMPT_ONLY：游戏区域空白。浏览器共尝试3款，日志中的多次命令不算更多作品。
- 12份完整流程结构均标SECONDARY_RECONSTRUCTION，其中Drive Mad附局部直接操作；并非另有12份直接回放。24卡中23款没有确认核心输入。官方视频实际观看0。

## 选样与范围

优先采用platforms.json列出的具名游戏。P01、P02、P03、P04与P06各保留包内四例，准确纠正Playgama Good Sort和Piece of Cake、CrazyGames Deadly Descent的真实URL。P05把Block/Arrow/Sort品类占位换成Color Sort Puz、Tower Craft、Stack Ball、Bottle Jump 3D，全部有Azur官网具名作品/历史案例证据，另用发行商商店核实包名及描述。P05/P06目录是历史样本，不是2026最新下载榜或采购榜。

家族映射是分析判断，不是官方分类。game_id恒为数组，元素只能G01—G10；空数组表示NONE并说明。Blocky Blast、Stack Ball、Bottle Jump不强行归类。Tiny Fishing只映射G07成长/离线邻接，Thief Puzzle只映射G04机关/路径邻接。样本没有覆盖G10，不增加平台或候选来补数量；G10仍有待另行具名补证。

## 可机读结构与追溯

benchmarks.json顶层为metadata、summary、sources、benchmarks、gaps。每卡含platform_id/game_id/name/source_url/accessed_at/published_at/evidence_type/metric_definition/deep_analysis_source。来源ID只用于引文，不是新游戏ID。每条已知陈述附source_ids和verification；每个深析维度分别存known、unknown、hypotheses。未知值显式写UNKNOWN，不用空字符串、0或相邻作品参数代替。

published_at是文章/页面发布日期；无明确日期即UNKNOWN。game_release_date单独表示官网列出的本渠道版Release，只有月份时不补日。updated_at是页面或商店更新日期，不能冒充首发。accessed_at为本次请求日期，不保证web后台缓存也在当天刷新；CG-ARROW的缓存/重定向专门记录。

来源仅采用官方平台、发行商文章及发行商商店描述；商店是身份/操作的辅助证据，不新增发行目标。Fancade域Wiki标DEVELOPER_HOSTED_COMMUNITY_WIKI，托管官方不等于每个编辑者是开发者，只交叉确认输入，保留版本差异。不用玩家评论确立游戏规则，也没有使用第三方收益估算。官方文案也可能矛盾或有营销修辞，矛盾不擅自“修好”。

## 流程重建和时间纪律

12份深析每份包含首次30秒、首次5分钟、核心输入、成功、失败、重试、中期循环、UI、广告经济、设备。没有连续轨迹，30秒/5分钟字段一律UNKNOWN；“首次30秒”下的链只表示根据官方规则重建的操作依赖，不表示30秒内确曾发生。未知关数、教程次序、动画和经济均逐项列出。自拟验收路径单列HYPOTHESIS，不是对标观察结论。

本次没有观看官方视频，页面出现Video/Gameplay Video/Trailer不当成观看，不写视频秒数。官方教学交叉证据优先：Suika有游戏教学+官方攻略；Drive Mad有Poki教学+开发者域Wiki；Color Sort Puz有2023官方案例+署名商店；Stack Ball有官网目录+署名商店；TapNation两深析有官网教学+官网直链商店（Guess另有官方案例）。Paint Master、Arrow Escape、Screw Out、Arrow Puzzle、Good Sort主要是单一平台教学，明确保留独立交叉来源缺口；同站翻译不是独立证据。

## 浏览器证据

使用现有 `F:/beautiful/node_modules/playwright-core` 和本机缓存Chromium 149.0.7827.55（目录chromium-1228），不改F:\\beautiful，不安装浏览器。Windows桌面headless，viewport1365×900；没有Android/iOS真机。正常访问平台页面、发送鼠标/键盘事件、保存可见截图和命令日志，没有注入关卡状态或复制专有游戏源码。

Poki英文URL实际浏览时自动转到同站/zh/页面（保留最终URL）。第一次截图的广告休息/Preparing和空白不能证明广告真播放，更不能当普遍平台阻断。Drive Mad后来加载，ArrowRight保持2000ms前后车辆位置可见变化；后图接近格纹终点但没有结算，不能宣称过关。Level Devil在弹窗及入口花费多次输入，最后仅见首关场景，停止继续操作；不把命令名character-moved当作位移已证实。Paint Master未见运行棋盘。

evidence/session.json保留命令、实际URL、canvas数量、页面错误和截图相对路径。截图是本次页面观察而非商店宣传图。证据文件名是采集时标签，不是通过断言；以可见画面和这份裁决为准。没有视频录像，不能用离散截图补出未观察到的中间过程。

浏览器已通过context.close正常关闭；随后退出仍等待stdin的采集脚本进程，未发现本次浏览器/profile进程残留。临时profile/cache/tmp仅在evidence/runtime下；绝对路径已核对，但自动审批以“blocked by policy”拒绝递归删除，没有给出更具体原因。因此该本机目录仍在，**交付打包必须排除evidence/runtime/及其全部子项**，不得收录session cookies/cache。清理结果另存evidence/cleanup.json；delivery_manifest.json只枚举可交付文件。browser-probe.cjs和session.json及截图保留；旧名browser-session.json统一更名为session.json，不改写已采集事件。

## 指标与反证

页面存在性→平台关联；评分/投票→页面用户反馈；历史案例→发行和运营经验；商店下载档位→某商店累计安装门槛；任何一项都不等于当下采购、真实新作成功率、净收入或开发者到账。未建立热榜名次或DAU序列。Playgama的daily leaderboard人数与匿名榜名口径不明，未当活跃用户数；正文性能“完美/无延迟”未当实测。

Color Sort Puz案例2023-02-09自述累计总收入超过150万美元、支出超过100万美元，属于历史项目公司口径；成本范围、税、回收顺序、开发者份额不全，禁止相减作为利润。该案例中两次免费撤销加激励广告三次和商店无限撤销矛盾，当前规则UNKNOWN。Guess Their Answer的实时PvP与离线宣传、答案“人群”样本与授权都不明。Screw Out暂存满即失败/再拆才失败边界不明。均不应自动流入施工规则。

## 终审可用结论与未完成项

存在性和官方描述可引用；**P0没有本次直接可观察的G01/G02核心规则轨迹，G04 Paint Master也没有实玩**。这构成后续施工阻塞，不可把本库标READY_FOR_BUILD。其他agent的research/playthroughs/G04可由主控交叉引用，本轮未读取/修改其目录，不能把其未来结果计入本次数量。

接下来优先补G01/G02合法/非法操作、失败和重试的直接证据；再补G04的覆盖/机关规则；补每深析连续首30秒/5分钟、明确版本、实际广告触发与真机输入；解决单源教学与版本冲突。市场需求、收益、合同及独立质量评审仍独立进行，不从这里推导开发许可。
'''

def validate(data):
    assert len(CARDS)==24
    assert len({c['benchmark_id'] for c in CARDS})==24
    assert len([c for c in CARDS if c['deep_analysis']])==12
    for pid,_ in PLATFORMS:
        assert sum(c['platform_id']==pid for c in CARDS)==4
        assert sum(c['platform_id']==pid and c['deep_analysis'] is not None for c in CARDS)==2
    for c in CARDS:
        assert all(g in {f'G{x:02}' for x in range(1,11)} for g in c['game_id'])
        assert c['accessed_at']==DATE and c['ready_for_build'] is False
        assert all(s in S for s in c['source_ids'])
        for p in c['direct_play']['evidence_paths']:assert (ROOT/p).is_file(),p
        d=c['deep_analysis']
        if d:
            assert set(d['sections'])==set(LABELS)
            assert d['timing']['first_30_seconds']==d['timing']['first_5_minutes']==U
            for v in d['sections'].values():
                assert v['unknown']
                for f in v['known']:assert f['source_ids'] and all(s in S for s in f['source_ids'])

def main():
    data=dict(metadata=dict(schema_version='1.0.0',title='AI Game Foundry official benchmark evidence',
         accessed_at=DATE,timezone='Asia/Shanghai',scope_platform_ids=[p for p,_ in PLATFORMS],
         scope_game_ids=[f'G{x:02}' for x in range(1,11)],build_authorized=False,
         write_root=str(ROOT),methodology='methodology.md',
         delivery_exclude_paths=['evidence/runtime/'],
         local_runtime_cleanup='NOT_REMOVED_POLICY_REJECTION; exclude from delivery; see evidence/cleanup.json'),summary=counts(),sources=list(S.values()),benchmarks=CARDS,
         gaps=[dict(severity='BLOCKER',item='G01/G02缺直接合法/非法操作、失败与重试观察，G04 Paint Master未加载棋盘。'),
               dict(severity='BLOCKER',item='12份深析缺完整定时轨迹；关键规则/经济UNKNOWN，不是可施工档案。'),
               dict(severity='MAJOR',item='五份深析缺独立官方交叉来源/实际已观看视频；Arrow Escape有缓存和重定向。'),
               dict(severity='MAJOR',item='Color Sort Puz撤销与合法移动文本冲突；Screw Out失败边界；同名Piece of Cake版本差异。'),
               dict(severity='MAJOR',item='没有Android/iOS真机；广告触发与后期成长未经直接验证。'),
               dict(severity='MINOR',item='24卡未覆盖G10；不增加ID，后续另补具名装扮作品。')])
    validate(data)
    (ROOT/'benchmarks.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'methodology.md').write_text(METHODOLOGY,encoding='utf-8')
    for pid,name in PLATFORMS:(ROOT/f'{pid}.md').write_text(render_platform(pid,name),encoding='utf-8')
    print(json.dumps(data['summary'],ensure_ascii=False,indent=2))

if __name__=='__main__':main()
