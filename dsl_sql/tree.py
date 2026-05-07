from .models import Node


def tree_to_text(node: Node, indent: str = "", is_last: bool = True) -> str:
    branch = "└── " if is_last else "├── "
    label = node.name if node.value is None else f"{node.name}: {node.value}"
    lines = [indent + branch + label]

    next_indent = indent + ("    " if is_last else "│   ")
    for i, child in enumerate(node.children):
        lines.append(tree_to_text(child, next_indent, i == len(node.children) - 1))
    return "\n".join(lines)
