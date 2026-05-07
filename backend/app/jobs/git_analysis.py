from app.domain.git.analyzer import analyze_repo
from app.domain.git.persistence import persist_to_db, save_graph_to_db, delete_repo
from app.services.repo_service import sanitize_repo_name
from app.domain.git.tree import build_tree
from pathlib import Path

from app.services.graph_builder import build_graph
from app.domain.git.clone import clone_repo


import shutil
from pathlib import Path

# JOB ENTRYPOINT
def analyze_repo_job(repo_url: str, repo_id: int):
    repo_path = clone_repo(repo_url)
    try:
        data = analyze_repo(repo_path)
        tree = build_tree(Path(repo_path))
        graph = build_graph(repo_path)
        #print(f"Analysis graph built for {repo_url} : {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges", flush=True)
        #print(f"Analysis complete for {repo_url}, persisting to DB...", flush=True)
        data["tree"] = tree
        persist_to_db(repo_id, data)
        save_graph_to_db(repo_id, repo_path, graph)
        #print(f"Data persisted for {repo_url}", flush=True)
        data["repo_id"] = repo_id
        data["repo_url"] = repo_url
        repo_name = sanitize_repo_name(repo_url)
        return {
            "repo": repo_name,
            **data
        }
    except Exception as e:
        delete_repo(repo_id)
        raise e
    finally:
        #CLEANUP REPO
        try:
            if repo_path and Path(repo_path).exists():
                shutil.rmtree(repo_path)
                #print(f"Cleaned repo folder: {repo_path}", flush=True)
        except Exception as e:
            #print(f"Failed to clean repo folder: {e}", flush=True)
            pass