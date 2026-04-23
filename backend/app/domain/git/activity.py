from collections import defaultdict

class ActivityAgg:

    def __init__(self):
        self.commits_per_day = defaultdict(int)

    def update(self, commit):
        day = commit.author_date.date()
        self.commits_per_day[day] += 1

    def result(self):
        if not self.commits_per_day:
            return {
                "commits_per_day": {},
                "activity_score": 0.0
            }

        active_days = len(self.commits_per_day)
        total_days = (max(self.commits_per_day) - min(self.commits_per_day)).days + 1

        # régularité (important pour ton produit)
        regularity = active_days / total_days if total_days > 0 else 0

        # activité brute normalisée
        volume = sum(self.commits_per_day.values())
        volume_score = min(volume / 500, 1.0)

        activity_score = 0.6 * regularity + 0.4 * volume_score

        return {
            "commits_per_day": dict(self.commits_per_day),
            "activity_score": round(activity_score, 3),
            "active_days": active_days,
            "total_days": total_days
        }