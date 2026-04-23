class MetricsAgg:

    def __init__(self):
        self.commits = 0
        self.files = set()
        self.total_changes = 0

    def update_commit(self, commit):
        self.commits += 1

    def update_file(self, path):
        self.files.add(path)
        self.total_changes += 1

    def result(self):
        return {
            "commits": self.commits,
            "files_touched": len(self.files),
            "total_changes": self.total_changes
        }