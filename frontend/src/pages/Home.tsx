import { useEffect, useState } from "react";
import { loadRepository, getJobStatus } from "../services/api";
import { useNavigate, useLocation } from "react-router-dom";
import "./Home.css";

function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [statusText, setStatusText] = useState("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const repoUrlReanalyze = location.state?.repoUrl;

  const textDico: Record<string, string> = {
    "invalid_repository" : "Repository invalide !",
    "in_progress" : "Analyse du repository déjà en cours !"
  };

  useEffect(() => {
    if (repoUrlReanalyze) {
      setRepoUrl(repoUrlReanalyze);
      handleAnalyze();
    }
  }, [repoUrl]);

  const handleAnalyze = async () => {
    setStatusText("En attente de réponse du serveur ...");
    if (!repoUrl.trim()) return;
    setLoading(true);
    const res = await loadRepository(repoUrl);
    // backend now returns job_id
    if (res.status in textDico) {
      setStatusText(textDico[res.status]);
      setLoading(false);
      return;
    }
    if (res.status!== "queued") {
      navigate(`/repo/${res.repo_id}`);
      return;
    }
    setStatusText("Analyse en cours ...");
    setJobId(res.job_id);
  };

  // POLLING JOB STATUS
  useEffect(() => {
    if (!jobId) return;

    const interval = setInterval(async () => {
      const status = await getJobStatus(jobId);
      if (status.status === "finished") {
        clearInterval(interval);
        const repo_id = status.result?.repo_id;
        if (repo_id) {
          navigate(`/repo/${repo_id}`);
        }
        setLoading(false);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [jobId]);

  return (
    <div className="page">
      <h1 className="repo-title">Start Analyse</h1>
      <div>
        <div className="card">
          <input
            type="text"
            placeholder="https://github.com/user/repo.git"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
          />

          <button onClick={handleAnalyze} disabled={loading}>
            {loading ? "Analyse..." : "Analyser"}
          </button>
        </div>

        {statusText!=="" && (
          <div className="status">{statusText}</div>
        )}

        {loading && (
          <div className="loader">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;