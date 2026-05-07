import { useEffect, useState } from "react";
import {
  getAllRepositories,
  deleteRepository
} from "../services/api";
import { useNavigate } from "react-router-dom";
import "./RepositoriesPage.css";

type Repository = {
  id: number;
  name: string;
  url: string;
  analyzed_at: string | null;
  is_analyzing: boolean;
};

export default function RepositoriesPage() {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  const pageSize = 20;
  const navigate = useNavigate();

  useEffect(() => {
    getAllRepositories()
      .then(setRepos)
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id: number) => {
    await deleteRepository(id);
    setRepos((prev) => prev.filter((r) => r.id !== id));
  };

  const handleReanalyze = (repoUrl: string) => {
    navigate("/", {
      state: { repoUrl }
    });
  };

  const paginatedRepos = repos.slice(
    (page - 1) * pageSize,
    page * pageSize
  );

  if (loading) return <div className="loading">Loading...</div>;

  if (!repos.length) {
    return <div className="empty">No repositories analyzed yet.</div>;
  }

  return (
    <div className="repo-page">
      <h1 className="repo-title">Analyzed Repositories</h1>

      <div className="repo-grid">
        {paginatedRepos.map((repo) => {
          const disabled = repo.is_analyzing;
          return (
            <div
              key={repo.id}
              className={`repo-card ${disabled ? "repo-card-disabled" : ""}`}
              onClick={() => {
                if (!disabled) navigate(`/repo/${repo.id}`);
              }}>
              <div className="repo-name">
                {repo.name}
                {disabled && (
                  <span className="repo-status"> (analyzing...)</span>
                )}
              </div>

              {repo.analyzed_at && (
                <div className="repo-date">
                  Last analyzed:{" "}
                  {new Date(repo.analyzed_at).toLocaleString()}
                </div>
              )}

              <div className="repo-actions">
                <button
                  className="btn-reanalyze"
                  disabled={disabled}
                  onClick={(e) => {
                    e.stopPropagation();
                    if (!disabled) handleReanalyze(repo.url);
                  }}>
                  🔁
                </button>
                <button
                  className="btn-delete"
                  disabled={disabled}
                  onClick={(e) => {
                    e.stopPropagation();
                    if (!disabled) handleDelete(repo.id);
                  }}>
                  🗑
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="pagination">
        <button
          disabled={page === 1}
          onClick={() => setPage((p) => p - 1)}>
          Prev
        </button>
        <span>Page {page} / {Math.ceil(repos.length / pageSize)}</span>
        <button
          disabled={page >= Math.ceil(repos.length / pageSize)}
          onClick={() => setPage((p) => p + 1)}>
          Next
        </button>
      </div>
    </div>
  );
}