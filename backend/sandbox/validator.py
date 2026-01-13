"""
Code Validator - Security Checks for Python Code

Validates code for safety before execution by checking for:
- Forbidden imports
- Dangerous operations
- Network access attempts
- File system access attempts
"""

import ast
import re
from typing import Optional

import sys
sys.path.insert(0, '..')

from shared.config import settings
from shared.logging_config import get_logger

logger = get_logger(__name__)


# Forbidden modules that could be dangerous
FORBIDDEN_MODULES = {
    # System access
    'os', 'sys', 'subprocess', 'shutil', 'pathlib',
    'glob', 'fnmatch', 'tempfile', 'fileinput',
    
    # Network access
    'socket', 'http', 'urllib', 'requests', 'httpx',
    'ftplib', 'smtplib', 'poplib', 'imaplib', 'telnetlib',
    'ssl', 'asyncio.streams',
    
    # Code execution
    'code', 'codeop', 'compile', 'exec', 'eval',
    'importlib', 'imp', 'pkgutil', 'modulefinder',
    
    # Process/thread control
    'multiprocessing', 'threading', 'concurrent',
    'signal', 'atexit',
    
    # Low-level access
    'ctypes', 'cffi', 'mmap', 'resource',
    
    # Pickle (can execute arbitrary code)
    'pickle', 'cPickle', 'shelve', 'marshal',
    
    # Other dangerous modules
    'builtins', '__builtins__', 'gc', 'inspect',
    'traceback', 'linecache', 'dis', 'symtable',
}

# Forbidden function calls
FORBIDDEN_CALLS = {
    'exec', 'eval', 'compile', 'open', 'input',
    '__import__', 'getattr', 'setattr', 'delattr',
    'globals', 'locals', 'vars', 'dir',
    'breakpoint', 'help', 'exit', 'quit',
}

# Forbidden attribute access patterns
FORBIDDEN_ATTRIBUTES = {
    '__class__', '__bases__', '__subclasses__',
    '__mro__', '__code__', '__globals__',
    '__builtins__', '__dict__', '__module__',
    '__import__', '__loader__', '__spec__',
}


class CodeValidator:
    """Validates Python code for safety before execution."""
    
    def __init__(self):
        self.allowed_imports = set(settings.sandbox_allowed_imports_list)
    
    def validate(self, code: str) -> dict:
        """
        Validate code for safety.
        
        Args:
            code: Python code to validate
            
        Returns:
            Dict with safe (bool), issues (list), blocked_imports, blocked_operations
        """
        issues = []
        blocked_imports = []
        blocked_operations = []
        
        # Check for syntax errors first
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "safe": False,
                "issues": [{"type": "syntax", "message": f"Syntax error: {e.msg}", "line": e.lineno}],
                "blocked_imports": [],
                "blocked_operations": [],
            }
        
        # AST-based checks
        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if module in FORBIDDEN_MODULES:
                        issues.append({
                            "type": "import",
                            "message": f"Import of '{alias.name}' is not allowed",
                            "line": node.lineno,
                        })
                        blocked_imports.append(alias.name)
                    elif module not in self.allowed_imports:
                        issues.append({
                            "type": "import",
                            "message": f"Import of '{alias.name}' is not in allowed list",
                            "line": node.lineno,
                        })
                        blocked_imports.append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    if module in FORBIDDEN_MODULES:
                        issues.append({
                            "type": "import",
                            "message": f"Import from '{node.module}' is not allowed",
                            "line": node.lineno,
                        })
                        blocked_imports.append(node.module)
                    elif module not in self.allowed_imports:
                        issues.append({
                            "type": "import",
                            "message": f"Import from '{node.module}' is not in allowed list",
                            "line": node.lineno,
                        })
                        blocked_imports.append(node.module)
            
            # Check function calls
            elif isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name in FORBIDDEN_CALLS:
                    issues.append({
                        "type": "call",
                        "message": f"Call to '{func_name}' is not allowed",
                        "line": node.lineno,
                    })
                    blocked_operations.append(func_name)
            
            # Check attribute access
            elif isinstance(node, ast.Attribute):
                if node.attr in FORBIDDEN_ATTRIBUTES:
                    issues.append({
                        "type": "attribute",
                        "message": f"Access to '{node.attr}' is not allowed",
                        "line": node.lineno,
                    })
                    blocked_operations.append(node.attr)
        
        # Regex-based checks for patterns that might bypass AST
        regex_issues = self._check_regex_patterns(code)
        issues.extend(regex_issues)
        
        return {
            "safe": len(issues) == 0,
            "issues": issues,
            "blocked_imports": list(set(blocked_imports)),
            "blocked_operations": list(set(blocked_operations)),
        }
    
    def _get_call_name(self, node: ast.Call) -> Optional[str]:
        """Extract function name from Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return None
    
    def _check_regex_patterns(self, code: str) -> list:
        """Check for dangerous patterns using regex."""
        issues = []
        
        # Check for string-based exec/eval
        patterns = [
            (r'exec\s*\(', "Potential exec() call detected"),
            (r'eval\s*\(', "Potential eval() call detected"),
            (r'compile\s*\(', "Potential compile() call detected"),
            (r'__import__\s*\(', "Potential __import__() call detected"),
            (r'open\s*\(', "Potential open() call detected"),
            (r'subprocess', "Reference to subprocess module"),
            (r'os\.system', "Reference to os.system"),
            (r'os\.popen', "Reference to os.popen"),
            (r'socket\.', "Reference to socket module"),
            (r'urllib\.', "Reference to urllib module"),
            (r'requests\.', "Reference to requests module"),
        ]
        
        for pattern, message in patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                # Find line number
                line_num = code[:match.start()].count('\n') + 1
                issues.append({
                    "type": "pattern",
                    "message": message,
                    "line": line_num,
                })
        
        # Check for attempts to access dunder attributes via strings
        dunder_pattern = r'["\']__\w+__["\']'
        for match in re.finditer(dunder_pattern, code):
            line_num = code[:match.start()].count('\n') + 1
            issues.append({
                "type": "pattern",
                "message": f"Suspicious dunder string: {match.group()}",
                "line": line_num,
            })
        
        return issues
    
    def quick_check(self, code: str) -> bool:
        """
        Quick safety check without detailed analysis.
        
        Returns True if code appears safe, False otherwise.
        """
        # Quick regex checks
        dangerous_patterns = [
            r'\bimport\s+os\b',
            r'\bimport\s+sys\b',
            r'\bimport\s+subprocess\b',
            r'\bfrom\s+os\b',
            r'\bexec\s*\(',
            r'\beval\s*\(',
            r'\bopen\s*\(',
            r'__import__',
            r'__class__',
            r'__subclasses__',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                return False
        
        return True
