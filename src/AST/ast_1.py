"""
FluxScript Abstract Syntax Tree (AST) Module

This module defines the Abstract Syntax Tree (AST) nodes for the FluxScript programming language.
An AST represents the hierarchical structure of the source code after parsing, where each node
represents a construct in the source code.

The module implements the Visitor pattern to allow operations on the AST, such as interpretation,
compilation, or visualization.

Features:
- Comprehensive set of node types for expressions, statements, and control structures
- Support for variables, functions, arrays, and dictionaries
- Visitor pattern implementation for traversing and operating on the AST
- Pretty printer for AST visualization

Usage:
    # Creating AST nodes
    bin_op = BinOp(left=Integer(1), operator=Token(PLUS, '+', 1), right=Integer(2))
    
    # Using the visitor pattern
    result = bin_op.accept(my_visitor)
    
    # Printing the AST
    printer = AstPrinter()
    print(printer.print(ast_node))
"""
from dataclasses import dataclass
from typing import Union, Optional, List, Tuple, Any
from src.lexer.lexer import Token  
import re

@dataclass
class AST:
    """
    Base AST node class that all other node types inherit from.
    
    Implements the Visitor pattern through the accept method, which dispatches
    to the appropriate visitor method based on the node's class name.
    """
    def accept(self, visitor: 'Visitor') -> Any:
        """
        Accept method for the Visitor pattern.
        
        Automatically determines the correct visit method to call based on the class name.
        For example, a BinOp node will call visitor.visit_bin_op().
        
        Args:
            visitor: The visitor object that will process this node
            
        Returns:
            The result of the visitor's processing
        """
        class_name = self.__class__.__name__
        method_name = f"visit_{re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()}"
        return getattr(visitor, method_name)(self)

@dataclass
class BinOp(AST):
    """
    Binary operation node representing operations with two operands.
    
    Examples include addition, subtraction, multiplication, division,
    comparison operations, and logical operations.
    
    Attributes:
        left: The left operand (AST node)
        operator: The token representing the operation
        right: The right operand (AST node)
    """
    left: AST
    operator: Token
    right: AST

@dataclass
class UnaryOp(AST):
    """
    Unary operation node representing operations with a single operand.
    
    Examples include negation (-x) and logical NOT (not x).
    
    Attributes:
        operator: The token representing the operation
        right: The operand (AST node)
    """
    operator: Token
    right: AST

@dataclass
class Integer(AST):
    """
    Integer literal node representing whole number values.
    
    Attributes:
        value: The integer value
    """
    value: int

@dataclass
class Float(AST):
    """
    Float literal node representing floating-point number values.
    
    Attributes:
        value: The floating-point value
    """
    value: float

@dataclass
class Boolean(AST):
    """
    Boolean literal node representing True or False values.
    
    Attributes:
        value: The boolean value (True or False)
    """
    value: bool

@dataclass
class String(AST):
    """
    String literal node representing text values.
    
    Attributes:
        value: The string value
    """
    value: str

@dataclass
class Var(AST):
    """
    Variable reference node representing the use of a variable.
    
    Attributes:
        name: The variable name
        token: The original token for error reporting
    """
    name: str
    token: Token

@dataclass
class VarAssign(AST):
    """
    Variable declaration node representing the 'let' statement.
    Used for initial variable declaration and assignment.
    
    Attributes:
        name: The variable name
        value: The value to assign (AST node)
        token: The original token for error reporting
    """
    name: str
    value: AST
    token: Token

@dataclass
class VarReassign(AST):
    """
    Variable reassignment node representing the 'assign' statement.
    Used for updating the value of an existing variable.
    
    Attributes:
        name: The variable name
        value: The new value to assign (AST node)
        token: The original token for error reporting
    """
    name: str
    value: AST
    token: Token

@dataclass
class Block(AST):
    """
    Block of statements representing a sequence of statements.
    Used for function bodies, if/else bodies, loop bodies, etc.
    
    Attributes:
        statements: List of statement nodes
        scope_level: The nesting level of this block (for variable scope tracking)
    """
    statements: List[AST]
    scope_level: int = 0

@dataclass
class If(AST):
    """
    If statement node representing conditional execution.
    
    Attributes:
        condition: The condition to evaluate (AST node)
        then_branch: The code to execute if condition is true (AST node)
        else_branch: Optional code to execute if condition is false (AST node)
    """
    condition: AST
    then_branch: AST
    else_branch: Optional[AST] = None

@dataclass
class While(AST):
    """
    While loop node representing pre-condition loop execution.
    The loop continues as long as the condition evaluates to true.
    
    Attributes:
        condition: The loop condition (AST node)
        body: The loop body to execute (AST node)
    """
    condition: AST
    body: AST

@dataclass
class For:
    """
    For loop node representing iteration over a range of values.
    
    Attributes:
        variable: The loop variable name
        start: The starting value (AST node)
        end: The ending value (AST node)
        body: The loop body to execute (AST node)
        step: Optional step size (AST node)
        token: The original token for error reporting
    """
    def __init__(self, variable, start, end, body, step=None, token=None):
        self.variable = variable
        self.start = start
        self.end = end
        self.body = body
        self.step = step
        self.token = token
        
    def accept(self, visitor):
        """
        Accept method for the Visitor pattern.
        
        Args:
            visitor: The visitor object that will process this node
            
        Returns:
            The result of the visitor's processing
        """
        method_name = f'visit_{self.__class__.__name__.lower()}'
        return getattr(visitor, method_name)(self)

@dataclass
class RepeatUntil(AST):
    """
    Repeat-until loop node representing post-condition loop execution.
    The loop continues until the condition evaluates to true.
    
    Attributes:
        body: The loop body to execute (AST node)
        condition: The loop condition (AST node)
    """
    body: AST
    condition: AST

@dataclass
class Match(AST):
    """
    Match statement node representing pattern matching.
    Similar to switch/case statements in other languages.
    
    Attributes:
        expression: The expression to match against (AST node)
        cases: List of match cases (MatchCase nodes)
    """
    expression: AST
    cases: List['MatchCase']

@dataclass
class MatchCase(AST):
    """
    Case in a match statement representing a single pattern-body pair.
    
    Attributes:
        pattern: The pattern to match (AST node)
        body: The code to execute if the pattern matches (AST node)
    """
    pattern: AST
    body: AST

@dataclass
class FuncDef(AST):
    """
    Function definition node representing a function or method declaration.
    
    Attributes:
        name: The function name
        params: List of parameter names
        body: The function body (AST node)
        free_vars: List of free variables captured from outer scopes
        scope_level: Nesting level for variable scoping
        env: Optional environment for closure handling
        token: The original token for error reporting
    """
    name: str
    params: List[str]
    body: AST
    free_vars: List[str] = None
    scope_level: int = 0
    env: Optional[Any] = None
    token: Optional[Token] = None

@dataclass
class FuncCall(AST):
    """
    Function call node representing a function invocation.
    
    Attributes:
        callee: The function to call (AST node)
        args: List of argument expressions (AST nodes)
        token: The original token for error reporting
    """
    callee: AST
    args: List[AST]
    token: Optional[Token] = None

@dataclass
class Return(AST):
    """
    Return statement node representing returning a value from a function.
    
    Attributes:
        value: The value to return (AST node)
        token: The original token for error reporting
    """
    value: AST
    token: Optional[Token] = None
    
@dataclass
class Lambda(AST):
    """
    Anonymous function expression representing a lambda/closure.
    
    Attributes:
        params: List of parameter names
        body: The function body (AST node)
        token: The original token for error reporting
    """
    params: List[str]
    body: AST
    token: Optional[Token] = None

@dataclass
class Array(AST):
    """
    Array literal node representing a list of values.
    
    Attributes:
        elements: List of element expressions (AST nodes)
    """
    elements: List[AST]

@dataclass
class ArrayAccess(AST):
    """
    Array access node representing indexing into an array (e.g., arr[0]).
    
    Attributes:
        array: The array expression (AST node)
        index: The index expression (AST node)
        token: The original token for error reporting
    """
    array: AST  
    index: AST  
    token: any = None  
    
    def accept(self, visitor):
        """
        Accept method for the Visitor pattern.
        
        Args:
            visitor: The visitor object that will process this node
            
        Returns:
            The result of the visitor's processing
        """
        return visitor.visit_array_access(self)

@dataclass
class MultiDimArrayAccess(AST):
    """
    Multi-dimensional array access node representing nested indexing (e.g., arr[0][1][2]).
    
    Attributes:
        array: The array expression (AST node)
        indices: List of index expressions (AST nodes)
        token: The original token for error reporting
    """
    array: AST
    indices: List[AST]
    token: any = None
    
    def accept(self, visitor):
        """
        Accept method for the Visitor pattern.
        
        Args:
            visitor: The visitor object that will process this node
            
        Returns:
            The result of the visitor's processing
        """
        return visitor.visit_multi_dim_array_access(self)

@dataclass
class ArrayAssign(AST):
    """
    Array assignment node representing updating an array element (e.g., arr[1] = 5).
    
    Attributes:
        array: The array expression (AST node)
        index: The index expression (AST node)
        value: The value to assign (AST node)
        token: The original token for error reporting
    """
    array: AST
    index: AST
    value: AST
    token: any = None 
    
    def accept(self, visitor):
        """
        Accept method for the Visitor pattern.
        
        Args:
            visitor: The visitor object that will process this node
            
        Returns:
            The result of the visitor's processing
        """
        return visitor.visit_array_assign(self)

@dataclass
class MultiDimArrayAssign(AST):
    """
    Multi-dimensional array assignment node representing nested updates (e.g., arr[0][1] = 5).
    
    Attributes:
        array: The array expression (AST node)
        indices: List of index expressions (AST nodes)
        value: The value to assign (AST node)
        token: The original token for error reporting
    """
    array: AST
    indices: List[AST]
    value: AST
    token: any = None
    
    def accept(self, visitor):
        """
        Accept method for the Visitor pattern.
        
        Args:
            visitor: The visitor object that will process this node
            
        Returns:
            The result of the visitor's processing
        """
        return visitor.visit_multi_dim_array_assign(self)

@dataclass
class SizeOf(AST):
    """
    Size operation node representing getting the size of a collection (e.g., size(arr)).
    
    Attributes:
        expression: The collection expression (AST node)
        token: The original token for error reporting
    """
    expression: AST
    token: any = None
    
    def accept(self, visitor):
        """
        Accept method for the Visitor pattern.
        
        Args:
            visitor: The visitor object that will process this node
            
        Returns:
            The result of the visitor's processing
        """
        return visitor.visit_size_of(self)

@dataclass
class Dict(AST):
    """
    Dictionary literal node representing a key-value mapping.
    
    Attributes:
        pairs: List of key-value pairs (AST nodes)
    """
    pairs: List[Tuple[AST, AST]]

@dataclass
class ConditionalExpr(AST):
    """
    Conditional expression node representing ternary operations (expr if cond else expr).
    
    Attributes:
        condition: The condition to evaluate (AST node)
        then_expr: The expression to evaluate if condition is true (AST node)
        else_expr: The expression to evaluate if condition is false (AST node)
    """
    condition: AST
    then_expr: AST
    else_expr: AST

@dataclass
class Print(AST):
    """
    Print statement node representing output to console.
    
    Attributes:
        expression: The expression to print (AST node)
        token: The original token for error reporting
    """
    expression: AST
    token: Optional[Token] = None

class Break:
    """
    Break statement node representing early exit from a loop.
    
    Attributes:
        token: The original token for error reporting
    """
    def __init__(self, token=None):
        self.token = token
        
    def accept(self, visitor):
        """
        Accept method for the Visitor pattern.
        
        Args:
            visitor: The visitor object that will process this node
            
        Returns:
            The result of the visitor's processing
        """
        method_name = f'visit_{self.__class__.__name__.lower()}'
        return getattr(visitor, method_name)(self)

class Continue:
    """
    Continue statement node representing skipping to the next iteration of a loop.
    
    Attributes:
        token: The original token for error reporting
    """
    def __init__(self, token=None):
        self.token = token
        
    def accept(self, visitor):
        """
        Accept method for the Visitor pattern.
        
        Args:
            visitor: The visitor object that will process this node
            
        Returns:
            The result of the visitor's processing
        """
        method_name = f'visit_{self.__class__.__name__.lower()}'
        return getattr(visitor, method_name)(self)

# Visitor interface
class Visitor:
    """
    Visitor interface for operating on AST nodes.
    
    This class defines the interface for all operations on the AST. Concrete
    visitors should inherit from this class and implement the specific visit
    methods for each node type they need to handle.
    
    Common visitor implementations include:
    - Interpreters: Directly execute the code
    - Compilers: Generate bytecode or machine code
    - Type checkers: Perform static analysis
    - Pretty printers: Visualize the AST
    """
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
    """
    Visitor implementation for visualizing the AST as a string.
    
    This class generates a readable textual representation of the AST that
    can be used for debugging, logging, or understanding the structure of
    the parsed program.
    """
    def print(self, node: AST) -> str:
        """
        Print an AST node and its children as a string.
        
        Args:
            node: The root node to print
            
        Returns:
            A string representation of the AST
        """
        return node.accept(self)

    def parenthesize(self, name: str, *nodes: AST) -> str:
        """
        Helper method to format a node and its children with parentheses.
        
        Args:
            name: The name to give this node
            *nodes: Child nodes to include
            
        Returns:
            A formatted string representation
        """
        parts = [f"({name}"]
        for node in nodes:
            parts.append(" ")
            parts.append(node.accept(self))
        parts.append(")")
        return "".join(parts)

    def visit_bin_op(self, node: BinOp) -> str:
        """Format a binary operation node."""
        return self.parenthesize(node.operator.value, node.left, node.right)

    def visit_unary_op(self, node: UnaryOp) -> str:
        """Format a unary operation node."""
        return self.parenthesize(node.operator.value, node.right)

    def visit_integer(self, node: Integer) -> str:
        """Format an integer literal node."""
        return str(node.value)

    def visit_float(self, node: Float) -> str:
        """Format a float literal node."""
        return str(node.value)

    def visit_boolean(self, node: Boolean) -> str:
        """Format a boolean literal node."""
        return "True" if node.value else "False"

    def visit_string(self, node: String) -> str:
        """Format a string literal node."""
        return f'"{node.value}"'

    def visit_var(self, node: Var) -> str:
        """Format a variable reference node."""
        return node.name

    def visit_var_assign(self, node: VarAssign) -> str:
        """Format a variable declaration node."""
        return self.parenthesize(f"let {node.name}", node.value)

    def visit_var_reassign(self, node: VarReassign) -> str:
        """Format a variable reassignment node."""
        return self.parenthesize(f"assign {node.name}", node.value)

    def visit_block(self, node: Block) -> str:
        """Format a block of statements node."""
        scope_info = f" scope={node.scope_level}" if node.scope_level > 0 else ""
        return self.parenthesize(f"block{scope_info}", *node.statements)

    def visit_if(self, node: If) -> str:
        """Format an if statement node."""
        if (node.else_branch):
            return self.parenthesize("if", node.condition, node.then_branch, node.else_branch)
        return self.parenthesize("if", node.condition, node.then_branch)

    def visit_while(self, node: While) -> str:
        """Format a while loop node."""
        return self.parenthesize("while", node.condition, node.body)

    def visit_for(self, node: For) -> str:
        """Format a for loop node."""
        step_str = f" {node.step.accept(self)}" if node.step else ""
        return self.parenthesize(f"for {node.variable}", node.start, node.end, node.body) + step_str

    def visit_repeat_until(self, node: RepeatUntil) -> str:
        """Format a repeat-until loop node."""
        return self.parenthesize("repeat-until", node.body, node.condition)

    def visit_match(self, node: Match) -> str:
        """Format a match statement node."""
        expr_str = node.expression.accept(self)
        case_strings = [case.accept(self) for case in node.cases]
        cases_str = " ".join(case_strings)
        return f"(match {expr_str} {cases_str})"

    def visit_match_case(self, node: MatchCase) -> str:
        """Format a match case node."""
        return self.parenthesize("case", node.pattern, node.body)

    def visit_func_def(self, node: FuncDef) -> str:
        """Format a function definition node."""
        params = " ".join(node.params)
        env_info = f" env={id(node.env)}" if node.env else ""
        return self.parenthesize(f"func {node.name} {params}{env_info}", node.body)

    def visit_func_call(self, node: FuncCall) -> str:
        """Format a function call node."""
        return self.parenthesize("call", node.callee, *node.args)
    
    def visit_lambda(self, node: Lambda) -> str:
        """Format a lambda expression node."""
        params_str = ", ".join(node.params)
        return self.parenthesize(f"lambda ({params_str})", node.body)

    def visit_return(self, node: Return) -> str:
        """Format a return statement node."""
        return self.parenthesize("return", node.value)

    def visit_array(self, node: Array) -> str:
        """Format an array literal node."""
        return self.parenthesize("array", *node.elements)

    def visit_array_access(self, node: ArrayAccess) -> str:
        """Format an array access node."""
        array_str = node.array.accept(self)
        index_str = node.index.accept(self)
        return f"(array-access {array_str} {index_str})"
    
    def visit_multi_dim_array_access(self, node: MultiDimArrayAccess) -> str:
        """Format a multi-dimensional array access node."""
        array_str = node.array.accept(self)
        indices_str = " ".join(index.accept(self) for index in node.indices)
        return f"(multi-dim-array-access {array_str} {indices_str})"

    def visit_array_assign(self, node: ArrayAssign) -> str:
        """Format an array assignment node."""
        array_str = node.array.accept(self)
        index_str = node.index.accept(self)
        value_str = node.value.accept(self)
        return f"(array-assign {array_str} {index_str} {value_str})"

    def visit_multi_dim_array_assign(self, node: MultiDimArrayAssign) -> str:
        """Format a multi-dimensional array assignment node."""
        array_str = node.array.accept(self)
        indices_str = " ".join(index.accept(self) for index in node.indices)
        value_str = node.value.accept(self)
        return f"(multi-dim-array-assign {array_str} {indices_str} {value_str})"

    def visit_size_of(self, node: SizeOf) -> str:
        """Format a size-of operation node."""
        expression_str = node.expression.accept(self)
        return f"(size-of {expression_str})"

    def visit_dict(self, node: Dict) -> str:
        """Format a dictionary literal node."""
        pair_strings = [self.parenthesize("pair", key, value) for key, value in node.pairs]
        pairs_str = " ".join(pair_strings)
        return f"(dict {pairs_str})"

    def visit_conditional_expr(self, node: ConditionalExpr) -> str:
        """Format a conditional expression node."""
        return self.parenthesize("if-else", node.then_expr, node.condition, node.else_expr)

    def visit_print(self, node: Print) -> str:
        """Format a print statement node."""
        return self.parenthesize("print", node.expression)

    def visit_break(self, node: Break) -> str:
        """Format a break statement node."""
        return "(break)"

    def visit_continue(self, node: Continue) -> str:
        """Format a continue statement node."""
        return "(continue)"