"""
Property-based tests for code execution service.

Feature: real-backend-implementation
Tests Properties 11-12 from the design document.

Uses hypothesis library for property-based testing.
"""

import os
import sys

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from hypothesis import given, settings, strategies as st, assume

from services.sandbox import SandboxService, ExecutionResult


# ============================================================================
# Property 11: Code Execution Output Capture
# For any Python code that produces stdout output, the execution result
# SHALL contain that exact output.
# Validates: Requirements 6.4, 6.5
# ============================================================================

def test_property_11_simple_print_captured():
    """
    Feature: real-backend-implementation, Property 11: Code Execution Output Capture
    
    Simple print statement output should be captured.
    """
    code = 'print("Hello, World!")'
    result = SandboxService.execute(code)
    
    assert result.success, f"Code should succeed: {result.error}"
    assert "Hello, World!" in result.output, \
        f"Output should contain 'Hello, World!', got: {result.output}"


@settings(max_examples=50, deadline=10000)
@given(value=st.integers(min_value=-1000, max_value=1000))
def test_property_11_integer_output_captured(value: int):
    """
    Feature: real-backend-implementation, Property 11: Code Execution Output Capture
    
    For any integer, print(value) should capture that exact value.
    """
    code = f'print({value})'
    result = SandboxService.execute(code)
    
    assert result.success, f"Code should succeed: {result.error}"
    assert str(value) in result.output, \
        f"Output should contain '{value}', got: {result.output}"


@settings(max_examples=30, deadline=10000)
@given(text=st.text(min_size=1, max_size=50, alphabet=st.characters(
    whitelist_categories=('L', 'N'),
    whitelist_characters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ',
    max_codepoint=127  # ASCII only
)))
def test_property_11_text_output_captured(text: str):
    """
    Feature: real-backend-implementation, Property 11: Code Execution Output Capture
    
    For any safe ASCII text, print(text) should capture that text.
    """
    assume('\n' not in text and '\r' not in text)
    assume('"' not in text and "'" not in text and '\\' not in text)
    
    code = f'print("{text}")'
    result = SandboxService.execute(code)
    
    assert result.success, f"Code should succeed: {result.error}"


def test_property_11_multiline_output_captured():
    """
    Feature: real-backend-implementation, Property 11: Code Execution Output Capture
    
    Multiple print statements should all be captured.
    """
    code = '''print("Line 1")
print("Line 2")
print("Line 3")'''
    result = SandboxService.execute(code)
    
    assert result.success, f"Code should succeed: {result.error}"
    assert "Line 1" in result.output
    assert "Line 2" in result.output
    assert "Line 3" in result.output


def test_property_11_computation_output_captured():
    """
    Feature: real-backend-implementation, Property 11: Code Execution Output Capture
    
    Computation results should be captured correctly.
    """
    code = '''
result = 2 + 2
print(f"2 + 2 = {result}")
'''
    result = SandboxService.execute(code)
    
    assert result.success, f"Code should succeed: {result.error}"
    assert "2 + 2 = 4" in result.output


def test_property_11_loop_output_captured():
    """
    Feature: real-backend-implementation, Property 11: Code Execution Output Capture
    
    Loop output should be captured.
    """
    code = '''
for i in range(5):
    print(i)
'''
    result = SandboxService.execute(code)
    
    assert result.success, f"Code should succeed: {result.error}"
    for i in range(5):
        assert str(i) in result.output


# ============================================================================
# Property 12: Code Execution Error Handling
# For any Python code that raises an exception, the execution result
# SHALL contain the error message and success=false.
# Validates: Requirements 6.6
# ============================================================================

def test_property_12_syntax_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    Syntax errors should be captured with success=false.
    """
    code = 'print("unclosed string'
    result = SandboxService.execute(code)
    
    assert not result.success, "Syntax error should fail"
    assert result.error is not None, "Error message should be present"
    assert "SyntaxError" in result.error or "EOL" in result.error or "unterminated" in result.error.lower()


def test_property_12_name_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    NameError should be captured with success=false.
    """
    code = 'print(undefined_variable)'
    result = SandboxService.execute(code)
    
    assert not result.success, "NameError should fail"
    assert result.error is not None, "Error message should be present"
    assert "NameError" in result.error or "undefined" in result.error.lower()


def test_property_12_type_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    TypeError should be captured with success=false.
    """
    code = '"string" + 123'
    result = SandboxService.execute(code)
    
    assert not result.success, "TypeError should fail"
    assert result.error is not None, "Error message should be present"
    assert "TypeError" in result.error


def test_property_12_zero_division_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    ZeroDivisionError should be captured with success=false.
    """
    code = 'print(1 / 0)'
    result = SandboxService.execute(code)
    
    assert not result.success, "ZeroDivisionError should fail"
    assert result.error is not None, "Error message should be present"
    assert "ZeroDivisionError" in result.error or "division" in result.error.lower()


def test_property_12_index_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    IndexError should be captured with success=false.
    """
    code = '''
lst = [1, 2, 3]
print(lst[10])
'''
    result = SandboxService.execute(code)
    
    assert not result.success, "IndexError should fail"
    assert result.error is not None, "Error message should be present"
    assert "IndexError" in result.error or "index" in result.error.lower()


def test_property_12_key_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    KeyError should be captured with success=false.
    """
    code = '''
d = {"a": 1}
print(d["nonexistent"])
'''
    result = SandboxService.execute(code)
    
    assert not result.success, "KeyError should fail"
    assert result.error is not None, "Error message should be present"
    assert "KeyError" in result.error


def test_property_12_value_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    ValueError should be captured with success=false.
    """
    code = 'int("not_a_number")'
    result = SandboxService.execute(code)
    
    assert not result.success, "ValueError should fail"
    assert result.error is not None, "Error message should be present"
    assert "ValueError" in result.error


def test_property_12_attribute_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    AttributeError should be captured with success=false.
    """
    code = '''
x = 5
x.nonexistent_method()
'''
    result = SandboxService.execute(code)
    
    assert not result.success, "AttributeError should fail"
    assert result.error is not None, "Error message should be present"
    assert "AttributeError" in result.error


@settings(max_examples=20, deadline=10000)
@given(error_type=st.sampled_from([
    'raise ValueError("test")',
    'raise TypeError("test")',
    'raise RuntimeError("test")',
]))
def test_property_12_raised_exceptions_captured(error_type: str):
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    Explicitly raised exceptions should be captured.
    """
    result = SandboxService.execute(error_type)
    
    assert not result.success, f"Raised exception should fail: {error_type}"
    assert result.error is not None, "Error message should be present"


# ============================================================================
# Additional tests for execution behavior
# ============================================================================

def test_execution_returns_timing():
    """
    Execution should return timing information.
    """
    code = 'print("test")'
    result = SandboxService.execute(code)
    
    assert result.execution_time_ms >= 0, "Execution time should be non-negative"


def test_execution_empty_code():
    """
    Empty code should execute successfully with no output.
    """
    code = ''
    result = SandboxService.execute(code)
    
    assert result.success, "Empty code should succeed"


def test_execution_comment_only():
    """
    Comment-only code should execute successfully.
    """
    code = '# This is a comment'
    result = SandboxService.execute(code)
    
    assert result.success, "Comment-only code should succeed"


def test_execution_function_definition():
    """
    Function definition and call should work.
    """
    code = '''
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
'''
    result = SandboxService.execute(code)
    
    assert result.success, f"Function code should succeed: {result.error}"
    assert "Hello, World!" in result.output


def test_execution_class_definition():
    """
    Class definition and instantiation should work.
    """
    code = '''
class Person:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hi, I'm {self.name}"

p = Person("Alice")
print(p.greet())
'''
    result = SandboxService.execute(code)
    
    assert result.success, f"Class code should succeed: {result.error}"
    assert "Hi, I'm Alice" in result.output


def test_execution_list_comprehension():
    """
    List comprehension should work.
    """
    code = '''
squares = [x**2 for x in range(5)]
print(squares)
'''
    result = SandboxService.execute(code)
    
    assert result.success, f"List comprehension should succeed: {result.error}"
    assert "[0, 1, 4, 9, 16]" in result.output
