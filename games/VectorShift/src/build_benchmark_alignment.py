"""Reproduce static screenshot measurements and equal-width comparison plates.

Reads manually recorded evidence; does not change or generate playable levels.
Run from this game directory: python src/build_benchmark_alignment.py
Requires Pillow. Reference image rights remain with their respective owners.
"""
import hashlib
import json
from pathlib import Path
from statistics import median

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/benchmark-measurements.json"
OUT = ROOT / "artifacts/benchmark-alignment"
OUT.mkdir(exist_ok=True)
spec = json.loads(SOURCE.read_text(encoding="utf-8"))
font_candidates = [Path("C:/Windows/Fonts/msyh.ttc"), Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")]
font_path = next((p for p in font_candidates if p.exists()), None)
if font_path is None:
    raise SystemExit("A CJK font is required to render the Chinese comparison plate.")


def font(size):
    return ImageFont.truetype(str(font_path), size)


rows = []
images = {}
for item in spec["items"]:
    source_path = ROOT / item["source"]
    image = Image.open(source_path).convert("RGB")
    left, top, right, bottom = item["crop"]
    assert 0 <= left < right <= image.width and 0 <= top < bottom <= image.height
    crop = image.crop(tuple(item["crop"]))
    crop.save(OUT / (item["id"] + "-crop.png"))
    scaled = crop.resize((360, round(crop.height * 360 / crop.width)), Image.Resampling.LANCZOS)
    images[item["id"]] = scaled
    widths = []
    marked = Image.new("RGB", (crop.width + 64, crop.height + 64), "#f6f3eb")
    marked.paste(crop, (32, 32))
    draw = ImageDraw.Draw(marked)
    for index, (x, y) in enumerate(item["headCenters"], 1):
        cx, cy = x - left + 32, y - top + 32
        lx, ly = cx + 13, cy - 23
        draw.line((cx, cy, lx, ly), fill="#182e3c", width=2)
        draw.ellipse((lx - 12, ly - 12, lx + 12, ly + 12), fill="white", outline="#182e3c", width=1)
        draw.text((lx, ly), str(index), font=font(15), fill="#182e3c", anchor="mm")
    if item["headCount"] is not None:
        assert item["headCount"] == len(item["headCenters"])
    for sample in item["widthSamples"]:
        if sample["axis"] == "x":
            p1 = (sample["start"] - left + 32, sample["fixed"] - top + 32)
            p2 = (sample["end"] - left + 32, sample["fixed"] - top + 32)
        else:
            p1 = (sample["fixed"] - left + 32, sample["start"] - top + 32)
            p2 = (sample["fixed"] - left + 32, sample["end"] - top + 32)
        width = sample["end"] - sample["start"] + 1
        widths.append({"id": sample["id"], "sourcePx": width,
                       "boardFraction": round(width / crop.width, 5),
                       "normalized360Px": round(width * 360 / crop.width, 2)})
        draw.line((*p1, *p2), fill="white", width=6)
        draw.line((*p1, *p2), fill="#bb3159", width=2)
        draw.text((p2[0] + 5, p2[1] + 5), sample["id"], font=font(16), fill="#bb3159", stroke_width=1, stroke_fill="white")
    marked.save(OUT / (item["id"] + "-annotated.png"))
    rows.append({"id": item["id"], "source": item["source"],
                 "sourceSha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
                 "sourceSize": list(image.size), "crop": item["crop"],
                 "cropWidth": crop.width, "cropHeight": crop.height,
                 "normalizedSize": list(scaled.size), "visibleHeadCount": item["headCount"],
                 "widthSamples": widths,
                 "medianWidthAt360Px": round(median(w["normalized360Px"] for w in widths), 2) if widths else None})

report = {"observedOn": spec["observedOn"], "status": "STATIC_DIAGNOSIS_NOT_PARITY",
          "specSha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          "method": spec["method"], "items": rows,
          "currentToPrimarySampleWidthRatio": round(rows[0]["medianWidthAt360Px"] / rows[1]["medianWidthAt360Px"], 2),
          "boundsUncertainty": "Approximately +/-2 source pixels at each manually selected anti-aliased edge; ratios are rounded observations, not universal product constants."}
(OUT / "measurements.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

plate = Image.new("RGB", (1248, 870), "#f6f3eb")
draw = ImageDraw.Draw(plate)
draw.text((36, 25), "同宽棋盘复核：粗细、数量、形体层次", font=font(29), fill="#253b46")
draw.text((36, 72), "2026-10-22 · 每盘图形宽 360px · 保留原始宽高比 · 来源为现有截图", font=font(15), fill="#66767b")
for i, item in enumerate(spec["items"][:3]):
    x = 36 + i * 410
    draw.text((x, 125), item["title"], font=font(20), fill="#253b46")
    scaled = images[item["id"]]
    plate.paste(scaled, (x, 169))
    row = rows[i]
    if row["medianWidthAt360Px"]:
        label = f"管身样本约 {row['medianWidthAt360Px']:.1f}px / 主体 {row['visibleHeadCount']} 根"
    else:
        label = "整体剪影由大量局部路径组成；数量未计"
    draw.text((x, 674), label, font=font(16), fill="#253b46")
    secondary = ["大粗体与大三角头占据注意力", "长短交错、嵌套回折、圆润头身", "只借鉴宏观与局部两种观看尺度"][i]
    draw.text((x, 710), secondary, font=font(15), fill="#66767b")
draw.line((36, 760, 1212, 760), fill="#cdd6cf", width=1)
draw.text((36, 780), f"同宽下，本作管身样本约为主对标 {report['currentToPrimarySampleWidthRatio']:.1f} 倍粗；缩细现有 8 根仍然不够，必须重排整盘。", font=font(18), fill="#253b46")
draw.text((36, 818), "截图只支持静态比较。没有测得竞品真实难度、点击目标、动画时序或触觉；没有达到对标的成品证据。", font=font(14), fill="#66767b")
plate.save(OUT / "same-width-comparison.png")
print(json.dumps({"items": [{"id": r["id"], "heads": r["visibleHeadCount"],
                              "medianWidthAt360Px": r["medianWidthAt360Px"]} for r in rows],
                  "widthRatio": report["currentToPrimarySampleWidthRatio"]}, ensure_ascii=False, indent=2))
