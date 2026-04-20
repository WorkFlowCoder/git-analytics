import { useState } from "react";
import { loadRepository } from "../services/api";
import "./Home.css";

function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!repoUrl.trim()) return;

    try {
      setLoading(true);
      setResult(null);

      const data = await loadRepository(repoUrl);
      console.log(data);
      setResult(data);
    } finally {
      setLoading(false);
    }
  };

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
          <div className="grid">
            <div className="stat">
              <h3>Commits</h3>
              <p>{result.metrics?.commits}</p>
            </div>

            <div className="stat">
              <h3>Contributeurs</h3>
              <p>{result.metrics?.contributors}</p>
            </div>

            <div className="stat">
              <h3>Fichiers touchés</h3>
              <p>{result.metrics?.files_touched}</p>
            </div>

            <div className="stat highlight">
              <h3>Risk Score</h3>
              <p>{result.risk?.risk_score ?? "N/A"}</p>
            </div>

            <div className="stat full">
              <h3>Résumé activité</h3>
              <pre>{JSON.stringify(result.activity, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;