# pipeline.py
from pydriller import Repository

from app.domain.git.contributors import ContributorsAgg
from app.domain.git.activity import ActivityAgg
from app.domain.git.hotspots import HotspotsAgg
from app.domain.git.cochange import CoChangeAgg
from app.domain.git.metrics import MetricsAgg
from app.domain.git.risk import compute_risk


def analyze_repo(repo_path: str):

    contributors = ContributorsAgg()
    activity = ActivityAgg()
    hotspots = HotspotsAgg()
    cochange = CoChangeAgg()
    metrics = MetricsAgg()

    try:
        for commit in Repository(repo_path, num_workers=4).traverse_commits():
            author = (commit.author.email or "unknown").lower()
            contributors.update(commit, author)
            activity.update(commit)
            metrics.update_commit(commit)
            modified_paths = []
            for mf in commit.modified_files:
                path = mf.new_path or mf.old_path
                if not path:
                    continue

                modified_paths.append(path)
                hotspots.update(path, mf, author)
                metrics.update_file(path)

            cochange.update(modified_paths)

    except Exception as e:
        raise RuntimeError(f"Git traversal failed: {e}")

    # finalize
    contributors_data = contributors.result()
    activity_data = activity.result()
    hotspots_data = hotspots.result()
    metrics_data = metrics.result()
    risk = compute_risk(metrics_data, activity_data, contributors_data)

    return {
        "summary": {
            "commits": metrics_data["commits"],
            "contributors": contributors_data["bus_factor"],
            "files_touched": metrics_data["files_touched"]
        },
        "metrics": metrics_data,
        "contributors": contributors_data,
        "activity": activity_data,
        "hotspots": hotspots_data,
        "risk": risk,
        "cochange_edges": cochange.size()
    }