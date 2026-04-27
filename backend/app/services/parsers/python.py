def extract_python_deps(tree, source_code):
    root = tree.root_node
    deps = set()

    def walk(node):
        # import x
        if node.type == "import_statement":
            deps.add(node.text.decode())

        # from x import y
        if node.type == "import_from_statement":
            deps.add(node.text.decode())

        for child in node.children:
            walk(child)

    walk(root)
    return list(deps)