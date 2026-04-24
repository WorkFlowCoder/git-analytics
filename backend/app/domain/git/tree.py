from pathlib import Path

def build_tree(path: Path):
    if path.is_file():
        return {
            "name": path.name,
            "type": "file"
        }

    return {
        "name": path.name,
        "type": "directory",
        "children": [
            build_tree(child)
            for child in sorted(path.iterdir())
            if child.name != ".git"
        ]
    }