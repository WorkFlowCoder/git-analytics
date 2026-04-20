def compute_hotspots(commits, files):
    file_stats = {}

    for c in commits:
        for mf in (files or []):
            path = mf.new_path or mf.old_path or "unknown"

            if path not in file_stats:
                file_stats[path] = {
                    "changes": 0,
                    "additions": 0,
                    "deletions": 0
                }

            file_stats[path]["changes"] += 1
            file_stats[path]["additions"] += getattr(mf, "added_lines", 0)
            file_stats[path]["deletions"] += getattr(mf, "deleted_lines", 0)

    # ranking
    ranked = sorted(
        file_stats.items(),
        key=lambda x: x[1]["changes"],
        reverse=True
    )

    return [
        {"file": f, **stats}
        for f, stats in ranked[:10]
    ]