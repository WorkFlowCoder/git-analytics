from app.domain.git.analyzer import analyze_repo
from app.domain.git.persistence import persist_to_db, save_graph_to_db
from app.services.repo_service import sanitize_repo_name
from app.domain.git.tree import build_tree
from pathlib import Path

from app.services.graph_builder import build_graph

def analyze_repo_job(repo_path: str, repo_url: str, repo_id: int):
    """
    Job exécuté par le worker
    """
    data = analyze_repo(repo_path)
    tree = build_tree(Path(repo_path))
    graph = build_graph(repo_path)
    print(f"✅ Analysis graph built for {repo_url} : {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges", flush=True)
    #print(f"✅ Analysis complete for {repo_url}, persisting to DB...", flush=True)
    data["tree"] = tree
    persist_to_db(repo_id, data)
    save_graph_to_db(repo_id,graph)
    #print(f"✅ Data persisted for {repo_url}", flush=True)
    data["repo_id"] = repo_id
    data["repo_url"] = repo_url

    repo_name = sanitize_repo_name(repo_url)

    return {
        "repo": repo_name,
        **data
    }