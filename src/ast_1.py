from dataclasses import dataclass
from typing import Union, Optional

@dataclass
class AST:
    """Base AST node class"""
    pass

@dataclass
class BinOp(AST):
    """Binary operation node"""
    left: AST
    op: str
    right: AST

@dataclass
class Number(AST):
    """Numeric node for both integers and floats"""
    value: Union[int, float]

@dataclass
class UnaryOp(AST):
    """Unary operation node"""
    op: str
    expr: AST


def print_ast(node: AST, level: int = 0) -> None:
    """Helper function to visualize AST structure"""
    indent = '  ' * level
    if isinstance(node, BinOp):
        print(f"{indent}BinOp({node.op})")
        print_ast(node.left, level + 1)
        print_ast(node.right, level + 1)
    elif isinstance(node, UnaryOp):
        print(f"{indent}UnaryOp({node.op})")
        print_ast(node.expr, level + 1)
    elif isinstance(node, Number):
        print(f"{indent}Number({node.value})")