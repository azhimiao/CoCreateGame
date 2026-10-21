"""Index the team's existing partial observation. Read external files, write G01 only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parents[1]/'research/playthroughs/G01'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
hashes=json.loads((SOURCE/'screenshot_hashes.json').read_text(encoding='utf-8-sig'))
for row in hashes['files']:
    target=(SOURCE/row['path']).resolve()
    assert target.is_relative_to(SOURCE.resolve()) and digest(target)==row['sha256']
assert len(hashes['files'])==21
def node(name,status,locator,summary):
    return dict(node=name,status=status,locator=locator,author_summary=summary)
nodes=[
node('P04 entry','OBSERVED','01 / 10:39:03 UTC','作品页及Play Now可见。'),
node('start/ad/close','OBSERVED','02,14,15 / 10:39:29 and 10:44:15–17 UTC','出现广告，普通点击关闭后回教学页；不能推出游戏内激励广告规则。'),
node('continue without login','OBSERVED_UI_TRANSITION','03 -> 05','登录条消失；保存是否发生UNKNOWN。'),
node('tutorial board','OBSERVED','03,05 / first retained 10:40:13 UTC','三条直箭、Tap to release、手指；05可见三颗红心。首次可操作时刻UNKNOWN。'),
node('core mouse attempt','INPUT_SENT_RESULT_UNCONFIRMED','05->06,16->17,19->20','点击/微拖/按下700ms已发送，没有确认箭头数或生命变化；响应原因UNKNOWN。'),
node('legal removal','NOT_OBSERVED','same before/after pairs','合法输入与整条移动/碰撞几何UNKNOWN。'),
node('illegal input/heart loss','NOT_OBSERVED','no verified blocked board','非法反馈/扣心UNKNOWN；静态三心不是扣心证据。'),
node('win/next level','NOT_OBSERVED','no success frame','胜利判定/奖励/下一关UNKNOWN。'),
node('failure/retry','NOT_OBSERVED','no fail/restart UI','失败及游戏内重开UNKNOWN；文件名retry只是再次发送点击。'),
node('progress return','UNKNOWN','two browser contexts, no accepted move','重访并未证明已提交进度持久化。'),
node('P02 game','OBSERVED_REDIRECT_ONLY','21 / 10:45:55 UTC','意语原游戏URL最终到/it/t/brain；本作教学/输入/胜败/重试全部UNKNOWN；不推断全球下架。'),
node('continuous first 30 seconds','NOT_COVERED','operations.jsonl; two contexts','起点未知，无连续有效轨迹；440.252秒总尝试时长不是此覆盖。'),
node('continuous first 5 minutes','NOT_COVERED','context close/reopen 10:42:58.614 / 10:43:00.937 UTC','未连续玩满5分钟；不由总驻留时长回填。')]
data=dict(evidence_id='O01',title='G01 team browser attempt: partial tutorial, input unconfirmed',
    accessed_on='2026-10-21',observation_timezone='UTC',linked_at_utc=datetime.now(timezone.utc).isoformat(),
    evidence_type='DIRECT_BROWSER_ATTEMPT_PARTIAL; not completed gameplay or continuous playthrough',
    source_root='../../../research/playthroughs/G01/',
    sources=[dict(path='../../../research/playthroughs/G01/'+name,sha256=digest(SOURCE/name)) for name in ['observation.md','operations.jsonl','screenshot_hashes.json','validation.json','delivery_manifest.json']],
    urls=[dict(profile='P04',requested='https://playgama.com/game/arrow-puzzle',final='https://playgama.com/game/arrow-puzzle'),dict(profile='P02',requested='https://www.crazygames.com/it/game/arrow-escape-puzzle',final='https://www.crazygames.com/it/t/brain')],
    first_record_utc='2026-10-21T10:38:35.952Z',last_record_utc='2026-10-21T10:45:56.204Z',attempt_span_seconds=440.252,
    duration_scope='includes tooling, ad, image inspection, context restart; NOT continuous gameplay',
    environment='Windows; headless Chromium 149.0.7827.55; 1365x900 DPR1; en-US; mouse; GPU/performance UNKNOWN',
    method_history='Author initial round used web text only (no browser interaction tool in that round). Team later used browser and sent input; do not describe that later attempt as complete play.',
    screenshot_hashes_verified=21,coverage=nodes,remaining_finding='G01-M01 remains open; key flow and continuous timing missing',ready_for_build=False,
    distribution='Link original team evidence once in root package; do not duplicate commercial page text or browser runtime. Exclude external runtime/ and local research/raw/.')
target=ROOT/'research/observation-coverage.json'
target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('O01 linked; 21 screenshot SHA-256 verified; core/timed flow remains unconfirmed.')
