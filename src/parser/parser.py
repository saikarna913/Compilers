"""
FluxScript Parser Module

This module implements the parser for the FluxScript language. It converts a stream of tokens from the lexer into an abstract syntax tree (AST) for further compilation or interpretation.

Features:
- Recursive descent parsing for statements and expressions
- Handles variable declarations, control flow, functions, arrays, and dictionaries
- Tracks scope and variables for free variable analysis
- Error handling and synchronization for robust parsing

Usage:
    lexer = Lexer(code)
    parser = Parser(lexer)
    ast = parser.parse()
"""

from src.lexer.lexer import (Lexer, Token, LET, IF, WHILE, FOR, FUNC, RETURN, PRINT, ELSE, ASSIGN, EQUALS,
                            PLUS, MINUS, MULTIPLY, DIVIDE, EXPONENT, REM, LPAREN, RPAREN, LBRACE, RBRACE,
                            LT, GT, LTE, GTE, EQEQ, NOTEQ, AND, OR, NOT, COMMA, LBRACKET, RBRACKET, COLON,
                            IDENTIFIER, INTEGER, FLOAT, STRING, TRUE, FALSE, EOF, TO, STEP, BREAK, CONTINUE)
from src.AST.ast_1 import (AST, BinOp, UnaryOp, Integer, Float, String, Boolean, Var, VarAssign, VarReassign, Block,
                           If, While, For, FuncDef, Return, FuncCall, Print, Array, Dict, Break, Continue, AstPrinter,
                           ArrayAccess, ArrayAssign, Lambda)
from typing import List, Set

class ParseError(Exception):
    """Exception raised for parsing errors."""
    pass

class Parser:
    """
    FluxScript Parser
    Converts a list of tokens into an abstract syntax tree (AST).
    Attributes:
        lexer: The lexer instance
        tokens: List of tokens
        pos: Current position in the token list
        scope_level: Current scope depth
        variables: Set of defined variables for free variable analysis
    """
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.tokens = self._tokenize()
        self.pos = 0
        self.scope_level = 0  # Track current scope depth
        self.variables = set()  # Track defined variables for free_vars analysis

    def _tokenize(self):
        """
        Tokenize the input using the lexer and return a list of tokens.
        Raises ParseError on lexer errors.
        """
        tokens = []
        while True:
            try:
                token = self.lexer.get_next_token()
                tokens.append(token)
                if token.type == EOF:
                    break
            except Exception as e:
                # Convert lexer error to parse error without printing
                error_msg = str(e)
                raise ParseError(error_msg)
        return tokens

    def peek(self):
        """Return the current token without advancing."""
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.pos]

    def advance(self):
        """Advance to the next token and return it."""
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return self.tokens[-1]  # EOF

    def previous(self):
        """Return the previous token."""
        if self.pos > 0:
            return self.tokens[self.pos - 1]
        raise ParseError("No previous token available.")

    def check(self, token_type):
        """Check if the current token matches the given type."""
        return self.peek().type == token_type

    def is_at_end(self):
        """Check if the parser has reached the end of input."""
        return self.peek().type == EOF

    def match(self, *types):
        """Advance if the current token matches any of the given types."""
        if self.peek().type in types:
            return self.advance()
        return None

    def consume(self, token_type: str, message: str, suggestion: str = ""):
        """Consume a token of the expected type or raise a ParseError."""
        if self.peek().type == token_type:
            return self.advance()
        error_msg = f"[line {self.peek().line}] Error at '{self.peek().value}': {message}"
        if suggestion:
            error_msg += f" Suggestion: {suggestion}"
        # Don't print the error, just raise it
        raise ParseError(error_msg)

    def synchronize(self):
        """Synchronize the parser after an error to a known good state."""
        self.advance()
        while not self.is_at_end():
            if self.previous().type == RBRACE or self.peek().type in (LET, IF, WHILE, FOR, FUNC, RETURN, PRINT):
                return
            self.advance()

    def parse(self) -> Block:
        """
        Parse the entire input and return the root Block node.
        Handles top-level statements and error recovery.
        """
        statements = []
        self.scope_level = 0
        self.variables = set()
        while not self.is_at_end():
            try:
                stmt = self.statement()
                if stmt:
                    statements.append(stmt)
            except ParseError as e:
                # Don't print the error here, just synchronize and continue
                if "Lexer Error" in str(e):
                    raise e  # Re-raise lexer errors as ParseErrors
                self.synchronize()
        return Block(statements, scope_level=self.scope_level)

    def statement(self) -> AST:
        """
        Parse a single statement (let, if, while, for, break, continue, func, return, print, or expression).
        """
        if self.peek().type == LET:
            return self.let_statement()
        if self.peek().type == IF:
            return self.if_statement()
        if self.peek().type == WHILE:
            return self.while_statement()
        if self.peek().type == FOR:
            return self.for_statement()
        if self.peek().type == BREAK:
            return self.break_statement()
        if self.peek().type == CONTINUE:
            return self.continue_statement()
        if self.peek().type == FUNC:
            return self.function_definition()
        if self.peek().type == RETURN:
            return self.return_statement()
        if self.peek().type == PRINT:
            return self.print_statement()
        
        # Handle binary expressions directly at the statement level
        return self.expression_statement()

    def let_statement(self) -> VarAssign:
        """Parse a variable declaration statement."""
        let_token = self.advance()  # Consume 'let'
        if not self.check(IDENTIFIER):
            raise self.error(let_token, "Expected variable name after 'let'", "Use a valid identifier")
        name_token = self.consume(IDENTIFIER, "Expected variable name after 'let'", "Use a valid identifier")
        self.variables.add(name_token.value)
        self.consume(EQUALS, "Expected '=' after variable name", "Assign a value with '='")
        value = self.expression()
        return VarAssign(name_token.value, value, name_token)

    def if_statement(self) -> If:
        """Parse an if-else statement."""
        if_token = self.advance()  # Consume 'if'
        self.consume(LPAREN, "Expected '(' after 'if'", "Enclose condition in parentheses")
        condition = self.expression()
        self.consume(RPAREN, "Expected ')' after condition", "Close condition with ')'")
        then_branch = self.block()
        else_branch = None
        if self.peek().type == ELSE:
            self.advance()  # Consume 'else'
            else_branch = self.block()
        return If(condition, then_branch, else_branch)

    def while_statement(self) -> While:
        """Parse a while loop statement."""
        self.advance()  # Consume 'while'
        self.consume(LPAREN, "Expected '(' after 'while'", "Enclose condition in parentheses")
        condition = self.expression()
        self.consume(RPAREN, "Expected ')' after condition", "Close condition with ')'")
        body = self.block()
        return While(condition, body)

    def for_statement(self) -> For:
        """Parse a for loop statement."""
        token = self.advance()  # Consume 'for'
        self.consume(LPAREN, "Expected '(' after 'for'", "Start for loop with '('")
        self.consume(LET, "Expected 'let' after 'for ('", "Declare loop variable with 'let'")
        name_token = self.consume(IDENTIFIER, "Expected variable name", "Use a valid identifier")
        self.variables.add(name_token.value)
        self.consume(EQUALS, "Expected '=' after variable name", "Initialize variable with '='")
        start = self.expression()
        self.consume(TO, "Expected 'to' after start expression", "Specify loop range with 'to'")
        end = self.expression()
        step = None
        if self.match(STEP):
            step = self.expression()
        self.consume(RPAREN, "Expected ')' after for loop header", "Close for loop with ')'")
        body = self.block()
        return For(name_token.value, start, end, body, step, token)

    def break_statement(self) -> Break:
        """Parse a break statement."""
        token = self.advance()  # Consume 'break'
        return Break(token=token)

    def continue_statement(self) -> Continue:
        """Parse a continue statement."""
        token = self.advance()  # Consume 'continue'
        return Continue(token=token)

    def function_definition(self) -> FuncDef:
        """Parse a function definition statement."""
        func_token = self.advance()  # Consume 'func'
        if not self.check(IDENTIFIER):
            raise self.error(func_token, "Expected function name after 'func'", "Use a valid identifier")
        name_token = self.consume(IDENTIFIER, "Expected function name after 'func'", "Use a valid identifier")
        self.variables.add(name_token.value)
        self.consume(LPAREN, "Expected '(' after function name", "Start parameters with '('")
        params = []
        if self.peek().type != RPAREN:
            param = self.consume(IDENTIFIER, "Expected parameter name", "Use a valid identifier")
            params.append(param.value)
            self.variables.add(param.value)
            while self.match(COMMA):
                param = self.consume(IDENTIFIER, "Expected parameter name after ','", "Use a valid identifier")
                params.append(param.value)
                self.variables.add(param.value)
        self.consume(RPAREN, "Expected ')' after parameters", "Close parameters with ')'")
        self.scope_level += 1
        body = self.block()
        # Analyze free variables
        free_vars = self.analyze_free_vars(body, params)
        self.scope_level -= 1
        return FuncDef(name_token.value, params, body, free_vars=free_vars, scope_level=self.scope_level, token=name_token)

    def return_statement(self) -> Return:
        """Parse a return statement."""
        token = self.advance()  # Consume 'return'
        expr = self.expression()
        return Return(expr, token=token)

    def print_statement(self) -> Print:
        """Parse a print statement."""
        self.advance()  # Consume 'print'
        expr = self.expression()
        return Print(expr)

    def block(self) -> Block:
        """
        Parse a block of statements enclosed in braces.
        Increases scope level for variable tracking.
        """
        self.consume(LBRACE, "Expected '{' to start block", "Start block with '{'")
        self.scope_level += 1
        statements = []
        while self.peek().type not in (RBRACE, EOF):
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        self.consume(RBRACE, "Expected '}' to end block", "Close block with '}'")
        block = Block(statements, scope_level=self.scope_level)
        self.scope_level -= 1
        return block

    def expression_statement(self) -> AST:
        """Parse an expression statement, including assignments and binary expressions."""
        # First, try to parse a normal expression
        start_pos = self.pos
        expr = self.expression()
        
        # Handle array assignment after an expression
        if isinstance(expr, ArrayAccess) and self.peek().type == ASSIGN:
            token = self.advance()  # Consume 'assign'
            value = self.expression()
            return ArrayAssign(expr.array, expr.index, value, token)

        # Handle variable reassignment after an expression
        if isinstance(expr, Var) and self.peek().type == ASSIGN:
            token = self.advance()  # Consume 'assign'
            value = self.expression()
            return VarReassign(expr.name, value, token)

        # If we got a variable and there are more tokens that could form a binary operation
        if isinstance(expr, Var) and not self.is_at_end() and self.peek().type in (PLUS, MINUS, MULTIPLY, DIVIDE, EXPONENT, REM):
            # Reset parser position to retry parsing the complete expression
            self.pos = start_pos
            
            # Parse using the full expression grammar
            left = self.term()  # Start with term level to handle precedence correctly
            
            return left
        
        return expr

    def expression(self) -> AST:
        """Parse an expression (entry point for expressions)."""
        return self.logic_or()

    def logic_or(self) -> AST:
        """Parse logical OR expressions."""
        expr = self.logic_and()
        while self.match(OR):
            op = self.previous()
            right = self.logic_and()
            expr = BinOp(expr, op, right)
        return expr

    def logic_and(self) -> AST:
        """Parse logical AND expressions."""
        expr = self.equality()
        while self.match(AND):
            op = self.previous()
            right = self.equality()
            expr = BinOp(expr, op, right)
        return expr

    def equality(self) -> AST:
        """Parse equality (==, !=) expressions."""
        expr = self.comparison()
        while self.match(EQEQ, NOTEQ):
            op = self.previous()
            right = self.comparison()
            expr = BinOp(expr, op, right)
        return expr

    def comparison(self) -> AST:
        """Parse comparison (<, >, <=, >=) expressions."""
        expr = self.term()
        while self.match(LT, GT, LTE, GTE):
            op = self.previous()
            right = self.term()
            expr = BinOp(expr, op, right)
        return expr

    def term(self) -> AST:
        """Parse addition and subtraction expressions."""
        expr = self.factor()
        while self.match(PLUS, MINUS):
            op = self.previous()
            right = self.factor()
            expr = BinOp(expr, op, right)
        return expr

    def factor(self) -> AST:
        """Parse multiplication, division, and remainder expressions."""
        expr = self.power()
        while self.match(MULTIPLY, DIVIDE, REM):
            op = self.previous()
            right = self.power()
            expr = BinOp(expr, op, right)
        return expr

    def power(self) -> AST:
        """Parse exponentiation expressions."""
        expr = self.unary()
        while self.match(EXPONENT):
            op = self.previous()
            right = self.unary()
            expr = BinOp(expr, op, right)
        return expr

    def unary(self) -> AST:
        """Parse unary operations (negation, logical NOT)."""
        if self.match(MINUS, NOT):
            op = self.previous()
            right = self.unary()
            # Create a UnaryOp instead of optimizing to Integer
            return UnaryOp(op, right)
        return self.call()

    def call(self) -> AST:
        """Parse function call expressions."""
        expr = self.primary()
        while self.match(LPAREN):
            args = []
            if self.peek().type != RPAREN:
                args.append(self.expression())
                while self.match(COMMA):
                    args.append(self.expression())
            token = self.consume(RPAREN, "Expected ')' after arguments", "Close function call with ')'")
            expr = FuncCall(expr, args, token=token)
        return expr

    def primary(self) -> AST:
        """
        Parse primary expressions: literals, variables, grouped expressions, arrays, dictionaries, and array access.
        Handles special cases for array append and assignment.
        """
        if self.match(INTEGER):
            return Integer(self.previous().value)
        if self.match(FLOAT):
            return Float(self.previous().value)
        if self.match(STRING):
            return String(self.previous().value)
        if self.match(TRUE):
            return Boolean(True)
        if self.match(FALSE):
            return Boolean(False)
        if self.match(IDENTIFIER):
            token = self.previous()
            name = token.value
            
            # Check for array access: arr[index]
            if self.match(LBRACKET):
                index = self.expression()
                self.consume(RBRACKET, "Expected ']' after array index", "Close array access with ']'")
                array_access = ArrayAccess(Var(name, token), index, token)
                
                # Handle nested array access for 2D arrays: arr[index1][index2]
                while self.match(LBRACKET):
                    index = self.expression()
                    self.consume(RBRACKET, "Expected ']' after array index", "Close array access with ']'")
                    array_access = ArrayAccess(array_access, index, token)
                
                # Check for array assignment: arr[index] assign value
                if self.match(ASSIGN):
                    value = self.expression()
                    return ArrayAssign(array_access.array, array_access.index, value, token)
                
                return array_access
            
            # Check for array append: arr append value or arr append to value
            if self.peek().type == IDENTIFIER and self.peek().value == "append":
                self.advance()  # Consume 'append'
                
                # Check for optional 'to' token for readability: arr append to value
                if self.peek().type == IDENTIFIER and self.peek().value == "to":
                    self.advance()  # Consume 'to'
                
                # Parse the value to append
                value = self.expression()
                
                # Create a function call to a special "__append" function
                return FuncCall(
                    callee=Var("__append", token),
                    args=[Var(name, token), value],
                    token=token
                )
            
            return Var(name, token)
            
        if self.match(LPAREN):
            expr = self.expression()
            self.consume(RPAREN, "Expected ')' after expression", "Close expression with ')'")
            return expr
        if self.match(LBRACKET):
            elements = []
            if self.peek().type != RBRACKET:
                elements.append(self.expression())
                while self.match(COMMA):
                    elements.append(self.expression())
            self.consume(RBRACKET, "Expected ']' after array elements", "Close array with ']'")
            return Array(elements)
        if self.match(LBRACE):
            pairs = []
            if self.peek().type != RBRACE:
                key = self.expression()
                self.consume(COLON, "Expected ':' after dict key", "Separate key and value with ':'")
                value = self.expression()
                pairs.append((key, value))
                while self.match(COMMA):
                    key = self.expression()
                    self.consume(COLON, "Expected ':' after dict key", "Separate key and value with ':'")
                    value = self.expression()
                    pairs.append((key, value))
            self.consume(RBRACE, "Expected '}' after dict pairs", "Close dictionary with '}'")
            return Dict(pairs)
        raise self.error(self.peek(), "Expected expression", "Check for a valid number, string, boolean, variable, or expression")

    def analyze_free_vars(self, node: AST, params: List[str]) -> List[str]:
        """
        Analyze free variables in a function body, excluding parameters and local variables.
        Returns a list of free variable names.
        """
        free_vars = set()
        local_vars = set(params)
        
        def collect_vars(n: AST, locals_so_far=None):
            if locals_so_far is None:
                locals_so_far = set(local_vars)
                
            if isinstance(n, Var):
                if n.name not in locals_so_far and n.name not in self.variables:
                    free_vars.add(n.name)
            elif isinstance(n, VarAssign):
                # First process the right side with current locals
                if n.value:
                    collect_vars(n.value, locals_so_far)
                # Then add the new variable to locals
                locals_so_far.add(n.name)
            elif isinstance(n, VarReassign):
                # For reassignment, first check if it's a free variable reference
                if n.name not in locals_so_far and n.name not in self.variables:
                    free_vars.add(n.name)
                # Then process the value
                if n.value:
                    collect_vars(n.value, locals_so_far)
            elif isinstance(n, ArrayAccess):
                # Process the array and index expressions
                collect_vars(n.array, locals_so_far)
                collect_vars(n.index, locals_so_far)
            elif isinstance(n, ArrayAssign):
                # Process array, index, and value expressions
                collect_vars(n.array, locals_so_far)
                collect_vars(n.index, locals_so_far)
                collect_vars(n.value, locals_so_far)
            elif isinstance(n, Block):
                # Use a copy of locals for the block
                block_locals = set(locals_so_far)
                for stmt in n.statements:
                    collect_vars(stmt, block_locals)
            elif isinstance(n, If):
                collect_vars(n.condition, locals_so_far)
                collect_vars(n.then_branch, locals_so_far)
                if n.else_branch:
                    collect_vars(n.else_branch, locals_so_far)
            elif isinstance(n, While):
                collect_vars(n.condition, locals_so_far)
                collect_vars(n.body, locals_so_far)
            elif isinstance(n, For):
                # Process start and end expressions with current locals
                collect_vars(n.start, locals_so_far)
                collect_vars(n.end, locals_so_far)
                if n.step:
                    collect_vars(n.step, locals_so_far)
                
                # Add the loop variable to locals for the body
                body_locals = set(locals_so_far)
                body_locals.add(n.variable)
                collect_vars(n.body, body_locals)
            elif isinstance(n, FuncDef):
                # Process the function body with its parameters as locals
                func_locals = set(locals_so_far)
                func_locals.update(n.params)
                collect_vars(n.body, func_locals)
            elif isinstance(n, FuncCall):
                collect_vars(n.callee, locals_so_far)
                for arg in n.args:
                    collect_vars(arg, locals_so_far)
            elif isinstance(n, Return):
                if n.value:
                    collect_vars(n.value, locals_so_far)
            elif isinstance(n, Print):
                if n.expression:
                    collect_vars(n.expression, locals_so_far)
            elif isinstance(n, BinOp):
                collect_vars(n.left, locals_so_far)
                collect_vars(n.right, locals_so_far)
            elif isinstance(n, UnaryOp):
                collect_vars(n.right, locals_so_far)
            elif isinstance(n, Array):
                for elem in n.elements:
                    collect_vars(elem, locals_so_far)
            elif isinstance(n, Dict):
                for key, value in n.pairs:
                    collect_vars(key, locals_so_far)
                    collect_vars(value, locals_so_far)

        collect_vars(node)
        return list(free_vars)

    def error(self, token, message, suggestion=""):
        """Create a ParseError with a helpful message and suggestion."""
        error_msg = f"[line {token.line}] Error at '{token.value}': {message}"
        if suggestion:
            error_msg += f" Suggestion: {suggestion}"
        return ParseError(error_msg)

def parse_code(code: str) -> Block:
    """Helper function to parse code and print the AST."""
    lexer = Lexer(code)
    parser = Parser(lexer)
    ast = parser.parse()
    printer = AstPrinter()
    print(printer.print(ast))
    return ast

if __name__ == "__main__":
    # Example usage: parse a sample FluxScript program
    code = """
    let x = 5
    let y = 10
    if (x > 0) {
        print x
    } else {
        print y
    }
    func counter() {
        let count = 0
        return func() {
            count assign count + 1
            return count
        }
    }
    """
    parse_code(code)