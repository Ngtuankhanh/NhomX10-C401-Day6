import json
from pathlib import Path

def load_graph(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def search(graph: dict, keyword: str) -> list:
    keyword = keyword.lower().strip()
    nodes   = graph.get("nodes", [])
    rels    = graph.get("relations", [])

    # Tìm các node có label/evidence chứa keyword
    matched_ids = {
        node["id"]
        for node in nodes
        if keyword in node.get("label", "").lower()
        or keyword in (node.get("evidence") or "").lower()
    }

    if not matched_ids:
        print(f"Không tìm thấy node nào với keyword: '{keyword}'")
        return []

    # Lấy tất cả relation liên quan (source hoặc target thuộc matched)
    related_rels = [
        rel for rel in rels
        if rel["source"] in matched_ids or rel["target"] in matched_ids
    ]

    # Build id → label map để hiển thị dễ đọc
    id_to_label = {node["id"]: node["label"] for node in nodes}

    results = []
    for rel in related_rels:
        results.append({
            "source":   id_to_label.get(rel["source"], rel["source"]),
            "relation": rel["relation"],
            "target":   id_to_label.get(rel["target"], rel["target"]),
            "disease":  rel.get("disease", ""),
        })

    return results


def print_results(results: list, keyword: str):
    if not results:
        return
    print(f"\nKết quả tìm kiếm: '{keyword}' — {len(results)} quan hệ\n")
    print(f"{'SOURCE':<35} {'RELATION':<25} {'TARGET':<35} {'DISEASE'}")
    print("-" * 120)
    for r in results:
        print(f"{r['source']:<35} {r['relation']:<25} {r['target']:<35} {r['disease']}")


# ──────────────────────────────────────────────
if __name__ == "__main__":
    graph   = load_graph(Path(r"D:\agent1\kg_merged.json"))
    keyword = input("Nhập keyword tìm kiếm: ").strip()
    results = search(graph, keyword)
    print_results(results, keyword)