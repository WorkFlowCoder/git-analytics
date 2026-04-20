import { useState } from "react";
import { loadRepository } from "../services/api";
import "./Home.css";

function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    const data = await loadRepository(repoUrl);
    setResult(data);
  };

  return (
    <div className="home">
      <h1>Analyse de repository Git</h1>

      <div className="form">
        <input
          type="text"
          placeholder="https://github.com/user/repo.git"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
        />

        <button onClick={handleAnalyze}>
          Analyser
        </button>
      </div>

      {result && (
        <div className="result">
          <p>Commits: {result.commits}</p>
          <p>Contributeurs: {result.contributors}</p>
        </div>
      )}
    </div>
  );
}

export default Home;