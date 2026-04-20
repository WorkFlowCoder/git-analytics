from concurrent.futures import ThreadPoolExecutor

from pydriller import Repository

from app.domain.git.hotspots import compute_hotspots
from app.domain.git.contributors import analyze_contributors
from app.domain.git.metrics import compute_metrics
from app.domain.git.risk import compute_risk
from app.domain.git.activity import compute_activity


def safe_traverse(repo_path: str, max_commits=2000):
    try:
        return list(
            Repository(repo_path, num_workers=4).traverse_commits()
        )[:max_commits]
    except Exception as e:
        raise RuntimeError(f"Git traversal failed: {e}")


def build_dataset(commits):
    files = []

    for c in commits:
        for mf in c.modified_files:
            path = mf.new_path or mf.old_path
            if not path:
                continue

            files.append({
                "path": path,
                "added": getattr(mf, "added_lines", 0),
                "deleted": getattr(mf, "deleted_lines", 0),
            })

    return files


def analyze_repo(repo_path: str):
    commits = safe_traverse(repo_path)
    files = build_dataset(commits)

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_contributors = executor.submit(analyze_contributors, commits)
        future_activity = executor.submit(compute_activity, commits)
        future_hotspots = executor.submit(compute_hotspots, files)

        contributors = future_contributors.result()
        activity = future_activity.result()
        hotspots = future_hotspots.result()

    metrics = compute_metrics(commits, contributors, files)
    risk = compute_risk(metrics, activity, contributors)

    return {
        "summary": {
            "commits": metrics["commits"],
            "contributors": contributors.bus_factor,
            "files_touched": metrics["files_touched"]
        },
        "metrics": metrics,
        "contributors": contributors,
        "activity": activity,
        "hotspots": hotspots,
        "risk": risk
    }