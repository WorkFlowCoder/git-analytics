import { Tree } from "react-arborist";
import "./RepoTree.css";
import { useEffect, useRef, useMemo } from "react";

type Node = {
  id: string;
  name: string;
  type: "file" | "directory";
  children?: Node[];
};

type Props = {
  tree: Node;
  onSelectFile?: (filePath: string) => void;
};

function buildId(node: Node, parentPath = ""): Node {
  const currentPath = parentPath
    ? `${parentPath}/${node.name}`
    : node.name;

  return {
    ...node,
    id: currentPath,
    children: node.children?.map(child =>
      buildId(child, currentPath)
    ),
  };
}

function buildPath(node: any): string {
  const parts: string[] = [];
  let current = node;

  while (current) {
    parts.unshift(current.data.name);
    current = current.parent;
  }

  return parts.join("/");
}

function sortTree(node: Node): Node {
  if (!node.children) return node;

  const sorted = [...node.children]
    .sort((a, b) => {
      if (a.type === b.type) {
        return a.name.localeCompare(b.name);
      }
      return a.type === "directory" ? -1 : 1;
    })
    .map(sortTree);

  return {
    ...node,
    children: sorted,
  };
}

export default function RepoTree({ tree, onSelectFile }: Props) {
  const treeRef = useRef<any>(null);
  const preparedTree = useMemo(() => {
    const withIds = buildId(tree as Node);
    return sortTree(withIds);
  }, [tree]);

  useEffect(() => {
    if (!treeRef.current) return;

    const root = treeRef.current.root;

    root.children.forEach((child: any) => {
        if (child.data.type === "directory") {
        child.open();
        }
    });
  }, [preparedTree]);

  return (
    <div className="repo-tree" style={{ height: "600px" }}>
      <Tree
        ref={treeRef}
        data={[preparedTree]}
        childrenAccessor="children"
        idAccessor="id"
        openByDefault={false}
      >
        {({ node, style, dragHandle }) => {
          const isDir = node.data.type === "directory";

          return (
            <div
              ref={dragHandle}
              style={{
                ...style,
                display: "flex",
                alignItems: "center",
                gap: 6,
                cursor: "pointer",
                fontSize: "14px",
                color: "#222",
                minWidth: 0
              }}
              onClick={() => {
                if (isDir) {
                  node.toggle();
                } else {
                  onSelectFile?.(buildPath(node));
                }
              }}
            >
              <span style={{ width: 18 }}>
                {isDir ? (node.isOpen ? "📂" : "📁") : "📄"}
              </span>

              <span>{node.data.name}</span>
            </div>
          );
        }}
      </Tree>
    </div>
  );
}