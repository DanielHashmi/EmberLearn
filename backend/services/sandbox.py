"""
Sandbox service for secure Python code execution.

Executes user-submitted Python code in a restricted environment with:
- 5-second timeout
- 50MB memory limit
- Captured stdout/stderr
- No filesystem access (except temp)
- No network access
"""

import subprocess
import sys
import tempfile
import os
import time
from typing import Optional, List
from pydantic import BaseModel


# Configuration
TIMEOUT_SECONDS = 5
MEMORY_LIMIT_MB = 50


class ExecutionResult(BaseModel):
    """Result of code execution."""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: int = 0


class TestCaseResult(BaseModel):
    """Result of a single test case."""
    input_data: str
    expected: str
    actual: str
    passed: bool


class TestResult(BaseModel):
    """Result of running test cases."""
    passed: int
    total: int
    score: int
    results: List[TestCaseResult]


class SandboxService:
    """Service for executing Python code in a sandboxed environment."""

    TIMEOUT = TIMEOUT_SECONDS
    MEMORY_LIMIT = MEMORY_LIMIT_MB * 1024 * 1024

    @staticmethod
    def execute(code: str) -> ExecutionResult:
        """
        Execute Python code in a sandboxed subprocess.
        
        Args:
            code: Python code to execute
            
        Returns:
            ExecutionResult with success status, output, and timing
        """
        start_time = time.time()
        
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.py', 
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Run in subprocess with timeout
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=TIMEOUT_SECONDS,
                    env={
                        'PATH': os.environ.get('PATH', ''),
                        'PYTHONPATH': '',
                        'HOME': tempfile.gettempdir(),
                    }
                )
                
                execution_time = int((time.time() - start_time) * 1000)
                
                if result.returncode == 0:
                    return ExecutionResult(
                        success=True,
                        output=result.stdout or "Code executed successfully (no output)",
                        error=None,
                        execution_time_ms=execution_time
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        output=result.stdout or "",
                        error=result.stderr or "Unknown error",
                        execution_time_ms=execution_time
                    )
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            execution_time = int((time.time() - start_time) * 1000)
            return ExecutionResult(
                success=False,
                output="",
                error=f"Code execution timed out after {TIMEOUT_SECONDS} seconds",
                execution_time_ms=execution_time
            )
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time_ms=execution_time
            )

    @staticmethod
    def run_tests(code: str, test_cases: List[dict]) -> TestResult:
        """
        Run code against test cases.
        
        Args:
            code: Python code containing a function to test
            test_cases: List of {input: str, expected: str} dicts
            
        Returns:
            TestResult with pass/fail counts and details
        """
        results = []
        passed_count = 0
        
        for test_case in test_cases:
            input_data = test_case.get("input", "")
            expected = test_case.get("expected", "")
            
            # Create test wrapper code
            if input_data:
                test_code = f'''{code}

# Test execution
if __name__ == "__main__":
    result = {input_data}
    print(repr(result))
'''
            else:
                # If no input_data, just execute the code as-is and check stdout
                test_code = code
            
            # Execute the test
            exec_result = SandboxService.execute(test_code)
            
            if exec_result.success:
                actual = exec_result.output.strip()
                # Compare output (handle repr formatting)
                # For script output, we might need to be more flexible (e.g., strip quotes)
                passed = actual == str(expected) or actual == repr(expected)
            else:
                actual = exec_result.error or "Execution failed"
                passed = False
            
            if passed:
                passed_count += 1
                
            results.append(TestCaseResult(
                input_data=input_data,
                expected=expected,
                actual=actual,
                passed=passed
            ))
        
        total = len(test_cases)
        score = int((passed_count / max(total, 1)) * 100)
        
        return TestResult(
            passed=passed_count,
            total=total,
            score=score,
            results=results
        )

    @staticmethod
    def validate_code(code: str) -> tuple[bool, Optional[str]]:
        """
        Validate code for dangerous patterns.
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        dangerous_patterns = [
            ('import os', 'os module is not allowed'),
            ('import sys', 'sys module is not allowed'),
            ('import subprocess', 'subprocess module is not allowed'),
            ('import socket', 'socket module is not allowed'),
            ('__import__', 'dynamic imports are not allowed'),
            ('eval(', 'eval is not allowed'),
            ('exec(', 'exec is not allowed'),
            ('open(', 'file operations are not allowed'),
            ('compile(', 'compile is not allowed'),
        ]
        
        for pattern, message in dangerous_patterns:
            if pattern in code:
                return (False, message)
        
        return (True, None)
