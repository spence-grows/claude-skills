# kb_move.py — re-assign a document (and its chunks) to another project, in place (no re-embed).
# Usage: cd <your copilot repo> && uv run python "<this dir>/kb_move.py" <target_project> <doc_id> [<doc_id> ...]
# Reversible: re-run with the original project to undo. Find doc_ids with kb_inventory.py <project>.
import sys
from copilot.store.lancedb_store import Store
target, doc_ids = sys.argv[1], sys.argv[2:]
assert doc_ids, "give at least one doc_id"
s = Store()
for did in doc_ids:
    s.move_doc(did, target)
    print("moved", did, "->", target)
s.refresh_fts()
print("done; fts refreshed")
