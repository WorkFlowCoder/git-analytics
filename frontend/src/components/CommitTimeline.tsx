import "./CommitTimeline.css";

type CommitItem = {
  author_name: string;
  commit_date: string;
  commit_message: string;
  files_changed: number;
  insertions: number;
  deletions?: number;
};

type Props = {
  timeline: CommitItem[];
};

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);

  return date.toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }) + " • " +
  date.toLocaleTimeString("fr-FR", {
    hour: "2-digit",
    minute: "2-digit",
  });
};

export default function CommitTimeline({ timeline }: Props) {
  if (!timeline?.length) {
    return <div>No commit history available.</div>;
  }

  return (
    <div className="timeline-wrapper">
      <h2>Commit Timeline</h2>

      <div className="timeline">
        {timeline.map((commit, index) => (
          <div key={index} className="timeline-item">
            <div className="timeline-dot" />

            <div className="timeline-content">
              <div className="timeline-header">
                <h3>{commit.commit_message}</h3>
                <span>{formatDate(commit.commit_date)}</span>
              </div>

              <p className="timeline-author">
                {commit.author_name}
              </p>

              <div className="timeline-stats">
                <span>📁 {commit.files_changed} files</span>
                <span>➕ {commit.insertions}</span>
                <span>➖ {commit.deletions || 0}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}