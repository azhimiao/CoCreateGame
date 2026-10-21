"""Materialize the reviewed, Chinese-language channel research ledger."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-10-21'

SOURCES = [
 ('S01','P01','投稿和非独家许可','https://www.coolmathgames.com/submit-a-game'),
 ('S03','P02','Basic/Full 发行','https://docs.crazygames.com/'),
 ('S06','P03','测试阶段和参考指标','https://developers.poki.com/guide/how-testing-works'),
 ('S07','P03','投稿表单','https://developers.poki.com/guide/share'),
 ('S08','P03','独家及非独家合作','https://developers.poki.com/guide/revenue-deal-types'),
 ('S10','P04','注册和分发流程','https://wiki.playgama.com/playgama/quick-start'),
 ('S11','P04','SDK与发行覆盖的区别','https://wiki.playgama.com/playgama'),
 ('S13','P05','投稿和有条件买量测试','https://azurgames.com/publish-with-us/'),
 ('S14','P06','合作和评估流程','https://www.tap-nation.io/publishing/'),
 ('S16','P03','原创性与AI内容','https://developers.poki.com/guide/content-player-safety'),
 ('S19','P02','Basic结束条件','https://docs.crazygames.com/resources/basic-launch-metrics/'),
 ('S20','P02','技术要求','https://docs.crazygames.com/requirements/technical/'),
 ('S21','P02','结算','https://docs.crazygames.com/payouts/'),
 ('S22','P02','FAQ及权利','https://docs.crazygames.com/faq/'),
 ('S23','P03','技术要求的当前地址','https://developers.poki.com/guide/requirements-quality'),
 ('S24','P03','结算流程','https://developers.poki.com/guide/payouts-billing'),
 ('S25','P04','上传包和排除渠道','https://wiki.playgama.com/playgama/submitting-a-game'),
 ('S26','P04','技术及统计限制','https://wiki.playgama.com/playgama/game-requirements/technical-requirements'),
 ('S27','P04','权利说明','https://wiki.playgama.com/playgama/faq/general'),
 ('S28','P04','分成及结算','https://wiki.playgama.com/playgama/faq/payments-and-statistics.md'),
 ('S29','P04','FAQ联系入口','https://wiki.playgama.com/playgama/faq'),
 ('S30','P06','提交表单和响应说法','https://www.tap-nation.io/submit/'),
 ('S31','P03','测试平台使用条款（当前要求页所链PDF）','https://app.poki.dev/2024.03.13_Terms_and_Conditions_Poki_for_Developers.pdf'),
 ('S32','P03','外部资源逐案审批政策','https://developers.poki.com/guide/external-resources-policy'),
]

# These are paraphrased public facts, never signed contract terms or measured outcomes.
CLAIMS = [
 ('C01','S01','接受合适HTML5思考类游戏，可能购买非独家托管许可。','采购方式；并非采购承诺'),
 ('C02','S01','其专用版本须移除广告、外链、开发者回传统计及姓名输入。','版本要求'),
 ('C03','S03','Basic禁变现，Full需要进一步审核和SDK；通过不是自动发生。','发行阶段'),
 ('C04','S19','Basic同时达到至少7天和500 plays才正常结束；不足500则21天结束。','plays不是独立玩家数'),
 ('C05','S20','总包250MB/1500文件；初始50MB，移动首页20MB；不接SDK时按总包计初始。','官方最大值，内部预算应更低'),
 ('C06','S21','最低结算100欧元；合同NET60，文档称通常争取次月10日前处理。','应计收入门槛及处理时间；非到账保证'),
 ('C07','S22','FAQ说明保留游戏所有权并允许已有其他发行，但仍须持有发行权。','公开FAQ；实际协议另审'),
 ('C08','S22','FAQ初审列明PEGI-12，并将面向儿童的内容列为拒绝原因之一。','内容定位；不是自行取得分级认证'),
 ('C09','S06','Player fit样本500玩家，健康参考平均3分钟以上及25%以上play超过3分钟；C2P在Web fit测量。','平台测试参考；不外推至其他渠道'),
 ('C10','S07','投稿接受可访问试玩链接或实机视频，要求3张实际游戏截图，每张最大5MiB。','表单字段'),
 ('C11','S08','偏好Web独家，默认5年为示意条件；移动/PC通常排除在外；非独家可一次性许可且无同等推广分成。','意向说明；签署协议决定实际权利'),
 ('C12','S16','AI可辅助但需原创、审核、测试；高度相似作品和饱和题材可能被拒。','平台选品政策；非普遍法律结论'),
 ('C13','S23','需桌面/手机/平板适配，桌面覆盖16:9，资产本地打包，存储异常可玩；SDK事件不得连续重复。','技术验收要求'),
 ('C14','S24','通过银行或PayPal结算，金额由协议定义；页面不提供统一费率。','流程；费率UNKNOWN'),
 ('C15','S10','开发者注册后接入Bridge、上传、审核，再按报表结算。','流程；无流量保底'),
 ('C16','S11','Playgama不替开发者向Poki和CrazyGames投稿；SDK支持不等于取得发行。','发行覆盖边界'),
 ('C17','S25','ZIP根目录index.html，总解压文件最大300MB；可排除渠道，上传后仍需审核。','文件限制和配置能力'),
 ('C18','S26','必须接Bridge，不得以外部注册阻断游戏，不内嵌GA4等第三方统计。','技术要求；不能误解为禁止平台自身统计'),
 ('C19','S27','FAQ称开发者保留权利并授予合作平台转授权。','公开摘要；注册条款仍待逐条审阅'),
 ('C20','S28','合作站点分发按月净收入分段70%/80%/90%；Playgama站内及iframe伙伴网络固定50%。','不同收入流；Net Revenue定义仍需合同确认'),
 ('C21','S28','提现门槛100美元，个人收款依国家和司法辖区个案决定。','门槛；不保证本团队可收款'),
 ('C22','S29','开发支持邮箱developer.success@playgama.com公开列于FAQ。','公开联系入口；本次未发送邮件'),
 ('C23','S13','表单收视频和APK等资料；先内部评估，再有条件买少量流量看留存/CPI。','合作流程；金额和最低预算UNKNOWN'),
 ('C24','S13','官网列publishing@azurgames.com，并称首阶段两天反馈。','联系方式和宣传时效；非实际响应实测'),
 ('C25','S14','接受概念/原型/现有构建；称两周内评估，匹配后协商分成、里程碑和创作权。','流程；不是固定采购价'),
 ('C26','S14','成功发行后可能给买断选项，价格和触发细节未公开。','可选交易；非保证收购'),
 ('C27','S30','实际表单要求上月收入、D1和平均时长；称7个工作日内回复。','字段/响应说法；与两周评估须区分'),
 ('C28','S31','测试平台使用受其条款约束；测试非保证且无报酬；上传授予测试目的Web许可；预览链接不得用于竞争平台分发。','PDF第1—3页§1.4—1.5/3.3/4.2—4.3/5.1；长期发行另议'),
 ('C29','S32','外部服务默认阻止，部分非Google统计可逐案审批；技术CSP放行与条款适用边界需确认。','外部资源政策；不是已取得第三方统计豁免'),
 ('C30','S26','禁止浏览器页滚动，允许游戏内自定义内容滚动；主场景仍须可单手操作且不依赖额外滚动/滑动，大型场地类有例外。','技术§5.2与§5.5应同时满足；普通六盘谜题不默认属于大型场地例外'),
]

LOCATORS = {
 'S01':'How to Submit a Game / game requirements', 'S03':'Launching on CrazyGames / Basic Launch and Full Launch',
 'S06':'The five steps / Player fit test; What to aim for', 'S07':'Share a playable build / Show us what it looks like',
 'S08':'Web exclusive / Good to know / Non-exclusive', 'S10':'Steps 1–5', 'S11':'SDK / paragraph after partner list',
 'S13':'Game Submission Form / We received your game / Write us', 'S14':'How It Works / Buy-out option',
 'S16':'Quality guidelines / Working with AI / Oversaturation', 'S19':'The process and your dashboard / Duration',
 'S20':'File Size & Count Limits / SDK Integration', 'S21':'Payment Methods / Payment Timeline & Thresholds',
 'S22':'Can I publish... / Do I still own... / Step A Initial QA', 'S23':'Hard requirements / Technical standards',
 'S24':'How you get paid / What determines the amount', 'S25':'Step 3 / Game Archive and Distribution',
 'S26':'Technical requirements, items 1–5; scrolling clauses 5.2 and 5.5', 'S27':'Who owns the rights to the game I upload?',
 'S28':'How much will I earn? / When can I withdraw? / I am an individual', 'S29':'final support paragraph',
 'S30':'hero response time / Your game fields', 'S31':'PDF pp.1–3, clauses 1.4–1.5, 3.3, 4.2–4.3, 5.1',
 'S32':'Possible exceptions / Getting a resource approved',
}

CHANNELS = {
 'P01': dict(name='Coolmath Games', role='非独家许可采购', stage='HTML5可玩候选；展示版可在采购后依要求调整',
             contact='官方投稿表单；不猜测采购个人邮箱', entry='https://www.coolmathgames.com/submit-a-game',
             claims=['C01','C02'], sdk='无平台SDK通用承诺；独立clean构建，不加载广告/外链/开发者统计。',
             traffic='编辑采购意愿，不是承诺购买、固定价或独立玩家数量。',
             payment='报价、账期、退款/违约扣款、续约、验收权UNKNOWN，正式询价后才能建应收。',
             rights='核对托管域名、期限、地域、转授权、源代码交付；保留共用机制库。'),
 'P02': dict(name='CrazyGames', role='Basic玩家测试及Full分成', stage='完成基本QA的HTML5构建，不是只有GDD',
             contact='开发者门户及官方FAQ Contact', entry='https://developer.crazygames.com/',
             claims=['C03','C04','C05','C06','C07','C08'], sdk='Basic可无SDK但禁广告/IAP；Full接独立CrazyGames适配器。',
             traffic='有限测试；实际展示/启动/游玩留存分别记录，晋级基准不等于采购保证。',
             payment='公开100欧元最低结算，NET60；较早处理只是文档目标。费率、银行费用及退款/追回条款另审。',
             rights='FAQ所有权不替代Terms；收款地区资格、内容定位、已有排他许可须审。'),
 'P03': dict(name='Poki', role='精选测试及可选独家/非独家许可', stage='可玩无登录链接或实际玩法视频，3张实机截图',
             contact='官方share表单/获得权限后的开发者门户', entry='https://developers.poki.com/guide/share',
             claims=['C09','C10','C11','C12','C13','C14','C28','C29'], sdk='Web Fit/发行需Poki SDK；本地打包资产和字体，桌面16:9及手机布局分开验收。测试条款和正式发行协议分开；默认零第三方统计。',
             traffic='有分阶段真人/页面测试，营销支持依协议；500是Player fit玩家样本，不能与CrazyGames的plays混用。',
             payment='协议定义分成/一次性许可额；银行/PayPal；统一比例、门槛、付款周期和退款规则UNKNOWN。',
             rights='Web独家与P01/P02/P04同一IP分发原则上冲突；默认5年仅指示值，合同优先。'),
 'P04': dict(name='Playgama', role='HTML5及合作站点分销', stage='HTML5 ZIP、Bridge及元数据，经过QA/审核',
             contact='developer.success@playgama.com；官方开发者门户', entry='https://developer.playgama.com/',
             claims=['C15','C16','C17','C18','C19','C20','C21','C22','C30'], sdk='Bridge独立版本；不混装Poki/CrazyGames SDK；关闭GA4等第三方遥测。核心游玩不得依赖额外滚动，菜单内容内滚不构成主场景豁免。',
             traffic='网络总体覆盖和SDK可支持列表都不等于单款保证流量，也不替代Poki/CrazyGames单独审核。',
             payment='区分合作站点分发净收入分段与站内/iframe固定50%；100美元门槛；净额扣除和支付账期/追回仍需协议。',
             rights='注册就接受条款，不能为研究自行注册；撤回游戏不等于服务器删除；核对转授权/排除渠道/终止及删除。'),
 'P05': dict(name='Azur Games', role='移动发行和有条件买量测试', stage='原型视频、APK链接、团队信息；先内部评估',
             contact='publishing@azurgames.com；官方投稿表单', entry='https://azurgames.com/publish-with-us/',
             claims=['C23','C24'], sdk='发行商评估后指定归因/数据SDK；Android签名、ABI、目标API与SDK版本需书面确认。',
             traffic='只有通过内部评估后才可能购买测试流量；预算、样本、国家、停止规则UNKNOWN。',
             payment='没有公开本团队CPI、分成、报价、回收顺序或结算承诺；不按公司总安装数预测收入。',
             rights='签署前核IP、移动排他范围、共用库保留、买量回收、数据访问、退出和迭代义务。'),
 'P06': dict(name='TapNation', role='移动发行运营及可选买断', stage='概念/原型/build，但当前表单包含收入和D1等必填字段',
             contact='官方submit表单及Contact；不猜测私人邮箱', entry='https://www.tap-nation.io/submit/',
             claims=['C25','C26','C27'], sdk='开发平台可选不代表SDK兼容已验证；合作后锁定移动引擎/归因/广告/隐私配置。',
             traffic='合作评估、A/B/UA是能力描述；没有给本项目的保底测试/采购金额。',
             payment='分成、里程碑、买断价、回本优先级、付款及退款/追回UNKNOWN。',
             rights='官网表示协商创作权且可选买断；不得据此认为IP自动永久归团队。'),
}

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    source_items = [dict(source_id=i, platform_id=p, title=t, url=u, accessed_on=DATE,
                         published_on='UNKNOWN', locator=LOCATORS[i], evidence_type='OFFICIAL_DOCUMENT',
                         verification='WEB_CONTENT_READ', recheck_rule='BEFORE_SUBMISSION_AND_CONTRACT')
                    for i,p,t,u in SOURCES]
    dump(ROOT/'research/official-sources.json', source_items)
    source_map = {x['source_id']: x for x in source_items}
    claims = [dict(claim_id=i, source_id=s, source_url=source_map[s]['url'], platform_id=source_map[s]['platform_id'],
                   claim=c, accessed_on=DATE, published_on='UNKNOWN', metric_definition=m,
                   evidence_type='OFFICIAL_DOCUMENT', source_locator=LOCATORS[s], confidence='A_PUBLIC_PAGE_ONLY',
                   counter_evidence='官网公开描述不能证明本团队已经获批、实际付款或合同同等条款。',
                   recheck_rule='投稿/签约当日重核；宣传响应时效必须实测') for i,s,c,m in CLAIMS]
    dump(ROOT/'research/claims.json', claims)
    by_claim = {c['claim_id']: c for c in claims}
    docs = ROOT/'research/platforms'
    docs.mkdir(parents=True, exist_ok=True)
    for pid, item in CHANNELS.items():
        lines = [f"# {pid} {item['name']}｜官方渠道档案", '', f'核查：{DATE}（Asia/Shanghai）。状态：PUBLIC_ENTRY_VERIFIED；未注册、未提交、未联系。', '',
                 f"- 合作角色：{item['role']}。", f"- 允许阶段：{item['stage']}。", f"- 提交入口：{item['entry']}", f"- 公开联系：{item['contact']}。", '',
                 '## 已核实事实与口径', '']
        for cid in item['claims']:
            c = by_claim[cid]
            lines.append(f"- {cid}：{c['claim']} 口径：{c['metric_definition']}。[官方依据]({c['source_url']})")
        lines += ['', '## 交付及风险', '', f"技术：{item['sdk']}", '', f"流量：{item['traffic']}", '',
                  f"结算：{item['payment']}", '', f"权利：{item['rights']}", '',
                  f'作品证据卡与间接流程分析见 `../benchmarks/{pid}.md`；历史目录不当作当前采购榜。', '',
                  '## 仍需取得的证据', '',
                  '本团队的进入资格、当前协议全文/版本、付款主体和所在地可收款性、实际报价或分成、费用扣除、宣传和测试预算。全部为UNKNOWN。', '',
                  '后续投稿须先完成项目及权利审查；本轮只准备资料。来源发布时间UNKNOWN，访问日期不能充当政策生效日期。', '']
        (docs/f'{pid}.md').write_text('\n'.join(lines), encoding='utf-8')
    dump(ROOT/'research/channel-profiles.json', [dict(id=k, **v, checked_on=DATE) for k,v in CHANNELS.items()])
    print(f'Generated {len(source_items)} official sources, {len(claims)} claims, {len(CHANNELS)} channel profiles.')

if __name__ == '__main__': main()
