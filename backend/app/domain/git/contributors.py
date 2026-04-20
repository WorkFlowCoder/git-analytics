from collections import defaultdict
from app.domain.git.types import ContributorStats

def analyze_contributors(commits):
    contributions = defaultdict(int)

    for c in commits:
        contributions[c.author.email] += 1

    sorted_contrib = sorted(
        contributions.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top = sorted_contrib[0][0] if sorted_contrib else None

    return ContributorStats(
        contributors=dict(contributions),
        top_contributor=top,
        bus_factor=len(contributions)
    )