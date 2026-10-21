"""Summarize delivered artifacts without turning validation into product approval."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P0 = {'G01','G02','G04'}

def read(path, default):
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else default

def main():
    projects = read(ROOT/'data/projects.json', [])
    decisions = read(ROOT/'reviews/decisions.json', [])
    if isinstance(decisions,dict): decisions = decisions.get('decisions',[])
    by_id = {x.get('game_id',x.get('id')): x for x in decisions}
    rows = []
    for game in projects:
        gid = game['id']
        directory = ROOT/'games'/gid
        spec = read(directory/'game-spec.json', {})
        decision = by_id.get(gid, {})
        verdict = decision.get('verdict','PENDING') if gid in P0 else 'RESEARCH_BACKLOG'
        note = decision.get('summary',decision.get('decision_note',''))
        if not note:
            note = ('施工文档与20关数据已准备；独立审查及可观察对标证据仍在核对。' if gid in P0
                    else '候选证据和本家族研究问题已交付；完整玩法、数值、资产及验证待后续研究。')
        title = spec.get('title',spec.get('working_title',game['family']))
        if isinstance(title,dict): title = title.get('zh',title.get('en',game['family']))
        complete = all((directory/n).exists() for n in
                      ['00_Project_Charter.md','01_Market_Evidence.md','02_Benchmark_Playthrough.md','03_Full_GDD.md',
                       '04_Systems_and_Data.md','05_Levels_Economy.md','06_UI_Art_Audio.md','07_Tech_Architecture.md',
                       '08_OpenSource_Licenses.md','09_Implementation_Plan.md','10_QA_Test_Plan.md',
                       '11_Distribution_Business.md','12_Falsifiability.md','game-spec.json','tasks.json']) if gid in P0 else False
        blockers = decision.get('unresolved_blockers', [])
        majors = decision.get('unresolved_majors', [])
        ready = verdict == 'GO' and complete and not blockers and not majors
        if verdict == 'GO' and not ready:
            raise ValueError(f'{gid}: GO conflicts with incomplete documents or unresolved findings')
        row = dict(id=gid, family=game['family'], title=title,
                   preparation_batch=game['preparation_batch'],
                   status=('READY_FOR_BUILD' if ready else 'REVISION_REQUIRED' if verdict=='REVISE' else 'KILLED' if verdict=='KILL' else
                           'INDEPENDENT_REVIEW' if gid in P0 else 'EVIDENCE_COLLECTED'),
                   audit_verdict=verdict,
                   display_status=('档案可施工' if ready else '需补证/修订' if verdict=='REVISE' else '建议淘汰' if verdict=='KILL' else
                                   '审查中' if gid in P0 else '候选研究'),
                   decision_note=note, ready_for_build=ready,
                   documentation_complete=complete,
                   unresolved_blockers=len(blockers), unresolved_majors=len(majors),
                   source_input_status=game['status'], development_authorized=False, development_started=False)
        rows.append(row)
    (ROOT/'data/preparation-status.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote {len(rows)} project status records; no automatic build approval.')

if __name__ == '__main__': main()
