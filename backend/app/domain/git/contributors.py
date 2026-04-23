from collections import defaultdict

class ContributorsAgg:

    def __init__(self):
        self.contributions = defaultdict(int)

    def update(self, commit, author):
        self.contributions[author] += 1

    def result(self):
        sorted_contrib = sorted(
            self.contributions.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top = sorted_contrib[0][0] if sorted_contrib else None

        return {
            "contributors": dict(self.contributions),
            "top_contributor": top,
            "bus_factor": len(self.contributions)
        }