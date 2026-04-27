from tree_sitter import Parser
import tree_sitter_python as tspython

LANGUAGES = {
    "py": tspython.language()
}

def get_parser(ext: str):
    parser = Parser()
    parser.set_language(LANGUAGES[ext])
    return parser