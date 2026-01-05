"""
Code Validator - Detects dangerous imports and code patterns.
Prevents execution of potentially harmful Python code.
"""

import ast
import re
from typing import NamedTuple


class ValidationResult(NamedTuple):
    is_safe: bool
    violations: list[str]


# Dangerous modules that should never be imported
DANGEROUS_MODULES = {
    "os",
    "subprocess",
    "socket",
    "sys",
    "shutil",
    "pathlib",
    "glob",
    "tempfile",
    "multiprocessing",
    "threading",
    "ctypes",
    "importlib",
    "builtins",
    "__builtins__",
    "pickle",
    "marshal",
    "shelve",
    "dbm",
    "sqlite3",
    "urllib",
    "http",
    "ftplib",
    "smtplib",
    "telnetlib",
    "ssl",
    "asyncio",
    "concurrent",
    "signal",
    "resource",
    "pty",
    "tty",
    "termios",
    "fcntl",
    "pipes",
    "posix",
    "pwd",
    "grp",
    "crypt",
    "spwd",
    "syslog",
    "commands",
    "popen2",
}

# Dangerous built-in functions
DANGEROUS_BUILTINS = {
    "eval",
    "exec",
    "compile",
    "open",
    "input",
    "__import__",
    "globals",
    "locals",
    "vars",
    "dir",
    "getattr",
    "setattr",
    "delattr",
    "hasattr",
    "breakpoint",
    "memoryview",
}

# Dangerous attribute access patterns
DANGEROUS_ATTRIBUTES = {
    "__class__",
    "__bases__",
    "__subclasses__",
    "__mro__",
    "__globals__",
    "__code__",
    "__builtins__",
    "__import__",
    "__loader__",
    "__spec__",
}


class CodeValidator(ast.NodeVisitor):
    """AST visitor that checks for dangerous code patterns."""

    def __init__(self):
        self.violations: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            module_name = alias.name.split(".")[0]
            if module_name in DANGEROUS_MODULES:
                self.violations.append(f"Dangerous import: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            module_name = node.module.split(".")[0]
            if module_name in DANGEROUS_MODULES:
                self.violations.append(f"Dangerous import from: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        # Check for dangerous built-in calls
        if isinstance(node.func, ast.Name):
            if node.func.id in DANGEROUS_BUILTINS:
                self.violations.append(f"Dangerous function call: {node.func.id}()")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        # Check for dangerous attribute access
        if node.attr in DANGEROUS_ATTRIBUTES:
            self.violations.append(f"Dangerous attribute access: {node.attr}")
        self.generic_visit(node)


def validate_code(code: str) -> ValidationResult:
    """
    Validate Python code for security issues.

    Args:
        code: Python source code to validate

    Returns:
        ValidationResult with is_safe flag and list of violations
    """
    violations: list[str] = []

    # Check for obvious dangerous patterns with regex first
    dangerous_patterns = [
        (r"__import__\s*\(", "Direct __import__ call"),
        (r"exec\s*\(", "exec() call"),
        (r"eval\s*\(", "eval() call"),
        (r"compile\s*\(", "compile() call"),
        (r"open\s*\(", "open() call - file access not allowed"),
        (r"\.read\s*\(", "File read operation"),
        (r"\.write\s*\(", "File write operation"),
    ]

    for pattern, message in dangerous_patterns:
        if re.search(pattern, code):
            violations.append(message)

    # Parse and analyze AST
    try:
        tree = ast.parse(code)
        validator = CodeValidator()
        validator.visit(tree)
        violations.extend(validator.violations)
    except SyntaxError as e:
        violations.append(f"Syntax error: {e.msg} at line {e.lineno}")

    # Remove duplicates while preserving order
    seen = set()
    unique_violations = []
    for v in violations:
        if v not in seen:
            seen.add(v)
            unique_violations.append(v)

    return ValidationResult(
        is_safe=len(unique_violations) == 0,
        violations=unique_violations,
    )


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("print('Hello')", True),
        ("import os", False),
        ("from subprocess import run", False),
        ("eval('1+1')", False),
        ("x = 1 + 2\nprint(x)", True),
        ("open('file.txt')", False),
        ("obj.__class__.__bases__", False),
    ]

    for code, expected_safe in test_cases:
        result = validate_code(code)
        status = "✓" if result.is_safe == expected_safe else "✗"
        print(f"{status} Code: {code[:30]!r}... Safe: {result.is_safe}")
        if result.violations:
            for v in result.violations:
                print(f"    - {v}")
