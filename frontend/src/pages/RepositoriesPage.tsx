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

  const [search, setSearch] = useState("");
  const [nameSort, setNameSort] = useState<"" | "asc" | "desc">("");
  const [dateSort, setDateSort] = useState<"" | "newest" | "oldest">("");
  const [statusFilter, setStatusFilter] = useState<"all" | "analyzing" | "ready">("all");

  const filteredRepos = repos
    .filter((repo) => {
      const matchesSearch =
        repo.name.toLowerCase().includes(search.toLowerCase()) ||
        repo.url.toLowerCase().includes(search.toLowerCase());

      const matchesStatus =
        statusFilter === "all" ||
        (statusFilter === "analyzing" && repo.is_analyzing) ||
        (statusFilter === "ready" && !repo.is_analyzing);

      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      // tri date
      if (dateSort) {
        const dateComparison =
          dateSort === "newest"
            ? new Date(b.analyzed_at || 0).getTime() -
              new Date(a.analyzed_at || 0).getTime()
            : new Date(a.analyzed_at || 0).getTime() -
              new Date(b.analyzed_at || 0).getTime();

        if (dateComparison !== 0) {
          return dateComparison;
        }
      }

      // tri nom
      if (nameSort) {
        return nameSort === "asc"
          ? a.name.localeCompare(b.name)
          : b.name.localeCompare(a.name);
      }

      return 0;
    });

  const paginatedRepos = filteredRepos.slice(
    (page - 1) * pageSize,
    page * pageSize
  );

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

  if (loading) return <div className="loading">Loading...</div>;

  if (!repos.length) {
    return <div className="empty">No repositories analyzed yet.</div>;
  }

  return (
    <div className="repo-page">
      <h1 className="repo-title">Analyzed Repositories</h1>

      <div className="repo-toolbar">
        <input
          type="text"
          placeholder="Search by repository name or URL..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="repo-search"
        />

        <div className="repo-toolbar-filters">
          <select
            value={nameSort}
            onChange={(e) => {
              setNameSort(e.target.value as "" | "asc" | "desc");
              setPage(1);
            }}
          >
            <option value="">Sort by name</option>
            <option value="asc">A-Z</option>
            <option value="desc">Z-A</option>
          </select>

          <select
            value={dateSort}
            onChange={(e) => {
              setDateSort(e.target.value as "" | "newest" | "oldest");
              setPage(1);
            }}
          >
            <option value="">Sort by date</option>
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(
                e.target.value as "all" | "analyzing" | "ready"
              );
              setPage(1);
            }}
          >
            <option value="all">All repositories</option>
            <option value="analyzing">Analyzing</option>
            <option value="ready">Ready</option>
          </select>
        </div>
      </div>

      <div className="repo-count">
        {filteredRepos.length} repositories
      </div>

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
        <span>
          Page {page} / {Math.max(1, Math.ceil(filteredRepos.length / pageSize))}
        </span>
        <button
          disabled={page >= Math.ceil(filteredRepos.length / pageSize)}
          onClick={() => setPage((p) => p + 1)}>
          Next
        </button>
      </div>
    </div>
  );
}