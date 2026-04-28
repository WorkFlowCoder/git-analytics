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

    # Initialize parsers only once per language
    parsers = {
        "py": get_parser("py"),
        # "js": get_parser("js"),
        # "java": get_parser("java"),
    }

    # Batch edge creation for better performance
    edges = []

    for file_path, ext in files:
        if ext not in parsers:
            continue

        parser = parsers[ext]

        try:
            # Read file safely in binary mode
            with open(file_path, "rb") as f:
                code_bytes = f.read()

            if not code_bytes:
                continue

            code = code_bytes.decode("utf-8", errors="ignore")

            # Parse AST with Tree-sitter
            tree = parser.parse(code_bytes)

            # Extract dependencies depending on language
            if ext == "py":
                deps = extract_python_deps(tree, code)

            # elif ext == "js":
            #     deps = extract_js_deps(tree)

            else:
                deps = []

            # Resolve imports and prepare graph edges
            for dep in deps:
                target = resolve_import(dep, file_path)

                if not target:
                    continue

                edges.append((
                    file_path,
                    target,
                    {
                        "type": "import",
                        "raw": dep
                    }
                ))

        except Exception as e:
            print(f"[DependencyGraph] Error parsing {file_path}: {e}")

    # Insert all edges at once (faster than add_edge in loop)
    G.add_edges_from(edges)

    return G