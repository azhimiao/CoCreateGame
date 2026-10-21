"""Build and verify the preparation-only ZIP. All writes remain in G02."""
import hashlib
import io
import json
import zipfile
from pathlib import Path
from verify import verify

ROOT = Path(__file__).resolve().parents[1]
ZIP_NAME = "G02_Preparation_2026-10-21.zip"


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def main():
    # Re-run the actual offline check so an old report cannot be packaged silently.
    result = verify()
    dump(ROOT / "verification/verification-report.json", result)
    docs = sorted(ROOT.glob("[0-1][0-9]_*.md"))
    assert len(docs) == 13 and [p.name[:2] for p in docs] == [f"{i:02d}" for i in range(13)]
    assert all(p.stat().st_size >= 1500 for p in docs), "substantive documents required"
    for name in ["game-spec.json", "tasks.json", "game-spec.schema.json", "tasks.schema.json", "README.md",
                 "HANDOFF_STATE.md", "STATUS.md", "REVISIONS.md", "revision-index.json",
                 "protocol-vectors.json","layout-cases.json","INDEPENDENT_AUDIT_REQUEST.md", "SELF_REVIEW.md"]:
        assert (ROOT / name).is_file(), name
    excluded = {ZIP_NAME, "package-manifest.json", "verification/package-check.json"}
    members = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in excluded or relative.endswith((".zip", ".pyc")):
            continue
        assert not path.is_symlink()
        members[relative] = path.read_bytes()
    manifest = {"project_id":"G02", "date":"2026-10-21", "status":"REVISION_REQUIRED_PENDING_RE_REVIEW",
        "independent_reviewer":"same reviewer Jason; not yet re-reviewed","ready_for_build":False,
        "scope":"preparation_only_no_game_build", "excluded":[ZIP_NAME,"package-manifest.json","verification/package-check.json","__pycache__"],
        "files":[{"path":name,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()} for name,data in members.items()]}
    dump(ROOT / "package-manifest.json", manifest)
    members["package-manifest.json"] = (ROOT / "package-manifest.json").read_bytes()
    destination = ROOT / ZIP_NAME
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo("G02/"+name, date_time=(2026,10,21,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)
    raw = destination.read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        assert archive.testzip() is None
        assert sorted(archive.namelist()) == sorted("G02/"+k for k in members)
        for name, data in members.items():
            assert archive.read("G02/"+name) == data
    check = {"overall_status":"PASS", "scope":"ZIP_INTEGRITY_NOT_GAME_BUILD", "date":"2026-10-21",
        "archive": ZIP_NAME, "archive_bytes":len(raw), "archive_sha256":hashlib.sha256(raw).hexdigest(),
        "document_count_00_12":len(docs),"archive_members":len(members),"payload_files_hashed":len(manifest["files"]),
        "crc_ok":True,"all_members_equal_to_workspace":True,"manifest_sha256_verified":True,
        "independent_audit":"PENDING_RE_REVIEW", "ready_for_build":False}
    dump(ROOT / "verification/package-check.json", check)
    print(f"PASS: 13 documents; {len(members)} ZIP members; {len(raw)} bytes; CRC and all member hashes verified")
    print(destination)


if __name__ == "__main__":
    main()
