def compute_risk(metrics, activity, contributors):

    commits = metrics.get("commits", 0)
    contributors_count = len(contributors.get("contributors", {}))
    files_touched = metrics.get("files_touched", 0)
    total_changes = metrics.get("total_changes", 0)

    contrib_values = list(contributors.get("contributors", {}).values())
    total_contrib_commits = sum(contrib_values) if contrib_values else 0

    # concentration
    top_share = (
        max(contrib_values) / total_contrib_commits
        if total_contrib_commits > 0 else 0
    )

    # bus factor
    bus_factor = contributors.get("bus_factor", 0)
    bus_risk = 1 / (bus_factor + 1)

    # churn
    churn_density = total_changes / (files_touched + 1)

    # dispersion équipe
    sparsity_risk = 1 / (contributors_count + 1)

    # activité
    activity_score = activity.get("activity_score", 0.5)
    activity_risk = 1 - activity_score

    # taille repo
    size_risk = 1 / (commits + 1)

    risk_score = (
        0.25 * top_share +
        0.20 * bus_risk +
        0.15 * activity_risk +
        0.15 * sparsity_risk +
        0.15 * (churn_density / 10) +
        0.10 * size_risk
    )

    return {
        "risk_score": round(min(risk_score, 1.0), 3),
        "top_contributor_share": round(top_share, 3),
        "bus_factor": bus_factor,
        "contributors_count": contributors_count,
        "churn_density": round(churn_density, 3),
        "activity_score": activity_score
    }