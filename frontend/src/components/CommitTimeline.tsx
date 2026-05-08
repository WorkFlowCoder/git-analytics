import "./CommitTimeline.css";
import { useState } from "react";
import { getRepositoryTimeline } from "../services/api";

type CommitItem = {
  author_name: string;
  commit_date: string;
  commit_message: string;
  files_changed: number;
  insertions: number;
  deletions?: number;
};

type Props = {
  repoId: number;
  initialTimeline: CommitItem[];
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

export default function CommitTimeline({ repoId, initialTimeline }: Props) {

  const [timeline, setTimeline] = useState(initialTimeline);
  const [page, setPage] = useState(2);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState( initialTimeline.length > 0 );

  const loadMore = async () => {
    try {
      setLoading(true);

      const response = await getRepositoryTimeline(
        repoId,
        page
      );

      const newCommits = response.timeline || [];

      if (newCommits.length === 0) {
        setHasMore(false);
        return;
      }

      setTimeline((prev) => [
        ...prev,
        ...newCommits
      ]);

      setPage((prev) => prev + 1);

    } finally {
      setLoading(false);
    }
  };

  if (!timeline?.length) {
    return <div>No commit history available.</div>;
  }

  return (
    <div className="timeline-wrapper">
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
                <span className="plusSymbol">➕ {commit.insertions}</span>
                <span className="minusSymbol">➖ {commit.deletions || 0}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      {hasMore && (
        <div className="timeline-load-more">
          <button
            onClick={loadMore}
            disabled={loading}
          >
            {loading ? "Loading..." : "Load more"}
          </button>
        </div>
      )}
    </div>
  );
}