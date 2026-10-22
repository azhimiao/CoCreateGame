"""Author the staged campaign and verify shortest routes before writing its data.

Run from any folder with Python 3. No packages required. The shipped game reads
data/campaign.json; this authoring solver is independent of Godot's rule engine.
"""
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = {'U': (0, -1), 'R': (1, 0), 'D': (0, 1), 'L': (-1, 0)}


def base(number, name, chapter, lower, upper, start, goal, lifts, note):
    return dict(id=f'LR-C1-{number:02}', number=number, available=True,
                verification=False, challenge=False, name=name, chapter=chapter,
                subtitle=note, width=len(lower[0]), height=len(lower),
                floors=[lower, upper], start=list(start), goal=list(goal),
                bit_count=0, start_bits=0, goal_bits=0, move_limit=50,
                par=0, time_limit=90, lifts=lifts, switches=[],
                switch_mode_by_layer=['instant', 'instant'], gates=[],
                sealed_gates=[], items=[], beacons=[], currents=[],
                moving_rows=[], moving_period=len(lower[0]),
                environment=[chapter + ' · 下层', chapter + ' · 上层'],
                rule_note=note, tutorial_events=[],
                solution=[])


def row_at(lv, p, phase):
    for row in lv['moving_rows']:
        if (row['layer'], row['y']) == (p[0], p[2]):
            if p[1] in [(x + row['direction'] * phase) % lv['width'] for x in row['tiles']]:
                return row
    return None


def supported(lv, p, bits, key, opened, phase):
    l, x, y = p
    if not (0 <= l < 2 and 0 <= x < lv['width'] and 0 <= y < lv['height']):
        return False
    if lv['floors'][l][y][x] != '.' and not row_at(lv, p, phase):
        return False
    for gate in lv['gates']:
        if tuple(gate['at']) == p and (bits >> gate['bit']) & 1 != gate['value']:
            return False
    for i, gate in enumerate(lv['sealed_gates']):
        if tuple(gate['at']) == p and not key and not opened & (1 << i):
            return False
    return True


def advance(lv, s, action):
    p, bits, pending, key, opened, anchor, collected, phase, turn = s
    if action == 'X':
        if list(p[1:]) not in lv['lifts']:
            return None
        dest = (1 - p[0], p[1], p[2])
    else:
        flow = next((c for c in lv['currents'] if tuple(c['at']) == p), None)
        if flow and action != flow['dir']:
            dx, dy = DIR[action]
            fx, fy = DIR[flow['dir']]
            if anchor == 0 or (dx, dy) != (-fx, -fy):
                return None
            anchor -= 1
        dx, dy = DIR[action]
        dest = (p[0], p[1] + dx, p[2] + dy)
    if not supported(lv, dest, bits, key, opened, phase):
        return None
    ride = row_at(lv, dest, phase)
    if lv['moving_rows']:
        phase = (phase + 1) % lv['moving_period']
        if ride:
            dest = (dest[0], (dest[1] + ride['direction']) % lv['width'], dest[2])
    bits ^= pending
    pending = 0
    if not supported(lv, dest, bits, key, opened, phase):
        return None
    for i, item in enumerate(lv['items']):
        if tuple(item['at']) == dest and not collected & (1 << i):
            # The inventory holds one generic key at a time. Routes space them apart.
            collected |= 1 << i
            if item['type'] == 'key':
                key = True
            else:
                anchor += 1
    for i, gate in enumerate(lv['sealed_gates']):
        if tuple(gate['at']) == dest and not opened & (1 << i) and key:
            opened |= 1 << i
            key = False
    for switch in lv['switches']:
        if tuple(switch['at']) == dest:
            if lv['switch_mode_by_layer'][dest[0]] == 'delayed':
                pending ^= switch['mask']
            else:
                bits ^= switch['mask']
            break
    turn += 1
    if not supported(lv, dest, bits, key, opened, phase):
        return None
    return dest, bits, pending, key, opened, anchor, collected, phase, turn


def solve(lv):
    start = (tuple(lv['start']), lv['start_bits'], 0, False, 0, 0, 0, 0, 0)
    # The first visit to a canonical state is its shortest route.
    def signature(s):
        return s[:-1]
    q = deque([(start, '')])
    seen = {signature(start)}
    while q:
        s, path = q.popleft()
        if s[0] == tuple(lv['goal']) and s[1] == lv['goal_bits'] and s[2] == 0:
            return list(path), len(seen)
        if len(path) >= 240:
            continue
        for a in ('U', 'R', 'D', 'L', 'X'):
            nxt = advance(lv, s, a)
            if nxt is not None and signature(nxt) not in seen:
                seen.add(signature(nxt))
                q.append((nxt, path + a))
    raise ValueError(f"Unsolvable: {lv['number']} {lv['name']}")


def item(kind, at, idx=0):
    return dict(id=f'{kind}_{idx}', type=kind, at=list(at), name='棱镜钥匙' if kind == 'key' else '相位锚片')


def bits(lv, count, target, switches, gates=(), delayed=False):
    lv.update(bit_count=count, goal_bits=target,
              switches=[dict(at=list(p), mask=m) for p, m in switches],
              gates=[dict(at=list(p), bit=b, value=v) for p, b, v in gates])
    if delayed:
        lv['switch_mode_by_layer'][1] = 'delayed'


def locks(lv, keys, doors):
    lv['items'] = [item('key', p, i) for i, p in enumerate(keys)]
    lv['sealed_gates'] = [dict(id=f'lock_{i}', at=list(p)) for i, p in enumerate(doors)]


def flows(lv, anchors, arrows):
    lv['items'].extend(item('anchor', p, i) for i, p in enumerate(anchors))
    lv['currents'] = [dict(at=list(p), dir=d) for p, d in arrows]


def tracks(lv, rows):
    lv['moving_rows'] = [dict(layer=l, y=y, tiles=tiles, direction=d, name=f'轨{n+1}') for n, (l, y, tiles, d) in enumerate(rows)]


def author():
    levels = []
    def add(*args):
        lv = base(*args)
        levels.append(lv)
        return lv
    # 01–06: layer changes only. Each graph adds another turn or layer crossing.
    add(1, '初次跃迁', '01 · 层间起步', ['###', '..#', '###'], ['###', '#..', '###'], (0,0,1), (1,2,1), [[1,1]], '走到双环格，升到上层，再到出口。')
    add(2, '折角', '01 · 层间起步', ['....','####','####'], ['###.','###.','##..'], (0,0,0), (1,2,2), [[3,0]], '先走到走廊尽头，切层后沿折角向前。')
    add(3, '断桥接力', '01 · 层间起步', ['..#..','####.','####.'], ['#...#','#####','#####'], (0,0,0), (0,4,2), [[1,0],[3,0]], '下层断桥要借上层跨过，再降回出口。')
    add(4, '上下交错', '01 · 层间起步', ['...##','#####','##...','####.'], ['##.##','##.##','##.##','#####'], (0,0,0), (0,4,3), [[2,0],[2,2]], '别把另一层当终点，寻找第二处升降台。')
    add(5, '三次折返', '01 · 层间起步', ['...##','##.##','##...','#####','#####'], ['##.##','##.##','##.##','####.','##...'], (0,0,0), (1,2,4), [[2,0],[2,2],[4,2],[4,4]], '比较两层的缺口，连续三次升降才能到达。')
    # Fix upper continuity for the third transfer.
    levels[-1]['floors'][1][2] = '##.#.'
    levels[-1]['floors'][0][1] = '#####'
    levels[-1]['lifts'] = [[2,0],[2,2],[4,2]]
    add(6, '回环坐标', '01 · 层间起步', ['...##','##.##','##...','####.','....#'], ['##.##','##.##','##.##','..##.','.....'], (0,0,0), (0,0,4), [[2,0],[2,2],[4,2],[4,4],[0,4]], '在不同高度接续断路，五处升降点中选对路线。')
    # Add a final lower dock and connect its transfer through the upper layer.
    levels[-1]['floors'][1][2] = '##.#.'
    levels[-1]['floors'][0][1] = '#####'
    levels[-1]['floors'][0][3] = '#####'
    levels[-1]['floors'][0][4] = '.....'
    levels[-1]['floors'][1][4] = '.###.'
    levels[-1]['goal'] = [1,0,4]
    # 07–12: shared goal bits, then gates, coupled bits, delayed switches.
    lv=add(7,'点亮目标','02 · 光位校准',['#####','.....','#####'],['#####','####.','#####'],(0,0,1),(1,4,1),[[4,1]],'本关开始需要完成目标：点亮 ○，再到出口。')
    bits(lv,1,1,[((0,2,1),1)])
    lv['tutorial_events']=[dict(id='switch_goal',title='点亮翻位目标',steps=[dict(target='objective',text='目标面板显示本关出口、需要匹配的机关位，以及剩余步数和计时。先点亮 ○，再到出口。'),dict(target='cell',at=[0,2,1],text='这枚翻位格会在落地后切换共享位 ○。达标时地块转为薄荷绿，中央圆环亮起勾号。')])]
    lv=add(8,'支路取光','02 · 光位校准',['#####','.....','#.###'],['#####','####.','#####'],(0,0,1),(1,4,1),[[4,1]],'先走支路点亮 ○，回到主路再过门。')
    bits(lv,1,1,[((0,1,2),1)],[((0,3,1),0,1)])
    lv['tutorial_events']=[dict(id='bit_gate',title='光栅障碍',steps=[dict(target='cell',at=[0,3,1],text='红色光栅是位门，只有 ○=1 时才有支撑。先踩亮下方支路的 ○ 翻位格，再穿过这里。')])]
    lv=add(9,'双位拼图','02 · 光位校准',['.....','##.##','.....'],['####.','####.','.....'],(0,0,0),(1,0,2),[[4,0],[4,2]],'○ 与 ◇ 分别点亮，穿过两道光栅。')
    bits(lv,2,3,[((0,2,0),1),((0,0,2),2)],[((1,2,2),0,1),((1,1,2),1,1)])
    lv=add(10,'回声落定','02 · 光位校准',['.....','#####','#####'],['####.','####.','.....'],(0,0,0),(1,0,2),[[4,0]],'上层延迟翻位，下一次落地后 ◇ 才会点亮。')
    bits(lv,2,3,[((0,1,0),1),((1,4,1),2)],[((1,1,2),1,1)],True)
    lv['tutorial_events']=[dict(id='delayed_switch',title='延迟翻位',steps=[dict(target='cell',at=[1,4,1],text='上层这枚开关会把 ◇ 放进待生效队列。完成下一次有效跳跃或升降后，◇ 才会切换；左上面板会显示待生效位。')])]
    lv=add(11,'联动回路','02 · 光位校准',['.....','#.#.#','.....'],['##.##','##.##','.....'],(0,0,0),(1,0,2),[[2,0],[4,2]],'翻 ○◇ 会同时改变两位；目标是 ○ 亮、◇ 灭。')
    bits(lv,2,1,[((0,1,0),3),((0,3,2),2)],[((1,1,2),0,1)])
    lv=add(12,'三色校准','02 · 光位校准',['.....','#.#.#','.....'],['..#..','.#.#.','.....'],(0,0,0),(1,0,0),[[4,0],[0,2],[4,2]],'○、△ 亮而 ◇ 灭，选择联动开关的组合。')
    bits(lv,3,5,[((0,2,0),3),((0,2,2),6),((1,2,2),1),((1,4,1),2)],[((1,0,1),2,1)])
    # 13–18: keys form an independent course, with no bits, currents or tracks.
    lv=add(13,'第一把钥匙','03 · 棱镜锁室',['#####','.....','#####'],['#####','####.','#####'],(0,0,1),(1,4,1),[[4,1]],'金色钥匙能开启粉色的钥匙门。')
    locks(lv,[(0,1,1)],[(0,3,1)])
    lv['tutorial_events']=[dict(id='key_lock',title='棱镜钥匙与门',steps=[dict(target='cell',at=[0,1,1],text='金色菱形是钥匙。落在钥匙格后会自动拾取，状态显示在底部道具栏。'),dict(target='cell',at=[0,3,1],text='粉色栅栏是钥匙门。带着钥匙进入会自动开门；开过的门会保持开启。')])]
    lv=add(14,'钥匙在岔路','03 · 棱镜锁室',['#.###','.....','#####'],['#####','####.','#####'],(0,0,1),(1,4,1),[[4,1]],'锁就在前方，先去支路取钥匙。')
    locks(lv,[(0,1,0)],[(0,3,1)])
    lv=add(15,'楼上的储藏室','03 · 棱镜锁室',['.....','#####','#####'],['..###','#.###','#..##'],(0,0,0),(0,4,0),[[1,0]],'上层取钥匙，再降回原路开锁。')
    locks(lv,[(1,2,2)],[(0,3,0)])
    lv=add(16,'一锁一钥','03 · 棱镜锁室',['.....','####.','.....'],['#####','#####','..###'],(0,0,0),(1,0,2),[[1,2]],'先开第一道锁，才能拿到第二把钥匙。')
    locks(lv,[(0,1,0),(0,4,2)],[(0,3,0),(0,2,2)])
    lv=add(17,'跨层双锁','03 · 棱镜锁室',['.....','##.##','.....'],['#....','#.##.','#....'],(0,0,0),(1,1,2),[[4,0],[4,2]],'钥匙藏在两层的分支里，开锁后可以往返。')
    lv['floors'][1][1] = '####.'
    lv['lifts'] = [[4,0]]
    locks(lv,[(0,0,2),(1,2,2)],[(1,4,1),(1,1,2)])
    lv=add(18,'三段密室','03 · 棱镜锁室',['.....','####.','.....','..###'],['#####','#####','..###','#....'],(0,0,0),(1,4,3),[[1,3]],'按开锁顺序拾取三把钥匙，每把都要用在必经处。')
    locks(lv,[(0,1,0),(0,4,2),(0,0,3)],[(0,3,0),(0,2,2),(1,3,3)])
    # 19–24: currents and anchor allocation, independently from previous modules.
    lv=add(19,'逆流初识','04 · 矢量航道',['.....','#####','#####'],['####.','####.','.....'],(0,0,0),(1,0,2),[[4,0]],'取锚片后，试着逆箭头离开折流格。')
    flows(lv,[(0,2,0)],[((1,3,2),'R')])
    lv['tutorial_events']=[dict(id='current_anchor',title='折流与相位锚片',steps=[dict(target='cell',at=[0,2,0],text='锚片提供一次逆流通行机会，收集后会显示在道具栏。'),dict(target='cell',at=[1,3,2],text='箭头格默认只允许顺箭头离开。逆向离开会消耗一片锚片；侧向不能离开。')])]
    lv=add(20,'顺流与逆流','04 · 矢量航道',['.....','####.','###..'],['#####','#####','.....'],(0,0,0),(1,0,2),[[4,2]],'下层顺流不消耗；把锚片留给上层。')
    flows(lv,[(0,3,0)],[((0,1,0),'R'),((1,2,2),'R')])
    lv=add(21,'先找锚点','04 · 矢量航道',['.....','#.###','#..##'],['####.','####.','.....'],(0,0,0),(1,0,2),[[4,0]],'锚片在支路尽头，错过后无法逆流到达出口。')
    flows(lv,[(0,2,2)],[((1,3,2),'R'),((0,3,0),'R')])
    lv=add(22,'双重阻流','04 · 矢量航道',['.....','#.#.#','#.#.#'],['####.','####.','.....'],(0,0,0),(1,0,2),[[4,0]],'收集两片锚片，连续穿过两段逆流。')
    flows(lv,[(0,1,2),(0,3,2)],[((1,3,2),'R'),((1,1,2),'R')])
    lv=add(23,'转向预算','04 · 矢量航道',['.....','#.#.#','.....'],['####.','####.','.....'],(0,0,0),(1,0,2),[[4,0],[4,2]],'利用升降绕开风向限制，把锚片用在必要的一步。')
    flows(lv,[(0,0,2)],[((0,3,0),'R'),((1,3,2),'R'),((1,4,1),'D')])
    lv=add(24,'三片的远征','04 · 矢量航道',['.....','#.#.#','.....','###.#','###..'],['####.','####.','####.','####.','.....'],(0,0,0),(1,0,4),[[4,0],[4,4]],'三片锚片分布在回廊中，逆流航道不容浪费。')
    flows(lv,[(0,1,2),(0,3,2),(0,3,4)],[((1,3,4),'R'),((1,2,4),'R'),((1,1,4),'R')])
    # 25–30: moving platforms only; explicitly no currents/anchors or other modules.
    configs=[
        (25,'第一班摆渡',5,['.....','#####','.....'],[0,1],1,1),
        (26,'窄窗登船',5,['.....','#####','.....'],[0],1,3),
        (27,'向左的轨迹',5,['.....','#####','....#'],[3],-1,0),
    ]
    for n,name,w,floor,tiles,d,gx in configs:
        upper=['#'*w,'#'*w, ''.join('.' if x==gx else '#' for x in range(w))]
        lv=add(n,name,'05 · 潮汐摆渡',floor,upper,(0,0,0),(1,gx,2),[[gx,2]],'观察平台的下一步落点，再跳上它。')
        tracks(lv,[(0,1,tiles,d)])
        if n == 25:
            lv['tutorial_events']=[dict(id='moving_platform',title='移动平台',steps=[dict(target='cell',at=[0,tiles[0],1],text='这排地块会在每次有效动作结束后移动一格。站在上面时，角色会跟着地块一起走。')])]
    for n,name,tiles1,tiles2,d1,d2,gx in [
        (28,'两次接驳',[0,1],[2,3],1,1,4),
        (29,'相向潮汐',[1],[3],1,-1,0),
        (30,'双轨会合',[0],[4],-1,1,3),
    ]:
        floor=['.....','#####','.....','#####','.....']
        upper=['#####','#####','#####','#####',''.join('.' if x==gx else '#' for x in range(5))]
        lv=add(n,name,'05 · 潮汐摆渡',floor,upper,(0,0,0),(1,gx,4),[[gx,4]],'先过上轨，在中央固定平台调整相位，再过下轨。')
        tracks(lv,[(0,1,tiles1,d1),(0,3,tiles2,d2)])
    lv=add(31,'四维接力','06 · 复合回路',['..###','#####','.####'],['#####','#####','.....'],(0,0,0),(1,4,2),[[0,2]],'把光位、钥匙、逆流与移动轨道放进同一条路线。')
    bits(lv,1,1,[((0,1,0),1)])
    locks(lv,[(0,1,0)],[(1,3,2)])
    flows(lv,[(1,1,2)],[((1,2,2),'L')])
    tracks(lv,[(0,1,[3,4],1)])
    lv['tutorial_events']=[dict(id='mechanism_combo',title='四种机制接力',steps=[dict(target='board',text='这关把前面学过的翻位目标、钥匙门、相位锚片和移动轨道接在同一条路线上。按顺序查看机关，再规划资源使用。')])]
    from late_campaign import author_late
    levels.extend(author_late())
    levels[40]['tutorial_events'] = [dict(id='expert_routes',title='挑战：先规划再出发',steps=[dict(target='objective',text='从这里开始是十关挑战。地图更大、分支更多：先核对三种通道的目标，再规划钥匙和锚片的取用顺序。步数用完仍会失败。'),dict(target='preview',text='点击缩略图查看另一层，先找出锁门、逆流和终点的位置，再决定下层该带哪些资源。查看地图不消耗步数；善用撤销修正路线。')])]
    # Attach introductions to every map that contains a mechanism. The client
    # shows each id only once, including when a player enters a trial directly.
    for lv in levels:
        authored = {event['id']: event for event in lv['tutorial_events']}
        events = []

        def introduce(event_id, title, steps):
            events.append(authored.get(event_id, dict(id=event_id, title=title, steps=steps)))

        def cell(at, text):
            return dict(target='cell', at=list(at), text=text)

        if lv['switches']:
            introduce('switch_goal', '点亮翻位目标', [
                dict(target='objective', text='出口不仅要求抵达，还要求当前位型匹配目标。○、◇、△ 分别代表三个共享通道，1 表示点亮、0 表示熄灭；先看清本关目标。'),
                cell(lv['switches'][0]['at'], '踩上翻位格后会改变标注的共享位，两层共用同一组状态。与目标匹配时，格面变绿，中央圆环出现勾号；再次踩入会翻回。')])
        if lv['gates']:
            introduce('bit_gate', '光栅障碍', [cell(lv['gates'][0]['at'], '这是位门。门前的通道图案实心要求点亮，空心要求熄灭；满足条件才能进入。先利用对应图案的翻位格改变机关状态。')])
        if lv['bit_count'] >= 2:
            introduce('multi_bit', '多个目标位', [dict(target='objective', text='本关同时检查多个共享位。○、◇ 分别变化，出口要求每一位都与目标一致；只点亮其中一位还不够。')])
        delayed = [s for s in lv['switches'] if lv['switch_mode_by_layer'][s['at'][0]] == 'delayed']
        if delayed:
            introduce('delayed_switch', '延迟翻位', [cell(delayed[0]['at'], '带时钟图案的翻位格不会立刻切换状态，会先进入待生效队列。完成下一次有效跳跃或升降后才生效，左上目标卡会显示等待切换的位。')])
        coupled = [s for s in lv['switches'] if s['mask'].bit_count() > 1]
        if coupled:
            introduce('coupled_switch', '联动翻位', [cell(coupled[0]['at'], '带多个通道图案的翻位格，会同时翻转这些位。亮的会熄灭，灭的会点亮；留意目标里需要保持熄灭的位。')])
        if lv['bit_count'] >= 3:
            introduce('three_bit', '三位校准', [dict(target='objective', text='现在目标扩展为 ○、◇、△ 三位。按目标逐项核对，利用联动格一次改变多位，再用单独翻位格校准。')])
        if lv['sealed_gates']:
            key = next(item for item in lv['items'] if item['type'] == 'key')
            introduce('key_lock', '棱镜钥匙与门', [
                cell(key['at'], '金色菱形是钥匙，落地后自动拾取并显示在底部道具栏。一次携带一把，先用完再取下一把。'),
                cell(lv['sealed_gates'][0]['at'], '粉色栅栏是钥匙门。携带钥匙进入时自动消耗一把并开门，已经打开的门可以反复通过。')])
        if lv['currents']:
            anchor = next(item for item in lv['items'] if item['type'] == 'anchor')
            introduce('current_anchor', '折流与相位锚片', [
                cell(anchor['at'], '这是相位锚片，收集后会显示在底部道具栏。每片提供一次逆流通行机会。'),
                cell(lv['currents'][0]['at'], '箭头格默认只能顺着箭头离开。逆向离开自动消耗一片锚片，侧向不能离开；升降不受箭头限制。')])
        if lv['moving_rows']:
            row = lv['moving_rows'][0]
            introduce('moving_platform', '移动平台', [cell([row['layer'], row['tiles'][0], row['y']], '这是移动轨道。每次有效跳跃或升降全部结束后，平台才平移一格；站在上面会随它移动。越过边界的平台会从另一侧绕回。')])
        if len(lv['moving_rows']) > 1:
            row = lv['moving_rows'][1]
            introduce('dual_tracks', '双轨接驳', [cell([row['layer'], row['tiles'][0], row['y']], '现在有两排轨道，会在每回合结束时一起移动。注意两排箭头的方向；可以在中间固定地面往返，调整搭乘时机。')])
        events.extend(event for event in lv['tutorial_events'] if event['id'] not in {e['id'] for e in events})
        # Pair recognition with an action/feedback step; no one-page dead ends.
        followups = {
            'bit_gate': lambda: cell(lv['switches'][0]['at'], '先进入这枚翻位格改变共享位，再观察位门是否开启。门上标注的条件与出口目标可能不同，要分别核对。'),
            'multi_bit': lambda: cell(lv['switches'][-1]['at'], '看清每枚翻位格上的通道图案，踩入只会改变对应的位。通过目标卡逐项检查 ○、◇，全部匹配后再去出口。'),
            'delayed_switch': lambda: dict(target='objective', text='踩入延迟格后，目标卡会出现“下一步结算”。接着完成一次有效移动或升降才会切换该位；看地图和无效操作都不会推进结算。'),
            'coupled_switch': lambda: dict(target='objective', text='先核对目标里的亮与灭，再决定联动格的踩入次数。若只差一位，可以寻找单独翻位格校准；重复踩入会再次翻转。'),
            'three_bit': lambda: cell(coupled[0]['at'], '这里的联动格能同时改变标注的多位。把它与单独翻位格配合，调整到目标位型后再抵达出口。'),
            'moving_platform': lambda: dict(target='objective', text='目标卡中的轨道相位显示当前平台位置。每次有效动作完成后才更新相位，站上平台会被携带一格；先比较它下一回合能接上的地面。'),
            'dual_tracks': lambda: cell([lv['moving_rows'][0]['layer'],lv['moving_rows'][0]['tiles'][0],lv['moving_rows'][0]['y']], '先搭第一排轨道到中间固定地面，再观察第二排的相位。可在固定地面来回移动调整时机；查看缩略图不推进轨道。'),
            'mechanism_combo': lambda: dict(target='objective', text='先核对本关目标，再把翻位、钥匙、锚片和摆渡路线连起来。角色落地后机关才结算，留意每次移动结束后的状态。'),
        }
        for event in events:
            if len(event['steps']) == 1:
                event['steps'].append(followups[event['id']]())
        lv['tutorial_events'] = events
    return levels


if __name__ == '__main__':
    levels=author()
    for lv in levels:
        route, explored=solve(lv)
        lv['solution']=route
        lv['par']=len(route)
        lv['move_limit']=len(route)+max(6, len(route)//6) if lv['challenge'] else len(route)+max(4, len(route)//2)
        lv['time_limit']=max(40, 20+len(route)*(4 if lv['challenge'] else 6))
        print(f"{lv['number']:02} {lv['name']}  par={len(route)} budget={lv['move_limit']} searched={explored}  {''.join(route)}")
    slots=[]
    by_number={lv['number']:lv for lv in levels}
    for n in range(1,51):
        slots.append(by_number.get(n, dict(number=n,available=False,name='未开放',subtitle='建设中的组合关卡')))
    (ROOT/'data'/'campaign.json').write_text(json.dumps(slots,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
