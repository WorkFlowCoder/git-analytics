import os

def scan_repo(path):
    files = []

    for root, _, filenames in os.walk(path):
        for f in filenames:
            ext = f.split(".")[-1]
            full = os.path.join(root, f)
            files.append((full, ext))

    return files