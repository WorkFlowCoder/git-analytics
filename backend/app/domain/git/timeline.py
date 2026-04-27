class TimelineAgg:
    def __init__(self):
        self.timeline = []

    def update(self, commit):
        self.timeline.append({
            "commit_hash": commit.hash,
            "author": commit.author.name,
            "email": commit.author.email,
            "date": commit.author_date,
            "message": commit.msg,
            "files_changed": len(commit.modified_files),
            "insertions": commit.insertions,
            "deletions": commit.deletions
        })

    def result(self):
        return self.timeline