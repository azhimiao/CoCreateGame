"""Create an offline review index and a reproducible archive of preparation files."""
from __future__ import annotations
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
NAME = 'AI_Game_Foundry_Prepared_2026-10-21'

def read(path, default):
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else default

def build_index():
    status = read(ROOT/'data/preparation-status.json', [])
    validation = read(ROOT/'validation/preparation-report.json', {})
    sources = read(ROOT/'research/official-sources.json', [])
    benchmark_data = read(ROOT/'research/benchmarks/benchmarks.json', [])
    benchmarks = benchmark_data if isinstance(benchmark_data,list) else benchmark_data.get('benchmarks',benchmark_data.get('cards',[]))
    docs = {}
    for folder in [ROOT/'games', ROOT/'research', ROOT/'reviews']:
        for path in folder.rglob('*.md'):
            if not {'runtime','raw','node_modules','.git'}.intersection(path.relative_to(ROOT).parts):
                docs[path.relative_to(ROOT).as_posix()] = path.read_text(encoding='utf-8-sig')
    for name in ['STATUS.md','DELIVERY_REPORT.md','REQUIREMENTS_CHECKLIST.md','discrepancies.md','README.md']:
        path = ROOT/name
        if path.is_file(): docs[name] = path.read_text(encoding='utf-8-sig')
    def link(path, label):
        return f'<a href="{escape(path,quote=True)}" data-doc="{escape(path,quote=True)}">{escape(label)}</a>'
    project_html = []
    for game in sorted(status, key=lambda g:(g.get('preparation_batch','P9'),g['id'])):
        gid = game['id']
        p0 = game.get('preparation_batch') == 'P0'
        links = [link(f'games/{gid}/{name}', label) for name,label in
                 [('README.md','项目入口'),('00_Project_Charter.md','立项'),('01_Market_Evidence.md','证据'),
                  ('03_Full_GDD.md','设计'),('05_Levels_Economy.md','关卡'),('12_Falsifiability.md','停止条件')]
                 if (ROOT/'games'/gid/name).exists()]
        if (ROOT/'reviews'/f'{gid}-audit.md').exists(): links.append(link(f'reviews/{gid}-audit.md','独立审计'))
        if gid=='G04' and (ROOT/'research/playthroughs/G04/observation.md').exists():
            links.append(link('research/playthroughs/G04/observation.md','操作补证'))
        project_html.append(f'''<article class="project" data-batch="{escape(game.get('preparation_batch',''))}">
<div class="project-top"><span class="mono">{gid} / {escape(game.get('preparation_batch',''))}</span><span class="pill">{escape(game.get('display_status','待补证据'))}</span></div>
<h3>{escape(game.get('title',game.get('family',gid)))}</h3><p>{escape(game.get('decision_note',''))}</p>
<div class="doclinks">{' '.join(links)}</div></article>''')
    channel_html = []
    for p in read(ROOT/'research/channel-profiles.json', []):
        channel_html.append(f'''<tr><td><b>{p['id']}</b><br>{escape(p['name'])}</td><td>{escape(p['role'])}</td><td>{escape(p['rights'])}</td><td>{link('research/platforms/'+p['id']+'.md','官方档案')}<br>{link('research/benchmarks/'+p['id']+'.md','作品分析')}</td></tr>''')
    script_data = json.dumps(docs,ensure_ascii=False).replace('<','\\u003c')
    total_levels = sum(len(read(ROOT/'games'/g/'game-spec.json',{}).get('levels',[])) for g in ['G01','G02','G04'])
    html = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Game Foundry · 项目准备交付</title><style>
:root{--paper:#f4f3ed;--ink:#183e37;--muted:#65716a;--line:#d7ded4;--accent:#287c65;--soft:#e6ebdf}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.75 system-ui,'Microsoft YaHei',sans-serif}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}button{font:inherit;cursor:pointer}header{border-bottom:1px solid var(--line);background:#183e37;color:#fff}.top{max-width:1180px;margin:auto;padding:20px 32px;display:flex;align-items:center;justify-content:space-between;gap:20px}.wordmark{font-weight:760;letter-spacing:.04em}.top small{color:#b9d0c1}main{max-width:1180px;margin:auto;padding:0 32px 64px}.hero{padding:54px 0 34px;display:grid;grid-template-columns:1.5fr 1fr;gap:44px;align-items:end}.eyebrow{font-size:12px;letter-spacing:.12em;color:#4e7965;font-weight:750}h1{font-size:clamp(28px,4vw,46px);line-height:1.25;letter-spacing:-.035em;margin:12px 0 18px}h2{font-size:24px;margin:0}h3{font-size:20px;margin:12px 0 8px}.lead{color:var(--muted);max-width:660px}.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}.actions a{display:inline-block;padding:10px 18px;border:1px solid var(--ink);border-radius:5px;color:var(--ink)}.actions a.primary{background:var(--ink);color:white}.note{padding:23px;background:var(--soft);border-left:3px solid #638f69;font-size:14px}.note strong{display:block;font-size:16px;margin-bottom:8px}.stats{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.stat{padding:22px 16px 22px 0}.stat+.stat{padding-left:24px;border-left:1px solid var(--line)}.stat b{font-size:34px;line-height:1.3;font-weight:650;display:block}.stat span{font-size:13px;color:var(--muted)}section{padding-top:38px}.section-head{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:18px}.filters{display:flex;gap:6px}.filters button{border:1px solid var(--line);background:transparent;padding:5px 12px;border-radius:4px;color:var(--ink)}.filters button[aria-pressed=true]{background:var(--ink);border-color:var(--ink);color:#fff}.projects{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.project{background:#fffef9;padding:24px;border:1px solid var(--line);border-radius:6px}.project-top{display:flex;align-items:center;justify-content:space-between;gap:12px}.mono{font:12px ui-monospace,monospace;color:var(--muted)}.pill{font-size:11px;border:1px solid #c4cfba;padding:2px 8px;border-radius:20px;background:#f0f2e8}.project p{font-size:13px;color:var(--muted);margin:6px 0 18px}.doclinks{display:flex;gap:9px 16px;flex-wrap:wrap;font-size:13px}.tablewrap{overflow:auto;border:1px solid var(--line);border-radius:6px}table{width:100%;border-collapse:collapse;background:#fffef9;font-size:13px}th,td{text-align:left;padding:16px;vertical-align:top;border-bottom:1px solid var(--line)}th{background:var(--soft);font-weight:650}td:first-child{min-width:145px}td:last-child{min-width:90px}tr:last-child td{border-bottom:0}.resources{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.resource{border-top:2px solid #85a085;padding:15px 0}.resource a{font-weight:650}.resource p{font-size:13px;color:var(--muted);margin:8px 0}footer{margin-top:38px;padding-top:20px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}dialog{border:1px solid var(--line);border-radius:8px;max-width:1000px;width:calc(100% - 32px);height:90vh;padding:0;background:#fffef9;color:var(--ink)}dialog::backdrop{background:#0b251ed0}.reader-head{position:sticky;top:0;background:var(--soft);padding:12px 20px;display:flex;justify-content:space-between;gap:20px;align-items:center;border-bottom:1px solid var(--line)}.reader-head strong{font-size:13px;overflow-wrap:anywhere}.reader-head button{background:var(--ink);color:white;border:0;border-radius:4px;padding:5px 12px}pre{padding:24px;margin:0;white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.85 ui-monospace,'Microsoft YaHei',monospace}body.reading{overflow:hidden}[hidden]{display:none!important}@media(max-width:700px){main{padding:0 18px 40px}.top{padding:16px 18px;align-items:flex-start}.top small{font-size:10px}.hero{grid-template-columns:1fr;gap:18px;padding-top:32px}.stats{grid-template-columns:repeat(2,1fr)}.stat{padding:16px 12px!important}.stat:nth-child(3){border-left:0}.stat:nth-child(n+3){border-top:1px solid var(--line)}.projects,.resources{grid-template-columns:1fr}.project{padding:18px}.section-head{align-items:flex-start;flex-direction:column}td,th{padding:12px}.reader-head{padding:10px}pre{padding:16px;font-size:12px}}@media print{header,.filters,dialog,.actions{display:none}main{max-width:none}.projects{display:block}.project{break-inside:avoid;margin-bottom:10px}.tablewrap{overflow:visible}}
</style></head><body><header><div class="top"><div class="wordmark">AI GAME FOUNDRY</div><small>项目准备交付 / 2026.10.21</small></div></header><main>
<div class="hero"><div><div class="eyebrow">RESEARCH → SPECIFICATION → REVIEW</div><h1>先把游戏定义清楚。<br>再决定制造哪一款。</h1><p class="lead">六个渠道、十个游戏家族，以及三套优先项目施工档案。这里汇集官方证据、原创规则、关卡验证与独立审查，供下一步选品决策。</p><div class="actions">REPORT_LINK ARCHIVE_LINK</div></div><div class="note"><strong>本轮为开发前准备</strong>对标说明、实际观察与设计假设分别标注。数据验解通过代表规则可达；真人体验、渠道采纳、合同和收入仍需后续验证。<br>STATUS_LINK</div></div>
<div class="stats"><div class="stat"><b>SOURCE_COUNT</b><span>官方准入与商务来源</span></div><div class="stat"><b>BENCH_COUNT</b><span>具体作品证据卡</span></div><div class="stat"><b>03</b><span>优先项目施工档案</span></div><div class="stat"><b>LEVEL_COUNT</b><span>原创关卡规格及验解</span></div></div>
<section><div class="section-head"><h2>项目与审查结果</h2><div class="filters"><button data-filter="all" aria-pressed="true">全部项目</button><button data-filter="P0" aria-pressed="false">优先三项</button></div></div><div class="projects">PROJECTS</div></section>
<section><div class="section-head"><h2>六家渠道，各有进入条件</h2>ADAPTATION_LINK</div><div class="tablewrap"><table><thead><tr><th>渠道</th><th>合作方式</th><th>关键权利边界</th><th>证据</th></tr></thead><tbody>CHANNELS</tbody></table></div></section>
<section><div class="section-head"><h2>证据、风险与复核</h2><span class="mono">结构与数据校验：VALIDATION_RESULT</span></div><div class="resources"><div class="resource">DISCREPANCIES_LINK<p>结算口径、表单条件、平台范围及旧结论的修订。</p></div><div class="resource">RIGHTS_LINK<p>独家、转授权、共用机制库和素材许可的边界。</p></div><div class="resource">METHOD_LINK<p>实玩与间接分析如何区分，哪些证据仍未取得。</p></div><div class="resource">BUSINESS_LINK<p>包含失败项目的成本和净回款模型，不填假收入。</p></div><div class="resource">AUDIT_LINK<p>独立审查的问题、严重程度和下一步条件。</p></div><div class="resource"><a href="original-brief.html">原始总纲演示 ↗</a><p>保留输入版本，方便与本轮产物对照。</p></div></div></section>
<footer>文件均可离线查阅。游戏设计及关卡数值为原创待测方案；实际开发、投稿与签约按项目审批继续。完整文件清单与校验和位于交付包 manifest.json。</footer></main>
<dialog id="reader"><div class="reader-head"><strong id="doc-title"></strong><button id="close-reader">关闭 ×</button></div><pre id="doc-content"></pre></dialog><script id="documents" type="application/json">DOCUMENTS</script><script>
const docs=JSON.parse(document.getElementById('documents').textContent),reader=document.getElementById('reader');document.querySelectorAll('[data-doc]').forEach(a=>a.addEventListener('click',e=>{if(!docs[a.dataset.doc])return;e.preventDefault();document.getElementById('doc-title').textContent=a.dataset.doc;document.getElementById('doc-content').textContent=docs[a.dataset.doc];reader.showModal();reader.scrollTop=0;document.body.classList.add('reading')}));function closeReader(){reader.close();document.body.classList.remove('reading')}document.getElementById('close-reader').onclick=closeReader;reader.addEventListener('close',()=>document.body.classList.remove('reading'));document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-filter]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));document.querySelectorAll('.project').forEach(p=>p.hidden=b.dataset.filter!=='all'&&p.dataset.batch!==b.dataset.filter)}));
</script></body></html>'''
    replacements = {'REPORT_LINK':link('DELIVERY_REPORT.md','阅读交付报告'),
                    'ARCHIVE_LINK':link('REQUIREMENTS_CHECKLIST.md','查看要求与交付对照'),
                    'STATUS_LINK':link('STATUS.md','查看当前状态 →'),'SOURCE_COUNT':str(len(sources)),
                    'BENCH_COUNT':str(len(benchmarks)),'LEVEL_COUNT':str(total_levels),
                    'PROJECTS':''.join(project_html),'CHANNELS':''.join(channel_html),
                    'ADAPTATION_LINK':link('research/adaptation-matrix.md','查看全部适配矩阵 →'),
                    'VALIDATION_RESULT':escape(validation.get('result','PENDING')),
                    'DISCREPANCIES_LINK':link('discrepancies.md','本次重核与差异 →'),
                    'RIGHTS_LINK':link('research/contracts-and-rights.md','权利与合同冲突 →'),
                    'METHOD_LINK':link('research/methodology.md','证据与观察边界 →'),
                    'BUSINESS_LINK':link('research/business-model.md','成本与停止投入 →'),
                    'AUDIT_LINK':link('reviews/README.md','独立审计索引 →'),
                    'DOCUMENTS':script_data}
    # Replace document payload last so file content cannot accidentally become a token.
    for token,value in replacements.items(): html=html.replace(token,value)
    (ROOT/'index.html').write_text(html,encoding='utf-8')

def package():
    excluded = {'deliverables','runtime','raw','node_modules','.git','__pycache__'}
    paths = sorted(p for p in ROOT.rglob('*') if p.is_file() and not excluded.intersection(p.relative_to(ROOT).parts)
                   and p.suffix not in {'.pyc','.tmp'})
    manifest = [dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest()) for p in paths]
    out = ROOT/'deliverables'
    out.mkdir(exist_ok=True)
    manifest_text = json.dumps(dict(package=NAME,files=manifest),ensure_ascii=False,indent=2)+'\n'
    (out/'manifest.json').write_text(manifest_text,encoding='utf-8')
    archive = out/f'{NAME}.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=6) as z:
        for p in paths: z.write(p,NAME+'/'+p.relative_to(ROOT).as_posix())
        z.writestr(NAME+'/manifest.json',manifest_text)
    with ZipFile(archive) as z:
        if z.testzip() is not None: raise ValueError('archive integrity check failed')
        expected = {NAME+'/'+item['path']: item for item in manifest}
        if set(z.namelist()) != set(expected)|{NAME+'/manifest.json'}:
            raise ValueError('archive membership mismatch')
        for name,item in expected.items():
            payload = z.read(name)
            if len(payload)!=item['bytes'] or sha256(payload).hexdigest()!=item['sha256']:
                raise ValueError('archive payload hash mismatch: '+name)
    verification = dict(result='PASS',archive=str(archive),files=len(paths)+1,bytes=archive.stat().st_size,
                        sha256=sha256(archive.read_bytes()).hexdigest(),crc='PASS',
                        membership='PASS',all_payload_hashes='PASS',
                        excluded_directories=sorted(excluded))
    (out/'archive-verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(verification,ensure_ascii=False))

if __name__ == '__main__':
    build_index()
    package()
