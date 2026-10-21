"""Compact source registry and INTERNAL raw hashes; no network or page copying."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'research'; RAW=R/'raw'; RAW.mkdir(exist_ok=True)
for source in sorted(R.glob('research_*.txt')):
    target=RAW/source.name
    assert source.resolve().is_relative_to(ROOT) and target.resolve().is_relative_to(ROOT)
    if target.exists():
        assert source.read_bytes()==target.read_bytes()
        source.unlink()
    else: source.rename(target)

def e(i,title,url,published,kind,locator,summary,metric,limits,record):
    raw=RAW/record
    return dict(claim_id=f'E{i:02}',title=title,source_url=url,published_at=published,
        accessed_on='2026-10-21',access_timezone='Asia/Shanghai',read_time_precision='date only; exact tool-call time UNKNOWN',
        evidence_type=kind,access='official page text read via web tool; no gameplay interaction',locator=locator,
        summary=summary,metric_definition=metric,confidence='A_OFFICIAL_PAGE_TEXT_ONLY',counter_evidence=limits,
        recheck='revisit before submission/dependency lock; dynamic claims require fresh dated record',
        internal_raw_record='research/raw/'+record,
        content_sha256=hashlib.sha256(raw.read_bytes()).hexdigest() if raw.exists() else 'UNKNOWN',
        content_hash_scope='saved web-tool response bundle, not canonical HTML and not gameplay state',
        summary_sha256=hashlib.sha256(summary.encode('utf-8')).hexdigest())

ev=[
e(1,'Arrow Puzzle — Green Train','https://playgama.com/game/arrow-puzzle','release 2026-04; update 2026-06','official game description; platform display signal','About Arrow Puzzle / How to Play / Developer / Categories',
  '官方页描述清空箭头、净空后点击移除、受阻点击损失生命及提示。页面存在类别和集合展示入口。','description and placement only; no verified rank, revenue, downloads or DAU','实际交互、首次流程、生命数、内部经济、成功率UNKNOWN。','research_0.txt'),
e(2,'Arrow Escape: Puzzle — SolvePlay (official Spanish page)','https://www.crazygames.com/es/game/arrow-escape-puzzle','release 2026-02; update UNKNOWN','official game description','Desarrollador / Características / Cómo jugar / Controles',
  '官方页确认SolvePlay作品与清场/方向/阻挡规则；正文轻触和Controls拖动表述矛盾。英文URL本轮重定向分类页。','existence and described rules; short-level phrasing is marketing, not measured duration','没有试玩；30秒/5分钟实测UNKNOWN；不同于Bravestars同名作。','research_more_0.txt'),
e(3,'CrazyGames publishing introduction','https://docs.crazygames.com/','UNKNOWN','official launch policy','Launching on CrazyGames / Basic Launch / Full Launch',
  '官方区分Basic与Full；Basic禁变现；Full需完整实施并基于指标决定是否晋级。','launch requirements, not guaranteed income or acceptance','单游戏收入、采购概率、实际通过率UNKNOWN。','research_more_1.txt'),
e(4,'Playgama Quick start','https://wiki.playgama.com/playgama/quick-start','UNKNOWN','official submission and SDK process','Steps 1–5',
  '官方流程为注册、Bridge集成、上传、QA审核与报表付款。','process requirements, not actual transaction','无本项目审核、合同或回款。','research_more_1.txt'),
e(5,'AZUR GAMES Publishing','https://azurgames.com/publish-with-us/','UNKNOWN','official submission and conditional testing process','Game Submission Form / We received your game / Public Test',
  '表单含视频和APK字段；先内审，可能再购买少量流量评估留存与CPI。','publisher-described process, not committed budget','Cocos指定SDK支持、预算、权利与实际测试结果UNKNOWN。','research_more_1.txt'),
e(6,'CrazyGames Technical requirements','https://docs.crazygames.com/requirements/technical/','UNKNOWN','official technical admission','File Size & Count Limits / SDK Integration',
  '总文件≤250MB、≤1500；初始下载≤50MB，移动首页≤20MB；无SDK时用总包计；Full需SDK。','official file/download limits; project build performance not measured','MB压缩口径须实际复核；本地游戏包尚不存在。','research_constraints.txt'),
e(7,'CrazyGames FAQ & Contact','https://docs.crazygames.com/faq/','UNKNOWN','official content/selection policy','rejection reasons: PEGI-12 / Content is targeted for kids',
  '官方拒绝项含不符合PEGI-12与面向儿童内容。本项目定位16+，不以内容评级当儿童定位。','selection boundary, not audience conversion data','未获得G01内容审核。','research_final_targeted.txt'),
e(8,'Playgama Technical Requirements','https://wiki.playgama.com/playgama/game-requirements/technical-requirements','UNKNOWN','official technical admission','items 1–10; analytics at item 3',
  '要求Bridge；禁GA4等第三方统计；root index、拉丁文件名、archive≤300MB及兼容/旋转等条件。','official requirements; no performance measurement','旧系统与候选引擎兼容未测试；Bridge具体锁版UNKNOWN。','research_constraints.txt'),
e(9,'Coolmath Games Submission','https://www.coolmathgames.com/submit-a-game','UNKNOWN','official submission/licensing policy','How to Submit / game requirements',
  '可能购买非独家许可；要求HTML5思考类，禁广告、外链、开发者回传与名字输入。','admission and potential transaction form, not actual paid licensing','G01报价、许可正文、付款UNKNOWN；本轮仅保留隔离预案。','research_constraints.txt'),
e(10,'Playgama Welcome','https://wiki.playgama.com/playgama','UNKNOWN','official distribution boundary','warning near How to start',
  '官方说明不代向Poki和CrazyGames发布；SDK兼容不代表另一平台审批。','distribution scope statement, not traffic promise','没有本项目合作站曝光/净收益。','research_more_0.txt'),
e(11,'Cocos Creator Download / 3.8.8','https://www.cocos.com/en/creator-download','2025-12-16 for listed 3.8.8','official engine release page','3.8.8 / 16 Dec 2025 / Install from Dashboard',
  '官网下载页列3.8.8与2025-12-16，选为确切候选；不声称已安装或是全球最新。','version listing, not installation/build/performance validation','PATH未发现可执行，全机安装状态NOT_VERIFIED，未编译。','research_final_targeted.txt'),
e(12,'Cocos engine v3.8.8 LICENSE.md','https://raw.githubusercontent.com/cocos/cocos-engine/v3.8.8/LICENSE.md','UNKNOWN','official source license','MIT License / copyright / permission',
  '该tag的引擎LICENSE.md是MIT，保留版权和许可；不覆盖编辑器及商店资产。','license scope of specified source file','编辑器EULA未知；原先LICENSE路径404，已改正确文件。','research_licenses_final.txt'),
e(13,'Noto CJK Sans LICENSE','https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/LICENSE','license version 2007-02-26; file date UNKNOWN','official font license','OFL1.1 / permissions and conditions',
  'OFL1.1可随软件嵌入，附许可与版权；不能单卖字体，改名/子集按保留名要求审查。','font license, not proof all font assets already cleared','字体文件、hash和子集尚未生产；main会变化。','research_more_0.txt'),
e(14,'TypeScript LICENSE.txt','https://raw.githubusercontent.com/microsoft/TypeScript/main/LICENSE.txt','UNKNOWN','official compiler source license','Apache License 2.0',
  'TypeScript官方主分支许可为Apache-2.0；随精确编译器版本锁定后重核。','license only; not compiler compatibility','Cocos随附TS确切版UNKNOWN；main非版本锁。','research_final_targeted.txt'),
e(15,'python-jsonschema COPYING','https://github.com/python-jsonschema/jsonschema/blob/main/COPYING','UNKNOWN','official validation-tool source license','COPYING / copyright Julian Berman / permission',
  '验证工具官方COPYING为MIT。本轮环境jsonschema4.26.0已实际用于schema验证，未随包分发第三方库。','license and local validation dependency, not production runtime','许可main与运行安装文件hash未锁；不声称维护活跃程度。','research_1.txt'),
e(16,'Cocos Publish from the Command Line','https://docs.cocos.com/creator/3.8/manual/en/editor/publish/publish-in-command-line.html','UNKNOWN','official build tooling documentation','Command Reference / Exit Codes / configPath',
  '文档支持--project与--build configPath；列退出码36成功、32参数错、34构建错。','documented command semantics only','没有实际运行Creator命令；未来需面板导出配置并验证产物。','research_final_targeted.txt')]
(R/'evidence.json').write_text(json.dumps(dict(recorded_date='2026-10-21',raw_policy='INTERNAL_ONLY_EXCLUDED_FROM_DISTRIBUTION',claims=ev),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raw_index=[dict(path='research/raw/'+p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),distribution='EXCLUDED') for p in sorted(RAW.glob('*.txt'))]
(R/'raw-index.json').write_text(json.dumps(dict(hash_scope='exact saved tool-response bytes; not canonical page HTML',records=raw_index),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert len(ev)==16 and all(x['content_sha256']!='UNKNOWN' for x in ev)
print('16 compact evidence records; internal raw moved and indexed; no network.')
