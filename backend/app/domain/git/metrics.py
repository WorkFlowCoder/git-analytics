def compute_metrics(commits, contributors, files):
    file_set = {f["path"] for f in files}

    total_changes = len(files)

    return {
        "commits": len(commits),
        "contributors": len(contributors.contributors),
        "files_touched": len(file_set),
        "total_changes": total_changes
    }