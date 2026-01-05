"""
Code Executor - Runs Python code in isolated subprocess with resource limits.
"""

import subprocess
import resource
import tempfile
import os
import time
from dataclasses import dataclass
from typing import Optional

from .validator import validate_code


@dataclass
class ExecutionResult:
    output: str
    error: Optional[str]
    execution_time_ms: int
    memory_used_bytes: Optional[int]
    timed_out: bool
    validation_failed: bool
    validation_errors: list[str]


# Resource limits
MAX_TIMEOUT_SECONDS = 5
MAX_MEMORY_BYTES = 50 * 1024 * 1024  # 50MB
MAX_OUTPUT_SIZE = 10000  # characters


def set_resource_limits():
    """Set resource limits for the subprocess."""
    # CPU time limit
    resource.setrlimit(resource.RLIMIT_CPU, (MAX_TIMEOUT_SECONDS, MAX_TIMEOUT_SECONDS))

    # Memory limit
    resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY_BYTES, MAX_MEMORY_BYTES))

    # Disable core dumps
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    # Limit number of processes
    resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))

    # Limit file size
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))


def execute_code(code: str, timeout_ms: int = 5000) -> ExecutionResult:
    """
    Execute Python code in an isolated subprocess with resource limits.

    Args:
        code: Python source code to execute
        timeout_ms: Maximum execution time in milliseconds (max 5000)

    Returns:
        ExecutionResult with output, errors, and timing information
    """
    # Validate code first
    validation = validate_code(code)
    if not validation.is_safe:
        return ExecutionResult(
            output="",
            error="Code validation failed: " + "; ".join(validation.violations),
            execution_time_ms=0,
            memory_used_bytes=None,
            timed_out=False,
            validation_failed=True,
            validation_errors=validation.violations,
        )

    # Enforce maximum timeout
    timeout_seconds = min(timeout_ms / 1000, MAX_TIMEOUT_SECONDS)

    # Create temporary file for the code
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name

    try:
        start_time = time.perf_counter()

        # Execute in subprocess with restrictions
        process = subprocess.Popen(
            [
                "python3",
                "-u",  # Unbuffered output
                "-I",  # Isolated mode (no user site, ignore PYTHON* env vars)
                temp_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=set_resource_limits,
            env={
                "PATH": "/usr/bin:/bin",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            },
            cwd="/tmp",
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
            timed_out = False
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            timed_out = True

        end_time = time.perf_counter()
        execution_time_ms = int((end_time - start_time) * 1000)

        # Decode and truncate output
        output = stdout.decode("utf-8", errors="replace")[:MAX_OUTPUT_SIZE]
        error_output = stderr.decode("utf-8", errors="replace")[:MAX_OUTPUT_SIZE]

        # Determine error message
        error = None
        if timed_out:
            error = f"Execution timed out after {timeout_seconds}s"
        elif error_output:
            error = error_output
        elif process.returncode != 0:
            error = f"Process exited with code {process.returncode}"

        return ExecutionResult(
            output=output,
            error=error,
            execution_time_ms=execution_time_ms,
            memory_used_bytes=None,  # Would need /proc monitoring for accurate measurement
            timed_out=timed_out,
            validation_failed=False,
            validation_errors=[],
        )

    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except OSError:
            pass


if __name__ == "__main__":
    # Test execution
    test_code = """
print("Hello, EmberLearn!")
x = sum(range(100))
print(f"Sum: {x}")
"""
    result = execute_code(test_code)
    print(f"Output: {result.output}")
    print(f"Error: {result.error}")
    print(f"Time: {result.execution_time_ms}ms")
    print(f"Timed out: {result.timed_out}")
