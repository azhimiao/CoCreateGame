"""Package this directory's preparation artifacts; never writes outside G04."""
from __future__ import annotations
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARCHIVE = "G04_Preparation_2026-10-21_v1.0.0.zip"
EXCLUDE = {ARCHIVE, "DELIVERY_MANIFEST.json", "archive-verification.json"}
ALLOWED_SUFFIXES = {".md", ".json", ".py", ".txt"}
REQUIRED_DOCS = (
    "00_Project_Charter.md", "01_Market_Evidence.md", "02_Benchmark_Playthrough.md",
    "03_Full_GDD.md", "04_Systems_and_Data.md", "05_Levels_Economy.md",
    "06_UI_Art_Audio.md", "07_Tech_Architecture.md", "08_OpenSource_Licenses.md",
    "09_Implementation_Plan.md", "10_QA_Test_Plan.md", "11_Distribution_Business.md",
    "12_Falsifiability.md",
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    for name in REQUIRED_DOCS:
        assert (ROOT / name).stat().st_size >= 2000, f"Missing/substantive document: {name}"
    assert (ROOT / "STATUS.md").is_file(), "Current revision status required"
    spec = json.loads((ROOT / "game-spec.json").read_text(encoding="utf-8"))
    assert spec["status"] == "REVISION_REQUIRED" and not spec["ready_for_build"]
    report = json.loads((ROOT / "validation-report.json").read_text(encoding="utf-8"))
    assert report["result"] == "PASS"
    for name, expected in report["input_sha256"].items():
        assert sha((ROOT / name).read_bytes()) == expected, f"Stale validation: {name}"
    assert len(report["levels"]) == 22 and len(report["golden_vectors"]) == 21
    assert len(report["experiment_controls"]) == 2
    assert report["contracts"]["result"] == "PASS"
    paths = sorted(p for p in ROOT.iterdir()
                   if p.is_file() and p.name not in EXCLUDE and p.suffix in ALLOWED_SUFFIXES)
    for path in paths:
        assert path.resolve().parent == ROOT
        assert path.suffix not in {".ts", ".js", ".exe"}
    manifest = {
        "project_id": "G04", "version": "1.0.0", "contract_revision": "r2", "status": spec["status"],
        "ready_for_build": False, "access_date": "2026-10-21",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "package_type": "PREPARATION_DOCUMENTS_AND_OFFLINE_SPEC_CHECKS",
        "excluded_from_payload": [ARCHIVE, "DELIVERY_MANIFEST.json (self)", "archive-verification.json (external receipt)"],
        "files": [{"path": p.name, "bytes": p.stat().st_size,
                   "sha256": sha(p.read_bytes())} for p in paths],
    }
    manifest_path = ROOT / "DELIVERY_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    archive_path = ROOT / ARCHIVE
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in paths + [manifest_path]:
            archive.write(path, "G04/" + path.name)
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None, "ZIP CRC failed"
        expected_names = {"G04/" + p.name for p in paths + [manifest_path]}
        assert set(archive.namelist()) == expected_names
        assert len(archive.namelist()) == len(expected_names), "Duplicate ZIP member"
        for entry in manifest["files"]:
            content = archive.read("G04/" + entry["path"])
            assert len(content) == entry["bytes"] and sha(content) == entry["sha256"]
        assert archive.read("G04/DELIVERY_MANIFEST.json") == manifest_path.read_bytes()
        member_count = len(archive.namelist())
    result = {
        "result": "PASS", "archive": ARCHIVE, "bytes": archive_path.stat().st_size,
        "sha256": sha(archive_path.read_bytes()), "member_count": member_count,
        "payload_file_count": len(paths), "crc": "PASS", "member_set": "PASS",
        "payload_hashes": "PASS", "manifest_bytes": "PASS",
        "substantive_documents": len(REQUIRED_DOCS),
        "engine_build_executed": False,
        "verification": "Read ZIP without extraction; compared every archived member to on-disk manifest",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (ROOT / "archive-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
