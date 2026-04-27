import networkx as nx

from app.services.repo_scanner import scan_repo
from app.services.parsers.registry import get_parser
from app.services.parsers.python import extract_python_deps

def resolve_import(import_stmt, file_path):
    # version simplifiée
    import_stmt = import_stmt.split(" ")[-1].replace("'", "").replace('"', "")

    # ex: utils.helper → utils/helper.py
    path = import_stmt.replace(".", "/") + ".py"

    return path

def build_graph(repo_path):
    G = nx.DiGraph()
    files = scan_repo(repo_path)

    for file_path, ext in files:
        if ext not in ["py", "js"]:
            continue

        parser = get_parser(ext)

        with open(file_path, "r", encoding="utf8") as f:
            code = f.read()

        tree = parser.parse(bytes(code, "utf8"))

        if ext == "py":
            deps = extract_python_deps(tree, code)
        #elif ext == "js":
        #    deps = extract_js_deps(tree)

        for dep in deps:
            target = resolve_import(dep, file_path)
            G.add_edge(file_path, target, type="import")

    return G