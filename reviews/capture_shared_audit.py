"""Capture a review baseline; all writes stay inside reviews/. No game code."""
from collections import Counter
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "shared-research-baseline"


def main():
    # A completed baseline must not silently become a different review version.
    OUT.mkdir(exist_ok=False)
    stamp = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
    paths = [
        "MASTER_HANDOFF.md", "AGENTS.md", "prompts/PROMPT_03_对抗审计与淘汰.md",
        "discrepancies.md", "STATUS.md", "requirements-research.txt",
        "research/official-sources.json", "research/claims.json",
        "research/source-access-log.json", "research/channel-profiles.json",
        "research/methodology.md", "research/contracts-and-rights.md",
        "research/business-model.md", "tools/recheck_sources.py",
        "research/benchmarks/evidence/browser-session.json",
    ] + [f"research/platforms/P{i:02}.md" for i in range(1, 7)]
    screenshots = [
        "p01-paint-master-loaded.png", "p03-drive-mad-forward-2s.png",
        "p03-level-devil-stage-start.png", "p03-level-devil-enter-pits.png",
        "p03-level-devil-after-move.png", "p03-level-devil-pits-right.png",
    ]
    manifest = []
    for rel in paths:
        src = ROOT / rel
        if not src.is_file():
            manifest.append({"path": rel, "exists": False})
            continue
        data = src.read_bytes()
        target = OUT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        manifest.append({"path": rel, "exists": True, "bytes": len(data),
                         "sha256": sha256(data).hexdigest()})
    # Existing commercial-game screenshots are referenced and hashed, not copied.
    for name in screenshots:
        rel = f"research/benchmarks/evidence/screenshots/{name}"
        src = ROOT / rel
        data = src.read_bytes()
        manifest.append({"path": rel, "exists": True, "bytes": len(data),
                         "sha256": sha256(data).hexdigest(), "copied": False})
    def read(rel):
        return json.loads((OUT / rel).read_text(encoding="utf-8-sig"))
    claims = read("research/claims.json")
    sources = read("research/official-sources.json")
    access = read("research/source-access-log.json")
    source_by_id = {s["source_id"]: s for s in sources}
    sessions = read("research/benchmarks/evidence/browser-session.json")
    edges = [{"claim_id": c["claim_id"], "source_id": c["source_id"],
              "registered": c["source_id"] in source_by_id,
              "url_matches": c["source_url"] == source_by_id.get(c["source_id"], {}).get("url")}
             for c in claims]
    values = [0, 1000, 1001, 3000, 3001, 5000]
    formula = []
    for n in values:
        progressive = .7 * min(n, 1000) + .8 * min(max(n - 1000, 0), 2000) + .9 * max(n - 3000, 0)
        official_piecewise = .7*n if n <= 1000 else 700 + .8*(n-1000) if n <= 3000 else 2300 + .9*(n-3000)
        formula.append({"hypothetical_net_revenue_usd": n,
                        "document_formula_usd": round(progressive, 6),
                        "official_piecewise_usd": round(official_piecewise, 6),
                        "matches": abs(progressive-official_piecewise) < 1e-8})
    checks = {
        "captured_at": stamp,
        "scope": "shared research only; G01/G02/G04 not reviewed",
        "claims": len(claims), "sources": len(sources),
        "duplicate_claim_ids": [k for k,v in Counter(c["claim_id"] for c in claims).items() if v > 1],
        "duplicate_source_ids": [k for k,v in Counter(s["source_id"] for s in sources).items() if v > 1],
        "claim_source_edges": edges,
        "author_access_log": {"count": len(access), "http_200": sum(x.get("http_status") == 200 for x in access),
                              "interpretation": "Author metadata; not independent semantic verification"},
        "benchmark_cards": [{"path": f"research/benchmarks/P{i:02}.md",
                             "exists": (ROOT / f"research/benchmarks/P{i:02}.md").is_file()}
                            for i in range(1,7)],
        "advertised_preparation_validator_exists": (ROOT / "tools/validate_preparation.py").is_file(),
        "session_operations": len(sessions),
        "session_operations_by_game": dict(Counter(s["id"] for s in sessions)),
        "session_interpretation": "Operations submitted and screenshots do not prove successful game input, victory, or a five-minute playthrough",
        "playgama_formula_checks": formula,
        "formula_interpretation": "Arithmetic against the independently read public FAQ only; hypothetical N, no measured income",
        "files": manifest,
    }
    (OUT / "manifest-and-checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"captured_at": stamp, "copied_files": len(paths),
                      "claim_source_edges_ok": all(x["registered"] and x["url_matches"] for x in edges),
                      "benchmark_cards_present": sum(x["exists"] for x in checks["benchmark_cards"]),
                      "advertised_validator_exists": checks["advertised_preparation_validator_exists"],
                      "formula_boundaries_ok": all(x["matches"] for x in formula)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
