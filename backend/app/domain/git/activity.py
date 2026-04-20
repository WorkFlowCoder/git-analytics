from collections import defaultdict

def compute_activity(commits):
    by_author = defaultdict(int)
    by_day = defaultdict(int)

    for c in commits:
        author = c.author.name if c.author else "unknown"
        by_author[author] += 1

        try:
            day = c.author_date.date().isoformat()
            by_day[day] += 1
        except:
            continue

    return {
        "commits_by_author": dict(by_author),
        "commits_by_day": dict(by_day)
    }