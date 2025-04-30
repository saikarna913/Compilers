from dataclasses import dataclass
from typing import Union, Optional, List, Tuple, Any
from src.lexer.lexer import Token  
import re

@dataclass
class AST:
    """Base AST node class"""
    def accept(self, visitor: 'Visitor') -> Any:
        """Accept method for the Visitor pattern"""
        class_name = self.__class__.__name__
        method_name = f"visit_{re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()}"
        return getattr(visitor, method_name)(self)

@dataclass
class BinOp(AST):
    """Binary operation node"""
    left: AST
    operator: Token
    right: AST

@dataclass
class UnaryOp(AST):
    """Unary operation node"""
    operator: Token
    right: AST

@dataclass
class Integer(AST):
    """Integer literal node"""
    value: int

@dataclass
class Float(AST):
    """Float literal node"""
    value: float

@dataclass
class Boolean(AST):
    """Boolean literal node"""
    value: bool

@dataclass
class String(AST):
    """String literal node"""
    value: str

@dataclass
class Var(AST):
    """Variable reference node"""
    name: str
    token: Token

@dataclass
class VarAssign(AST):
    """Variable declaration node (let)"""
    name: str
    value: AST
    token: Token

@dataclass
class VarReassign(AST):
    """Variable reassignment node (assign)"""
    name: str
    value: AST
    token: Token

@dataclass
class Block(AST):
    """Block of statements"""
    statements: List[AST]
    scope_level: int = 0

@dataclass
class If(AST):
    """If statement node"""
    condition: AST
    then_branch: AST
    else_branch: Optional[AST] = None

@dataclass
class While(AST):
    """While loop node"""
    condition: AST
    body: AST

@dataclass
class For:
    def __init__(self, variable, start, end, body, step=None, token=None):
        self.variable = variable
        self.start = start
        self.end = end
        self.body = body
        self.step = step
        self.token = token
        
    def accept(self, visitor):
        method_name = f'visit_{self.__class__.__name__.lower()}'
        return getattr(visitor, method_name)(self)

@dataclass
class RepeatUntil(AST):
    """Repeat-until loop node"""
    body: AST
    condition: AST

@dataclass
class Match(AST):
    """Match statement node"""
    expression: AST
    cases: List['MatchCase']

@dataclass
class MatchCase(AST):
    """Case in a match statement"""
    pattern: AST
    body: AST

@dataclass
class FuncDef(AST):
    """Function definition node"""
    name: str
    params: List[str]
    body: AST
    free_vars: List[str] = None
    scope_level: int = 0
    env: Optional[Any] = None
    token: Optional[Token] = None

@dataclass
class FuncCall(AST):
    """Function call node"""
    callee: AST
    args: List[AST]
    token: Optional[Token] = None

@dataclass
class Return(AST):
    """Return statement node"""
    value: AST
    token: Optional[Token] = None
    
@dataclass
class Lambda(AST):
    """Anonymous function expression"""
    params: List[str]
    body: AST
    token: Optional[Token] = None

@dataclass
class Array(AST):
    """Array literal node"""
    elements: List[AST]

@dataclass
class ArrayAccess(AST):
    """Represents accessing an array element (e.g., arr[0])"""
    array: AST  
    index: AST  
    token: any = None  # Optional token for error reporting or debugging
    
    def accept(self, visitor):
        return visitor.visit_array_access(self)

@dataclass
class MultiDimArrayAccess(AST):
    """Represents accessing a multi-dimensional array element (e.g., arr[0][1][2])"""
    array: AST
    indices: List[AST]
    token: any = None
    
    def accept(self, visitor):
        return visitor.visit_multi_dim_array_access(self)

@dataclass
class ArrayAssign(AST):
    """Represents assigning a value to an array index (e.g., arr[1] = 5)"""
    array: AST
    index: AST
    value: AST
    token: any = None 
    
    def accept(self, visitor):
        return visitor.visit_array_assign(self)

@dataclass
class MultiDimArrayAssign(AST):
    """Represents assigning a value to a multi-dimensional array (e.g., arr[0][1] = 5)"""
    array: AST
    indices: List[AST]
    value: AST
    token: any = None
    
    def accept(self, visitor):
        return visitor.visit_multi_dim_array_assign(self)

@dataclass
class SizeOf(AST):
    """Represents a size operation on a collection (e.g., size(arr))"""
    expression: AST
    token: any = None
    
    def accept(self, visitor):
        return visitor.visit_size_of(self)

@dataclass
class Dict(AST):
    """Dictionary literal node"""
    pairs: List[Tuple[AST, AST]]

@dataclass
class ConditionalExpr(AST):
    """Conditional expression node (expr if cond else expr)"""
    condition: AST
    then_expr: AST
    else_expr: AST

@dataclass
class Print(AST):
    """Print statement node"""
    expression: AST
    token: Optional[Token] = None

class Break:
    def __init__(self, token=None):
        self.token = token
        
    def accept(self, visitor):
        method_name = f'visit_{self.__class__.__name__.lower()}'
        return getattr(visitor, method_name)(self)

class Continue:
    def __init__(self, token=None):
        self.token = token
        
    def accept(self, visitor):
        method_name = f'visit_{self.__class__.__name__.lower()}'
        return getattr(visitor, method_name)(self)

# Visitor interface
class Visitor:
    def visit_bin_op(self, node: BinOp) -> Any: pass
    def visit_unary_op(self, node: UnaryOp) -> Any: pass
    def visit_integer(self, node: Integer) -> Any: pass
    def visit_float(self, node: Float) -> Any: pass
    def visit_boolean(self, node: Boolean) -> Any: pass
    def visit_string(self, node: String) -> Any: pass
    def visit_var(self, node: Var) -> Any: pass
    def visit_var_assign(self, node: VarAssign) -> Any: pass
    def visit_var_reassign(self, node: VarReassign) -> Any: pass
    def visit_block(self, node: Block) -> Any: pass
    def visit_if(self, node: If) -> Any: pass
    def visit_while(self, node: While) -> Any: pass
    def visit_for(self, node: For) -> Any: pass
    def visit_repeat_until(self, node: RepeatUntil) -> Any: pass
    def visit_match(self, node: Match) -> Any: pass
    def visit_match_case(self, node: MatchCase) -> Any: pass
    def visit_func_def(self, node: FuncDef) -> Any: pass
    def visit_func_call(self, node: FuncCall) -> Any: pass
    def visit_lambda(self, node: Lambda) -> Any: pass
    def visit_return(self, node: Return) -> Any: pass
    def visit_array(self, node: Array) -> Any: pass
    def visit_array_access(self, node: ArrayAccess) -> Any: pass
    def visit_multi_dim_array_access(self, node: MultiDimArrayAccess) -> Any: pass
    def visit_array_assign(self, node: ArrayAssign) -> Any: pass
    def visit_multi_dim_array_assign(self, node: MultiDimArrayAssign) -> Any: pass
    def visit_size_of(self, node: SizeOf) -> Any: pass
    def visit_dict(self, node: Dict) -> Any: pass
    def visit_conditional_expr(self, node: ConditionalExpr) -> Any: pass
    def visit_print(self, node: Print) -> Any: pass

# Pretty printer for AST visualization
class AstPrinter(Visitor):
    def print(self, node: AST) -> str:
        return node.accept(self)

    def parenthesize(self, name: str, *nodes: AST) -> str:
        parts = [f"({name}"]
        for node in nodes:
            parts.append(" ")
            parts.append(node.accept(self))
        parts.append(")")
        return "".join(parts)

    def visit_bin_op(self, node: BinOp) -> str:
        return self.parenthesize(node.operator.value, node.left, node.right)

    def visit_unary_op(self, node: UnaryOp) -> str:
        return self.parenthesize(node.operator.value, node.right)

    def visit_integer(self, node: Integer) -> str:
        return str(node.value)

    def visit_float(self, node: Float) -> str:
        return str(node.value)

    def visit_boolean(self, node: Boolean) -> str:
        return "True" if node.value else "False"

    def visit_string(self, node: String) -> str:
        return f'"{node.value}"'

    def visit_var(self, node: Var) -> str:
        return node.name

    def visit_var_assign(self, node: VarAssign) -> str:
        return self.parenthesize(f"let {node.name}", node.value)

    def visit_var_reassign(self, node: VarReassign) -> str:
        return self.parenthesize(f"assign {node.name}", node.value)

    def visit_block(self, node: Block) -> str:
        scope_info = f" scope={node.scope_level}" if node.scope_level > 0 else ""
        return self.parenthesize(f"block{scope_info}", *node.statements)

    def visit_if(self, node: If) -> str:
        if (node.else_branch):
            return self.parenthesize("if", node.condition, node.then_branch, node.else_branch)
        return self.parenthesize("if", node.condition, node.then_branch)

    def visit_while(self, node: While) -> str:
        return self.parenthesize("while", node.condition, node.body)

    def visit_for(self, node: For) -> str:
        step_str = f" {node.step.accept(self)}" if node.step else ""
        return self.parenthesize(f"for {node.variable}", node.start, node.end, node.body) + step_str

    def visit_repeat_until(self, node: RepeatUntil) -> str:
        return self.parenthesize("repeat-until", node.body, node.condition)

    def visit_match(self, node: Match) -> str:
        expr_str = node.expression.accept(self)
        case_strings = [case.accept(self) for case in node.cases]
        cases_str = " ".join(case_strings)
        return f"(match {expr_str} {cases_str})"

    def visit_match_case(self, node: MatchCase) -> str:
        return self.parenthesize("case", node.pattern, node.body)

    def visit_func_def(self, node: FuncDef) -> str:
        params = " ".join(node.params)
        env_info = f" env={id(node.env)}" if node.env else ""
        return self.parenthesize(f"func {node.name} {params}{env_info}", node.body)

    def visit_func_call(self, node: FuncCall) -> str:
        return self.parenthesize("call", node.callee, *node.args)
    
    def visit_lambda(self, node: Lambda) -> str:
        params_str = ", ".join(node.params)
        return self.parenthesize(f"lambda ({params_str})", node.body)

    def visit_return(self, node: Return) -> str:
        return self.parenthesize("return", node.value)

    def visit_array(self, node: Array) -> str:
        return self.parenthesize("array", *node.elements)

    def visit_array_access(self, node: ArrayAccess) -> str:
        array_str = node.array.accept(self)
        index_str = node.index.accept(self)
        return f"(array-access {array_str} {index_str})"
    
    def visit_multi_dim_array_access(self, node: MultiDimArrayAccess) -> str:
        array_str = node.array.accept(self)
        indices_str = " ".join(index.accept(self) for index in node.indices)
        return f"(multi-dim-array-access {array_str} {indices_str})"

    def visit_array_assign(self, node: ArrayAssign) -> str:
        array_str = node.array.accept(self)
        index_str = node.index.accept(self)
        value_str = node.value.accept(self)
        return f"(array-assign {array_str} {index_str} {value_str})"

    def visit_multi_dim_array_assign(self, node: MultiDimArrayAssign) -> str:
        array_str = node.array.accept(self)
        indices_str = " ".join(index.accept(self) for index in node.indices)
        value_str = node.value.accept(self)
        return f"(multi-dim-array-assign {array_str} {indices_str} {value_str})"

    def visit_size_of(self, node: SizeOf) -> str:
        expression_str = node.expression.accept(self)
        return f"(size-of {expression_str})"

    def visit_dict(self, node: Dict) -> str:
        pair_strings = [self.parenthesize("pair", key, value) for key, value in node.pairs]
        pairs_str = " ".join(pair_strings)
        return f"(dict {pairs_str})"

    def visit_conditional_expr(self, node: ConditionalExpr) -> str:
        return self.parenthesize("if-else", node.then_expr, node.condition, node.else_expr)

    def visit_print(self, node: Print) -> str:
        return self.parenthesize("print", node.expression)

    def visit_break(self, node: Break) -> str:
        return "(break)"

    def visit_continue(self, node: Continue) -> str:
        return "(continue)"