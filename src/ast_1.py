# ast_1.py
from dataclasses import dataclass
from typing import Union

@dataclass
class AST:
    """Base AST node class"""
    pass

@dataclass
class BinOp(AST):
    """Binary operation node (for arithmetic, comparisons, and logical operators)"""
    left: AST
    op: str
    right: AST

@dataclass
class Number(AST):
    """Numeric node for both integers and floats"""
    value: Union[int, float]

@dataclass
class UnaryOp(AST):
    """Unary operation node (for arithmetic unary ops and logical not)"""
    op: str
    expr: AST

@dataclass
class Boolean(AST):
    """Boolean literal node"""
    value: bool

@dataclass
class Var(AST):
    """Variable reference node"""
    name: str

@dataclass
class VarAssign(AST):
    """Variable declaration node using 'let'"""
    name: str
    value: AST

@dataclass
class VarReassign(AST):
    """Variable reassignment node using 'assign'"""
    name: str
    value: AST

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
    elif isinstance(node, Boolean):
        print(f"{indent}Boolean({node.value})")
    elif isinstance(node, Var):
        print(f"{indent}Var({node.name})")
    elif isinstance(node, VarAssign):
        print(f"{indent}VarAssign({node.name})")
        print_ast(node.value, level + 1)
    elif isinstance(node, VarReassign):
        print(f"{indent}VarReassign({node.name})")
        print_ast(node.value, level + 1)
