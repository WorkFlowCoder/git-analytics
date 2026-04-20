from collections import defaultdict

def compute_hotspots(files):
    file_stats = defaultdict(lambda: {
        "changes": 0,
        "additions": 0,
        "deletions": 0
    })

    for f in files:
        path = f["path"]

        file_stats[path]["changes"] += 1
        file_stats[path]["additions"] += f["added"]
        file_stats[path]["deletions"] += f["deleted"]

    ranked = sorted(
        file_stats.items(),
        key=lambda x: x[1]["changes"],
        reverse=True
    )

    return [
        {"file": f, **stats}
        for f, stats in ranked[:10]
    ]