from collections import defaultdict
from itertools import combinations


class CoChangeAgg:

    def __init__(self):
        self.edges = defaultdict(int)

    def update(self, paths):
        for a, b in combinations(set(paths), 2):
            self.edges[(a, b)] += 1

    def size(self):
        return len(self.edges)