def compute_metrics(commits, contributors, files):
    authors_count = len(contributors.contributors)

    file_set = set()
    total_changes = 0

    for c in commits:
        for f in files:
            path = f.new_path or f.old_path
            if not path:
                continue

            file_set.add(path)
            total_changes += 1

    return {
        "commits": len(commits),
        "contributors": authors_count,
        "files_touched": len(file_set),
        "total_changes": total_changes
    }