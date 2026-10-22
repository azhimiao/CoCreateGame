"""Deterministic layouts for the combined course and expert chambers.

Each seed authors two branching mazes, with a mandatory ferry between them.
Locks split the upper route into ordered regions; spare keys cannot be skipped.
Generation is an offline authoring step. The game loads the verified JSON.
"""
from collections import deque
from random import Random


def maze(width, height, seed, root, branching=False):
    rng = Random(seed)
    cells = {root}
    stack = [root]
    while stack:
        index = rng.randrange(len(stack)) if branching and rng.random() < 0.45 else len(stack)-1
        x, y = stack[index]
        choices = [(x+dx, y+dy) for dx, dy in [(0,-2),(2,0),(0,2),(-2,0)]
                   if 0 <= x+dx < width and 0 <= y+dy < height and (x+dx,y+dy) not in cells]
        if not choices:
            stack.pop(index)
            continue
        nx, ny = rng.choice(choices)
        cells.add(((x+nx)//2,(y+ny)//2))
        cells.add((nx,ny))
        stack.append((nx,ny))
    return cells


def neighbors(cells, p):
    return [(p[0]+dx,p[1]+dy) for dx,dy in [(0,-1),(1,0),(0,1),(-1,0)]
            if (p[0]+dx,p[1]+dy) in cells]


def path(cells, start, goal):
    queue = deque([start])
    previous = {start: None}
    while queue:
        p = queue.popleft()
        if p == goal:
            result = []
            while p is not None:
                result.append(p)
                p = previous[p]
            return result[::-1]
        for n in neighbors(cells,p):
            if n not in previous:
                previous[n] = p
                queue.append(n)
    raise ValueError('disconnected maze')


def rows(cells, width, height):
    return [''.join('.' if (x,y) in cells else '#' for x in range(width)) for y in range(height)]


def chamber(number, name, width, lower_height, bit_count, lock_count, anchor_count, seed,
            *, delayed=False, coupled=False, extra_loop=False):
    from build_campaign import base, bits, locks, flows, tracks
    height = lower_height+2
    dock_x = [width-1,0,2*(width//4)][number % 3]
    dock = (dock_x,height-1)
    goal = (0 if dock_x != 0 else width-1,0)
    for attempt in range(400):
        lower = maze(width,lower_height,seed+attempt*101,(0,0),branching=True)
        upper = maze(width,height,seed+attempt*101+37,dock)
        upper_route = path(upper,dock,goal)
        if len(upper_route) < 13+lock_count*3:
            continue
        gate_indices = [len(upper_route)*(i+1)//(lock_count+1) for i in range(lock_count)]
        # Keys after the first must be in side branches between consecutive locks.
        later_keys = []
        for i in range(lock_count-1):
            options = []
            for cell in upper-set(upper_route):
                if len(neighbors(upper,cell)) != 1:
                    continue
                branch = path(upper,dock,cell)
                attach = max(upper_route.index(p) for p in branch if p in upper_route)
                if gate_indices[i]+1 <= attach < gate_indices[i+1]:
                    options.append((len(branch),cell))
            if not options:
                break
            later_keys.append(max(options)[1])
        if len(later_keys) != lock_count-1:
            continue
        leaves = sorted((p for p in lower if len(neighbors(lower,p)) == 1 and p not in [(0,0),(width-1,lower_height-1)]),
                        key=lambda p:(-len(path(lower,(0,0),p)),p))
        needed = bit_count+1+anchor_count
        if len(leaves) < min(needed,3):
            continue
        spare = sorted(lower-set(leaves)-{(0,0),(width-1,lower_height-1)},
                       key=lambda p:(-len(path(lower,(0,0),p)),p))
        leaves.extend(spare)
        break
    else:
        raise ValueError(f'No authored layout for L{number}')
    # A few lower loops introduce route order choices without bypassing upper locks.
    if extra_loop:
        choices = []
        for y in range(1,lower_height-1):
            for x in range(1,width-1):
                p = (x,y)
                if p not in lower and len(neighbors(lower,p)) == 2:
                    choices.append(p)
        if choices:
            # Keep the item-bearing leaves as recognizable branch endpoints.
            for p in Random(seed).sample(choices,min(2,len(choices))):
                if not any(n in leaves[:needed] for n in neighbors(lower|{p},p)):
                    lower.add(p)
    lower_exit = (width-1,lower_height-1)
    direction = 1 if number % 2 else -1
    port_x = (dock_x-direction) % width
    nearest = min((x for x,y in lower if y == lower_height-1),key=lambda x:abs(x-port_x))
    lower.update((x,lower_height-1) for x in range(min(port_x,nearest),max(port_x,nearest)+1))
    lower.add(dock)
    chapter = '06 · 复合回路' if number <= 40 else '07 · 极限挑战'
    note = ('先规划支路取物和校准顺序，再接上平台与跨层锁室。' if number <= 40 else
            '多分支、跨层密室与有限锚片：先找必要资源，再安排回程和摆渡。')
    lv = base(number,name,chapter,rows(lower,width,height),rows(upper,width,height),
              (0,0,0),(1,*goal),[[dock_x,height-1]],note)
    target = (1<<bit_count)-1 if bit_count < 3 else 5
    switches = [((0,*leaves[i]),1<<i) for i in range(bit_count)]
    if coupled:
        lower_route = path(lower,(0,0),lower_exit)
        candidates = [p for p in lower_route[2:-2] if p not in leaves[:needed]]
        switches.append(((0,*candidates[len(candidates)//2]),3))
    bits(lv,bit_count,target,switches,[((1,*upper_route[-2]),0,1)])
    if delayed:
        lv['switch_mode_by_layer'][0] = 'delayed'
    keys = [(0,*leaves[bit_count])] + [(1,*p) for p in later_keys]
    doors = [(1,*upper_route[i]) for i in gate_indices]
    locks(lv,keys,doors)
    anchor_cells = [(0,*p) for p in leaves[bit_count+1:needed]]
    excluded = set(gate_indices) | {0,len(upper_route)-1}
    flow_indices = [i for i in range(2,len(upper_route)-2) if i not in excluded]
    chosen = [flow_indices[(i+1)*len(flow_indices)//(anchor_count+1)] for i in range(anchor_count)]
    arrows = []
    for i in chosen:
        dx = upper_route[i+1][0]-upper_route[i][0]
        dy = upper_route[i+1][1]-upper_route[i][1]
        reverse = {(1,0):'L',(-1,0):'R',(0,1):'U',(0,-1):'D'}[(dx,dy)]
        arrows.append(((1,*upper_route[i]),reverse))
    flows(lv,anchor_cells,arrows)
    tracks(lv,[(0,lower_height,[0,1] if number < 35 else [number % width],direction)])
    lv['required_items'] = [item['id'] for item in lv['items']]
    lv['challenge'] = number >= 41
    lv['layout_seed'] = seed+attempt*101
    lv['branch_count'] = sum(len(neighbors(lower,p)) >= 3 for p in lower) + sum(len(neighbors(upper,p)) >= 3 for p in upper)
    lv['design_note'] = f'{width}×{height} 双层分支；{bit_count} 位校准、{lock_count} 把钥匙、{anchor_count} 片锚、独立摆渡轨道。'
    return lv


def author_late():
    # Small combined circuits precede wide three-bit, multi-lock expert chambers.
    configs = [
        (32,'岔路取光',5,5,1,1,1,3203,False,False,False),
        (33,'锁前折返',5,5,1,1,1,3311,False,False,False),
        (34,'双位渡口',7,5,2,1,1,3407,False,False,False),
        (35,'回声摆渡',7,5,2,1,1,3521,True,False,False),
        (36,'两把钥匙',7,5,2,2,1,3613,False,False,False),
        (37,'联动支路',7,7,2,2,1,3733,False,True,False),
        (38,'双锚回廊',7,7,2,2,2,3821,False,True,False),
        (39,'延迟交汇',7,7,2,2,2,3923,True,True,True),
        (40,'复合终章',9,7,3,2,2,4001,True,True,True),
        (41,'分岔矩阵',9,7,3,2,2,4111,False,True,True),
        (42,'镜面锁城',9,7,3,2,2,4211,True,True,True),
        (43,'三锁环廊',9,7,3,3,2,4327,False,True,True),
        (44,'逆向密钥',9,7,3,3,3,4409,True,True,True),
        (45,'多路归零',9,9,3,3,3,4513,False,True,True),
        (46,'回声迷宫',9,9,3,3,3,4621,True,True,True),
        (47,'交错远征',9,9,3,3,3,4703,True,True,True),
        (48,'相位困局',9,9,3,3,3,4817,True,True,True),
        (49,'深层回路',11,9,3,3,3,4909,True,True,True),
        (50,'折光极点',11,9,3,3,3,5021,True,True,True),
    ]
    return [chamber(*row[:8],delayed=row[8],coupled=row[9],extra_loop=row[10]) for row in configs]
