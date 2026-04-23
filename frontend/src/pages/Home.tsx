import { useEffect, useState } from "react";
import { loadRepository, getJobStatus, getRepository } from "../services/api";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";
import "./Home.css";

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString("fr-FR", { day: "2-digit", month: "short" });
};

function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [repoId, setRepoId] = useState<number | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!repoUrl.trim()) return;
    setLoading(true);
    setResult(null);
    const res = await loadRepository(repoUrl);
    // backend now returns job_id
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
          setRepoId(repo_id);
        }
        setLoading(false);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [jobId]);

    useEffect(() => {
    if (!repoId) return;

    const fetchRepo = async () => {
      const data = await getRepository(repoId);
      setResult(data);
    };

    fetchRepo();
  }, [repoId]);


  return (
    <div className="page">
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

        {loading && (
          <div className="loader">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
        )}

        {result && !loading && (
          <>
            <div className="grid">
              <div className="stat">
                <h3>Commits</h3>
                <p>{result.summary?.commits}</p>
              </div>

              <div className="stat">
                <h3>Contributeurs</h3>
                <p>{result.summary?.contributors}</p>
              </div>

              <div className="stat">
                <h3>Fichiers touchés</h3>
                <p>{result.summary?.files_touched}</p>
              </div>

              <div className="stat highlight">
                <h3>Risk Score</h3>
                <p>{result.risk?.risk_score ?? "N/A"}</p>
              </div>
            </div>
            <div className="chart-wrapper">
              <h2>Activité des commits</h2>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={result.activity} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={formatDate} />
                    <YAxis allowDecimals={false} />
                    <Tooltip labelFormatter={(value) => formatDate(value)}/>
                    <Line
                      type="monotone"
                      dataKey="commits"
                      stroke="#2563eb"
                      strokeWidth={3}
                      dot={false}
                      activeDot={false} 
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default Home;