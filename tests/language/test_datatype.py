import unittest
from unittest.mock import patch
from src.lexer import Lexer
from src.parser import Parser
from src.evaluator import Evaluator, FluxRuntimeError

class TestDataTypes(unittest.TestCase):
    def setUp(self):
        self.evaluator = Evaluator()

    def run_program(self, code):
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()
        return self.evaluator.interpret(ast)

    # Numbers (Integers and Floats)
    def test_number_declaration_and_arithmetic(self):
        code = """
        let x = 10
        let y = 3.14
        let sum = x + y
        let product = x * y
        print sum
        print product
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_any_call("13.14")  # 10 + 3.14
            mock_print.assert_any_call("31.4")   # 10 * 3.14

    def test_number_edge_cases(self):
        code = """
        let zero = 0
        let negative = -42
        let large = 1000000
        print zero
        print negative
        print large
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_any_call("0")
            mock_print.assert_any_call("-42")
            mock_print.assert_any_call("1000000")

    def test_number_division_by_zero(self):
        code = "print 10 / 0"
        with self.assertRaises(FluxRuntimeError) as cm:
            self.run_program(code)
        self.assertIn("Division by zero", str(cm.exception))

    # Booleans
    def test_boolean_declaration_and_operations(self):
        code = """
        let t = True
        let f = False
        print t and f
        print t or f
        print not t
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_any_call("False")  # True and False
            mock_print.assert_any_call("True")   # True or False
            mock_print.assert_any_call("False")  # not True

    def test_boolean_in_conditionals(self):
        code = """
        let flag = True
        if (flag) {
            print "Yes"
        } else {
            print "No"
        }
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("Yes")

    # Strings
    def test_string_declaration_and_concatenation(self):
        code = """
        let s1 = "Hello"
        let s2 = "World"
        let result = s1 + " " + s2
        print result
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("Hello World")

    def test_string_indexing_and_length(self):
        code = """
        let s = "FluxScript"
        print s[0]
        print s[4]
        print len(s)
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_any_call("F")       # s[0]
            mock_print.assert_any_call("S")       # s[4]
            mock_print.assert_any_call("10")      # len("FluxScript")

    def test_string_edge_cases(self):
        code = """
        let empty = ""
        print len(empty)
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("0")

    def test_string_index_out_of_bounds(self):
        code = """
        let s = "test"
        print s[10]
        """
        with self.assertRaises(FluxRuntimeError) as cm:
            self.run_program(code)
        self.assertIn("Index out of bounds", str(cm.exception))

    # Arrays
    def test_array_declaration_and_access(self):
        code = """
        let arr = [1, "two", True]
        print arr[0]
        print arr[1]
        print arr[2]
        print len(arr)
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_any_call("1")
            mock_print.assert_any_call("two")
            mock_print.assert_any_call("True")
            mock_print.assert_any_call("3")

    def test_array_modification(self):
        code = """
        let arr = [1, 2, 3]
        arr[1] assign 42
        print arr[1]
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("42")

    def test_array_edge_cases(self):
        code = """
        let empty = []
        print len(empty)
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("0")

    def test_array_index_out_of_bounds(self):
        code = """
        let arr = [1, 2, 3]
        print arr[5]
        """
        with self.assertRaises(FluxRuntimeError) as cm:
            self.run_program(code)
        self.assertIn("Index out of bounds", str(cm.exception))

    # Dictionaries (Desirable Feature)
    def test_dictionary_declaration_and_access(self):
        code = """
        let dict = { "key1": 42, "key2": "value" }
        print dict["key1"]
        print dict["key2"]
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_any_call("42")
            mock_print.assert_any_call("value")

    def test_dictionary_modification(self):
        code = """
        let dict = { "key": 0 }
        dict["key"] assign 100
        print dict["key"]
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("100")

    def test_dictionary_missing_key(self):
        code = """
        let dict = { "key": 42 }
        print dict["missing"]
        """
        with self.assertRaises(FluxRuntimeError) as cm:
            self.run_program(code)
        self.assertIn("Key not found", str(cm.exception))

    # Type Interactions
    def test_mixed_type_operations(self):
        code = """
        let num = 42
        let s = "The answer is " + str(num)
        print s
        """
        with patch('builtins.print') as mock_print:
            self.run_program(code)
            mock_print.assert_called_with("The answer is 42")

    def test_invalid_type_operation(self):
        code = """
        let s = "text"
        let n = 42
        print s + n
        """
        with self.assertRaises(FluxRuntimeError) as cm:
            self.run_program(code)
        self.assertIn("Operands must be two strings or a string and another type", str(cm.exception))

if __name__ == "__main__":
    unittest.main()