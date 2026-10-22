"""Measure five real rendered straight sections and build the same-width comparison.

Requires Pillow. Run dense-smoke.cjs first; uses its real 390x844 PNG and Canvas bounds.
This is pixel evidence, not a competitor difficulty or touch-performance measurement.
"""
import hashlib
import json
from pathlib import Path
from statistics import median
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts'
report = json.loads((OUT / 'dense-browser-report.json').read_text(encoding='utf-8'))
level = json.loads((ROOT / 'data/dense-levels.json').read_text(encoding='utf-8'))[0]
source = OUT / 'dense-pattern-1.png'
im = Image.open(source).convert('RGB')
display = report['firstBoard']
rect = display['rect']
dpr = im.width / display['viewport']['width']
scale = display['s'] * dpr

def screen(x, y):
    return round(rect['x'] * dpr + (18 + (x + .5) * 32) * scale), round(rect['y'] * dpr + (18 + (y + .5) * 32) * scale)

def colored(rgb):
    return max(rgb)-min(rgb) > 33 and min(rgb) < 210

left, top = round(rect['x']*dpr), round(rect['y']*dpr)
right, bottom = round(rect['right']*dpr), round(rect['bottom']*dpr)
pixels = im.load()
points = [(x,y) for y in range(top,bottom) for x in range(left,right) if colored(pixels[x,y])]
bounds = (min(x for x,y in points), min(y for x,y in points), max(x for x,y in points)+1, max(y for x,y in points)+1)
crop = im.crop(bounds)
samples = []
for a in sorted(level['arrows'], key=lambda a: -len(a['cells'])):
    if any(s['skin'] == a['skin'] for s in samples):
        continue
    cells = a['cells']
    for i in range(2,len(cells)-2):
        before, at, after = cells[i-1:i+2]
        if (at[0]-before[0],at[1]-before[1]) != (after[0]-at[0],after[1]-at[1]):
            continue
        x,y = screen(*at)
        horizontal = before[0] != at[0]
        dx,dy = (0,1) if horizontal else (1,0)
        if not colored(pixels[x,y]):
            continue
        lo=hi=0
        while lo>-40 and colored(pixels[x+dx*(lo-1),y+dy*(lo-1)]): lo-=1
        while hi<40 and colored(pixels[x+dx*(hi+1),y+dy*(hi+1)]): hi+=1
        width=hi-lo+1
        if not 28<=width<=40: continue
        samples.append({'id':a['id'],'skin':a['skin'],'cell':at,'from':[x+dx*lo,y+dy*lo],'to':[x+dx*hi,y+dy*hi],'sourcePx':width,'normalized360Px':round(width/crop.width*360,2)})
        break
    if len(samples)==5: break
assert len(samples)==5, samples
font_path='C:/Windows/Fonts/msyh.ttc'
font=ImageFont.truetype(font_path,20)
small=ImageFont.truetype(font_path,16)
annotated=im.copy();draw=ImageDraw.Draw(annotated)
for n,s in enumerate(samples,1):
    draw.line([tuple(s['from']),tuple(s['to'])],fill='#17302e',width=2)
    draw.text((s['from'][0]+6,s['from'][1]+6),f'S{n}',font=small,fill='#193a32',stroke_width=2,stroke_fill='#faf7ef')
annotated.save(OUT/'dense-width-samples.png')
crop.save(OUT/'dense-board-crop.png')
items=[('旧版 L20 · 8 条',OUT/'benchmark-alignment/vs-level20-crop.png'),('新版首盘 · 28 条',OUT/'dense-board-crop.png'),('8Great 参考 · 26 条',OUT/'benchmark-alignment/8great-dense-crop.png')]
canvas=Image.new('RGB',(1160,650),'#faf7ef');draw=ImageDraw.Draw(canvas)
for i,(label,file) in enumerate(items):
    image=Image.open(file).convert('RGB');image=image.resize((360,round(image.height/image.width*360)),Image.Resampling.LANCZOS)
    x=20+i*390;draw.text((x,18),label,font=font,fill='#354339');canvas.paste(image,(x,62))
    text=['管宽约 39.8px / 360px','五处实测中位数 %.1fpx / 360px'%median(s['normalized360Px'] for s in samples),'既有样本约 17.7～18.6px / 360px'][i]
    draw.text((x,578),text,font=small,fill='#64725f')
draw.text((20,615),'同宽、保留原比例；本图只用于静态画面与尺度对照，不代表手感或难度已超过对标。',font=small,fill='#909582')
canvas.save(OUT/'dense-same-width-comparison.png')
result={'date':'2026-10-22','source':str(source.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'method':'Five perpendicular pixel cuts through straight body sections in the actual rendered initial board; colored body threshold excludes cream background and detached shadow. Not a whole-body mean. Bounds include visible colored body and heads; minor edge ambiguity remains.','crop':bounds,'visibleBodies':len(level['arrows']),'samples':samples,'medianNormalized360Px':median(s['normalized360Px'] for s in samples),'rangeNormalized360Px':[min(s['normalized360Px'] for s in samples),max(s['normalized360Px'] for s in samples)],'competitor':'Existing saved screenshot and measurements in artifacts/benchmark-alignment; no new live-game observation.'}
(OUT/'dense-width-measurements.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
