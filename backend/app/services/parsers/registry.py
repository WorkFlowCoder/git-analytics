from tree_sitter import Parser
from tree_sitter_languages import get_language

LANGUAGES = {
    "py": get_language("python"),
    "js": get_language("javascript"),
    "ts": get_language("typescript"),
    "java": get_language("java"),
    "go": get_language("go"),
    "c": get_language("c"),
    "cpp": get_language("cpp"),
    "php": get_language("php"),
    "ruby": get_language("ruby"),
    "rust": get_language("rust"),
    "csharp": get_language("c_sharp"),
    "kotlin": get_language("kotlin"),
    "scala": get_language("scala"),
    "bash": get_language("bash"),
}

EXT_MAP = {
    "ts": "ts",
    "tsx": "ts",   # 👈 important
    "js": "js",
    "jsx": "js",
    "py": "py",
}

def get_parser(ext: str):
    parser = Parser()

    if ext in EXT_MAP:
        ext = EXT_MAP[ext]

    if ext not in LANGUAGES:
        raise ValueError(f"Unsupported language extension: {ext}")

    parser.set_language(LANGUAGES[ext])

    return parser