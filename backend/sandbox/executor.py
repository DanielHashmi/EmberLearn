"""
Code Executor - Sandboxed Python Execution

Executes Python code with resource limits using subprocess.
"""

import asyncio
import subprocess
import tempfile
import os
import resource
import signal
from typing import Optional
from datetime import datetime

import sys
sys.path.insert(0, '..')

from shared.config import settings
from shared.logging_config import get_logger

logger = get_logger(__name__)


class CodeExecutor:
    """Executes Python code in a sandboxed environment."""
    
    def __init__(self):
        self.default_timeout = settings.sandbox_timeout_seconds
        self.default_memory_mb = settings.sandbox_memory_limit_mb
        self.allowed_imports = set(settings.sandbox_allowed_imports_list)
    
    async def execute(
        self,
        code: str,
        timeout_seconds: int = None,
        memory_limit_mb: int = None,
    ) -> dict:
        """
        Execute Python code with resource limits.
        
        Args:
            code: Python code to execute
            timeout_seconds: Maximum execution time
            memory_limit_mb: Maximum memory usage
            
        Returns:
            Dict with output, error, execution_time_ms, etc.
        """
        timeout = timeout_seconds or self.default_timeout
        memory_mb = memory_limit_mb or self.default_memory_mb
        
        # Create temporary file for code
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
        ) as f:
            # Wrap code with resource limits and output capture
            wrapped_code = self._wrap_code(code, memory_mb)
            f.write(wrapped_code)
            temp_path = f.name
        
        try:
            start_time = datetime.now()
            
            # Execute in subprocess with timeout
            result = await asyncio.wait_for(
                self._run_subprocess(temp_path, timeout),
                timeout=timeout + 1,  # Extra second for subprocess overhead
            )
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return {
                "success": result["returncode"] == 0,
                "output": result["stdout"],
                "error": result["stderr"] if result["returncode"] != 0 else None,
                "execution_time_ms": execution_time,
                "timed_out": False,
            }
            
        except asyncio.TimeoutError:
            execution_time = int(timeout * 1000)
            return {
                "success": False,
                "output": None,
                "error": f"Execution timed out after {timeout} seconds",
                "execution_time_ms": execution_time,
                "timed_out": True,
            }
        except Exception as e:
            logger.exception("execution_error", error=str(e))
            return {
                "success": False,
                "output": None,
                "error": str(e),
                "execution_time_ms": 0,
                "timed_out": False,
            }
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception:
                pass
    
    async def execute_test(
        self,
        code: str,
        test_input: str,
        expected_output: str,
        timeout_seconds: int = None,
    ) -> dict:
        """
        Execute code with test input and compare output.
        
        Args:
            code: Python code to execute
            test_input: Input to pass to the code
            expected_output: Expected output
            timeout_seconds: Maximum execution time
            
        Returns:
            Dict with passed, actual_output, error, etc.
        """
        timeout = timeout_seconds or self.default_timeout
        
        # Create test wrapper code
        test_code = self._create_test_wrapper(code, test_input)
        
        # Execute
        result = await self.execute(test_code, timeout)
        
        if not result["success"]:
            return {
                "passed": False,
                "actual_output": None,
                "error": result.get("error"),
                "execution_time_ms": result.get("execution_time_ms", 0),
            }
        
        # Compare outputs
        actual_output = (result.get("output") or "").strip()
        expected = expected_output.strip()
        
        passed = self._compare_outputs(actual_output, expected)
        
        return {
            "passed": passed,
            "actual_output": actual_output,
            "error": None if passed else f"Expected: {expected}, Got: {actual_output}",
            "execution_time_ms": result.get("execution_time_ms", 0),
        }
    
    def _wrap_code(self, code: str, memory_mb: int) -> str:
        """Wrap code with resource limits and safety measures."""
        # Memory limit in bytes
        memory_bytes = memory_mb * 1024 * 1024
        
        wrapper = f'''
import sys
import resource

# Set memory limit
try:
    resource.setrlimit(resource.RLIMIT_AS, ({memory_bytes}, {memory_bytes}))
except Exception:
    pass  # May not work on all systems

# Disable dangerous builtins
import builtins
_original_import = builtins.__import__

ALLOWED_MODULES = {repr(self.allowed_imports)}

def _safe_import(name, *args, **kwargs):
    # Allow submodules of allowed modules
    base_module = name.split('.')[0]
    if base_module not in ALLOWED_MODULES:
        raise ImportError(f"Import of '{{name}}' is not allowed in sandbox")
    return _original_import(name, *args, **kwargs)

builtins.__import__ = _safe_import

# Remove dangerous builtins
for name in ['open', 'exec', 'eval', 'compile', '__import__']:
    if hasattr(builtins, name) and name != '__import__':
        try:
            delattr(builtins, name)
        except Exception:
            pass

# Capture stdout
from io import StringIO
_stdout = StringIO()
sys.stdout = _stdout

try:
    # User code starts here
{self._indent_code(code, 4)}
    # User code ends here
except Exception as e:
    print(f"Error: {{type(e).__name__}}: {{e}}", file=sys.stderr)
    sys.exit(1)
finally:
    # Output captured stdout
    sys.stdout = sys.__stdout__
    print(_stdout.getvalue(), end='')
'''
        return wrapper
    
    def _create_test_wrapper(self, code: str, test_input: str) -> str:
        """Create wrapper for test execution."""
        # Parse test input to determine how to call the function
        wrapper = f'''
{code}

# Test execution
try:
    # Try to find and call the main function
    if 'solution' in dir():
        result = solution({test_input})
        if result is not None:
            print(result)
    elif 'main' in dir():
        result = main({test_input})
        if result is not None:
            print(result)
    else:
        # Look for any function that might be the solution
        import inspect
        funcs = [name for name, obj in locals().items() 
                 if callable(obj) and not name.startswith('_')]
        if funcs:
            func = locals()[funcs[0]]
            result = func({test_input})
            if result is not None:
                print(result)
except Exception as e:
    print(f"Error: {{e}}")
'''
        return wrapper
    
    def _indent_code(self, code: str, spaces: int) -> str:
        """Indent code by specified number of spaces."""
        indent = ' ' * spaces
        lines = code.split('\n')
        return '\n'.join(indent + line for line in lines)
    
    def _compare_outputs(self, actual: str, expected: str) -> bool:
        """Compare actual and expected outputs flexibly."""
        # Normalize whitespace
        actual_norm = ' '.join(actual.split())
        expected_norm = ' '.join(expected.split())
        
        # Direct comparison
        if actual_norm == expected_norm:
            return True
        
        # Try numeric comparison
        try:
            if float(actual_norm) == float(expected_norm):
                return True
        except (ValueError, TypeError):
            pass
        
        # Case-insensitive for strings
        if actual_norm.lower() == expected_norm.lower():
            return True
        
        # Check if actual contains expected (for print statements)
        if expected_norm in actual_norm:
            return True
        
        return False
    
    async def _run_subprocess(self, script_path: str, timeout: int) -> dict:
        """Run Python script in subprocess."""
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                sys.executable, script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                # Limit resources
                preexec_fn=self._set_process_limits if os.name != 'nt' else None,
            )
            
            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )
            
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='replace').strip(),
                "stderr": stderr.decode('utf-8', errors='replace').strip(),
            }
            
        except asyncio.TimeoutError:
            # Kill the process
            try:
                process.kill()
                await process.wait()
            except Exception:
                pass
            raise
    
    def _set_process_limits(self):
        """Set resource limits for subprocess (Unix only)."""
        try:
            # Set CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
            
            # Set memory limit (50MB)
            memory_bytes = self.default_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
            
            # Disable core dumps
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            
            # Limit number of processes
            resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
            
            # Limit file size
            resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
            
        except Exception:
            pass  # Resource limits may not be available on all systems
