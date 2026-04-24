from http.client import HTTPException
from app.domain.git.repo_queries import (
    get_repository,
    get_summary,
    get_contributors,
    get_hotspots,
    get_activity,
    get_risk
)


def fetch_repo_details(repo_id: int):
    repo = get_repository(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    return {
        "repo": {
            "id": repo[0],
            "name": repo[1],
            "url": repo[2],
            "analyzed_at": repo[3]
        },
        "tree": repo[4],
        "summary": get_summary(repo_id),
        "contributors": get_contributors(repo_id),
        "hotspots": get_hotspots(repo_id),
        "activity": get_activity(repo_id),
        "risk": get_risk(repo_id)
    }