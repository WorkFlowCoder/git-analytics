import { useEffect, useState } from "react";
import { getRepository, getRepositoryTimeline, getRepositoryGraph } from "../services/api";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";


import "./Home.css";
import RepoTree from "../components/RepoTree";
import DependencyGraph from "../components/DependencyGraph";
import { useParams } from "react-router-dom";
import CommitTimeline from "../components/CommitTimeline";

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short"
  });
};

function RepoPage() {
  const { id } = useParams();
  const repoId = Number(id);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    if (!repoId) return;

    const fetchData = async () => {
      const repo = await getRepository(repoId);
      const timeline = await getRepositoryTimeline(repoId);
      const graph = await getRepositoryGraph(repoId);

      console.log("repo:", repo);
      console.log("timeline:", timeline);
      console.log("graph:", graph);

      setResult({
        ...repo,
        timeline: timeline,
        graph
      });
    };

    fetchData();
  }, [repoId]);

  if (!result) {
    return <div>Loading repository...</div>;
  }

return (
    <div className="page">
      <div>

        {result && (
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
                  <LineChart data={result.activity}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={formatDate} />
                    <YAxis allowDecimals={false} />
                    <Tooltip labelFormatter={(value) => formatDate(value as string)}/>
                    <Line
                      type="monotone"
                      dataKey="commits"
                      stroke="#2563eb"
                      strokeWidth={3}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {result?.timeline?.timeline && (
              <div className="stat full">
                <h3>Historique des commits</h3>
                <CommitTimeline timeline={result?.timeline?.timeline} />
              </div>
            )}

            {result?.tree && (
              <div className="stat full">
                <h3>Arborescence du projet</h3>
                <RepoTree
                  tree={result?.tree}
                  onSelectFile={(file) => {
                    console.log("Fichier sélectionné :", file);
                  }}
                />
              </div>
            )}

            <DependencyGraph repoId={repoId} />
          </>
        )}
      </div>
    </div>
  );
}

export default RepoPage;