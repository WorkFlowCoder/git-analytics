import { useEffect, useState } from "react";
import {
  getAllRepositories,
  deleteRepository,
  reanalyzeRepository
} from "../services/api";
import { useNavigate } from "react-router-dom";
import "./RepositoriesPage.css";

type Repository = {
  id: number;
  name: string;
  analyzed_at: string | null;
};

export default function RepositoriesPage() {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getAllRepositories()
      .then(setRepos)
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id: number) => {
    await deleteRepository(id);
    setRepos(repos.filter(r => r.id !== id));
  };

  const handleReanalyze = async (id: number) => {
    await reanalyzeRepository(id);
    alert("Analysis relaunched");
  };

  if (loading) return <div className="loading">Loading...</div>;

  if (!repos.length) {
    return <div className="empty">No repositories analyzed yet.</div>;
  }

  return (
    <div className="repo-page">
      <h1 className="repo-title">Analyzed Repositories</h1>

      <div className="repo-grid">
        {repos.map((repo) => (
          <div
            key={repo.id}
            className="repo-card"
            onClick={() => navigate(`/repo/${repo.id}`)}
          >
            <div className="repo-name">{repo.name}</div>

            {repo.analyzed_at && (
              <div className="repo-date">
                Last analyzed:{" "}
                {new Date(repo.analyzed_at).toLocaleString()}
              </div>
            )}

            <div className="repo-actions">
              <button
                className="btn-reanalyze"
                onClick={(e) => {
                  e.stopPropagation();
                  handleReanalyze(repo.id);
                }}
              >
                🔁
              </button>

              <button
                className="btn-delete"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(repo.id);
                }}
              >
                🗑
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}