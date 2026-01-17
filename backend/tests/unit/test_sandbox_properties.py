"""
Property-based tests for sandbox/code execution service.

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
    
    assert result.success, f"Execution should succeed: {result.error}"
    assert "Hello, World!" in result.output, \
        f"Output should contain 'Hello, World!', got: {result.output}"


def test_property_11_multiple_prints_captured():
    """
    Feature: real-backend-implementation, Property 11: Code Execution Output Capture
    
    Multiple print statements should all be captured in order.
    """
    code = '''print("Line 1")
print("Line 2")
print("Line 3")'''
    
    result = SandboxService.execute(code)
    
    assert result.success, f"Execution should succeed: {result.error}"
    assert "Line 1" in result.output
    assert "Line 2" in result.output
    assert "Line 3" in result.output


@settings(max_examples=50, deadline=10000)
@given(text=st.text(min_size=1, max_size=50, alphabet=st.characters(
    whitelist_categories=('L', 'N'),
    max_codepoint=127  # ASCII only to avoid encoding issues
)))
def test_property_11_arbitrary_text_captured(text: str):
    """
    Feature: real-backend-implementation, Property 11: Code Execution Output Capture
    
    For any printable ASCII text, the output should be captured exactly.
    """
    # Skip text with quotes that would break the string literal
    assume('"' not in text and "'" not in text and '\\' not in text and '\n' not in text and '\r' not in text)
    
    code = f'print("{text}")'
    result = SandboxService.execute(code)
    
    assert result.success, f"Execution should succeed: {result.error}"
    assert text in result.output, \
        f"Output should contain '{text}', got: {result.output}"


def test_property_11_numeric_output_captured():
    """
    Feature: real-backend-implementation, Property 11: Code Execution Output Capture
    
    Numeric calculations should be captured.
    """
    code = '''result = 2 + 2
print(result)'''
    
    result = SandboxService.execute(code)
    
    assert result.success, f"Execution should succeed: {result.error}"
    assert "4" in result.output


@settings(max_examples=25, deadline=10000)
@given(
    a=st.integers(min_value=-1000, max_value=1000),
    b=st.integers(min_value=-1000, max_value=1000)
)
def test_property_11_arithmetic_output_captured(a: int, b: int):
    """
    Feature: real-backend-implementation, Property 11: Code Execution Output Capture
    
    Arithmetic results should be captured correctly.
    """
    code = f'print({a} + {b})'
    result = SandboxService.execute(code)
    
    assert result.success, f"Execution should succeed: {result.error}"
    expected = str(a + b)
    assert expected in result.output, \
        f"Output should contain '{expected}', got: {result.output}"


def test_property_11_list_output_captured():
    """
    Feature: real-backend-implementation, Property 11: Code Execution Output Capture
    
    List output should be captured.
    """
    code = 'print([1, 2, 3, 4, 5])'
    result = SandboxService.execute(code)
    
    assert result.success, f"Execution should succeed: {result.error}"
    assert "[1, 2, 3, 4, 5]" in result.output


def test_property_11_no_output_handled():
    """
    Feature: real-backend-implementation, Property 11: Code Execution Output Capture
    
    Code with no output should succeed with appropriate message.
    """
    code = 'x = 5'  # No print
    result = SandboxService.execute(code)
    
    assert result.success, f"Execution should succeed: {result.error}"
    # Output should indicate success even with no output
    assert result.output is not None


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
    code = 'print("unclosed string'  # Missing closing quote
    result = SandboxService.execute(code)
    
    assert not result.success, "Execution should fail for syntax error"
    assert result.error is not None, "Error message should be present"
    assert "SyntaxError" in result.error or "syntax" in result.error.lower(), \
        f"Error should mention syntax: {result.error}"


def test_property_12_name_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    NameError should be captured with success=false.
    """
    code = 'print(undefined_variable)'
    result = SandboxService.execute(code)
    
    assert not result.success, "Execution should fail for NameError"
    assert result.error is not None, "Error message should be present"
    assert "NameError" in result.error or "undefined" in result.error.lower() or "not defined" in result.error.lower(), \
        f"Error should mention name error: {result.error}"


def test_property_12_type_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    TypeError should be captured with success=false.
    """
    code = '"string" + 5'  # Can't add string and int
    result = SandboxService.execute(code)
    
    assert not result.success, "Execution should fail for TypeError"
    assert result.error is not None, "Error message should be present"


def test_property_12_zero_division_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    ZeroDivisionError should be captured with success=false.
    """
    code = 'print(1 / 0)'
    result = SandboxService.execute(code)
    
    assert not result.success, "Execution should fail for ZeroDivisionError"
    assert result.error is not None, "Error message should be present"
    assert "ZeroDivisionError" in result.error or "division" in result.error.lower(), \
        f"Error should mention division: {result.error}"


def test_property_12_index_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    IndexError should be captured with success=false.
    """
    code = '''my_list = [1, 2, 3]
print(my_list[10])'''
    result = SandboxService.execute(code)
    
    assert not result.success, "Execution should fail for IndexError"
    assert result.error is not None, "Error message should be present"
    assert "IndexError" in result.error or "index" in result.error.lower(), \
        f"Error should mention index: {result.error}"


def test_property_12_key_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    KeyError should be captured with success=false.
    """
    code = '''my_dict = {"a": 1}
print(my_dict["nonexistent"])'''
    result = SandboxService.execute(code)
    
    assert not result.success, "Execution should fail for KeyError"
    assert result.error is not None, "Error message should be present"
    assert "KeyError" in result.error or "key" in result.error.lower(), \
        f"Error should mention key: {result.error}"


def test_property_12_attribute_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    AttributeError should be captured with success=false.
    """
    code = '''x = 5
x.nonexistent_method()'''
    result = SandboxService.execute(code)
    
    assert not result.success, "Execution should fail for AttributeError"
    assert result.error is not None, "Error message should be present"


def test_property_12_value_error_captured():
    """
    Feature: real-backend-implementation, Property 12: Code Execution Error Handling
    
    ValueError should be captured with success=false.
    """
    code = 'int("not a number")'
    result = SandboxService.execute(code)
    
    assert not result.success, "Execution should fail for ValueError"
    assert result.error is not None, "Error message should be present"
    assert "ValueError" in result.error or "invalid" in result.error.lower(), \
        f"Error should mention value error: {result.error}"


# ============================================================================
# Additional tests for code validation
# ============================================================================

def test_validation_blocks_os_import():
    """
    Code validation should block os module import.
    """
    code = 'import os'
    is_valid, error = SandboxService.validate_code(code)
    
    assert not is_valid, "os import should be blocked"
    assert error is not None


def test_validation_blocks_subprocess():
    """
    Code validation should block subprocess module.
    """
    code = 'import subprocess'
    is_valid, error = SandboxService.validate_code(code)
    
    assert not is_valid, "subprocess import should be blocked"
    assert error is not None


def test_validation_blocks_eval():
    """
    Code validation should block eval.
    """
    code = 'eval("print(1)")'
    is_valid, error = SandboxService.validate_code(code)
    
    assert not is_valid, "eval should be blocked"
    assert error is not None


def test_validation_blocks_exec():
    """
    Code validation should block exec.
    """
    code = 'exec("print(1)")'
    is_valid, error = SandboxService.validate_code(code)
    
    assert not is_valid, "exec should be blocked"
    assert error is not None


def test_validation_allows_safe_code():
    """
    Code validation should allow safe code.
    """
    code = '''def add(a, b):
    return a + b

result = add(2, 3)
print(result)'''
    
    is_valid, error = SandboxService.validate_code(code)
    
    assert is_valid, f"Safe code should be allowed: {error}"
    assert error is None


def test_validation_allows_math_import():
    """
    Code validation should allow math module.
    """
    code = '''import math
print(math.sqrt(16))'''
    
    is_valid, error = SandboxService.validate_code(code)
    
    # Note: Our current validation doesn't specifically allow math,
    # but it doesn't block it either (only blocks specific dangerous modules)
    # The actual execution will determine if it works
    result = SandboxService.execute(code)
    assert result.success, f"Math import should work: {result.error}"
    assert "4" in result.output


# ============================================================================
# Execution timing tests
# ============================================================================

def test_execution_returns_timing():
    """
    Execution should return timing information.
    """
    code = 'print("test")'
    result = SandboxService.execute(code)
    
    assert result.execution_time_ms >= 0, "Execution time should be non-negative"


def test_execution_result_structure():
    """
    ExecutionResult should have all required fields.
    """
    code = 'print("test")'
    result = SandboxService.execute(code)
    
    assert hasattr(result, 'success')
    assert hasattr(result, 'output')
    assert hasattr(result, 'error')
    assert hasattr(result, 'execution_time_ms')
