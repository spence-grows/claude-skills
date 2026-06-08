# kb_inventory.py — audit the Copilot corpus.
# Usage: cd <your copilot repo> && uv run python "<this dir>/kb_inventory.py" [project_id]
# No project_id: prints per-project doc counts. With one: lists that project's docs (doc_id|date|type|source_kind|title).
import lancedb, os, collections, sys
db = lancedb.connect(os.path.expanduser("~/.copilot/lance"))
docs = db.open_table("documents").to_arrow().to_pylist()
proj = sys.argv[1] if len(sys.argv) > 1 else None
def cnt(rows, k): return collections.Counter(str(r.get(k, "")) for r in rows)
print("total documents:", len(docs))
print("--- docs per project ---")
for k, v in cnt(docs, "project_id").most_common():
    print(f"{v:4}  {k}")
if proj:
    rows = [r for r in docs if r.get("project_id") == proj]
    print(f"\n--- {proj} ({len(rows)} docs): doc_id | date | type | source_kind | title ---")
    for r in sorted(rows, key=lambda r: str(r.get("date", ""))):
        print("\t".join([str(r.get("doc_id", ""))[:40], str(r.get("date", ""))[:10],
                          str(r.get("type", "")), str(r.get("source_kind", "")),
                          str(r.get("title", ""))[:55]]))
