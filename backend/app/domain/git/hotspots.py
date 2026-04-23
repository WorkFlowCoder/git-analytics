from collections import defaultdict

class HotspotsAgg:

    def __init__(self):
        self.file_stats = defaultdict(lambda: {
            "changes": 0,
            "additions": 0,
            "deletions": 0,
            "authors": set()
        })

    def update(self, path, mf, author):
        stats = self.file_stats[path]
        stats["changes"] += 1
        stats["additions"] += mf.added_lines or 0
        stats["deletions"] += mf.deleted_lines or 0
        stats["authors"].add(author)

    def result(self):
        ranked = sorted(
            self.file_stats.items(),
            key=lambda x: (
                x[1]["changes"],
                x[1]["additions"] + x[1]["deletions"]
            ),
            reverse=True
        )

        return [
            {
                "file": path,
                "changes": s["changes"],
                "additions": s["additions"],
                "deletions": s["deletions"],
                "contributors": len(s["authors"]),
                "churn": s["additions"] + s["deletions"]
            }
            for path, s in ranked[:10]
        ]