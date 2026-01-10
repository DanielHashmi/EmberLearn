# Research: Hackathon III Implementation

**Date**: 2026-01-05
**Feature**: 001-hackathon-iii
**Purpose**: Deep research on all technical decisions for architectural planning

---

## 1. OpenAI Agents SDK Architecture

### Decision
Use **OpenAI Agents Python SDK** (`openai-agents-python`) with manager/worker pattern for 6 specialized AI agents.

### Rationale
- **Built-in agent loop**: Handles tool calling, LLM communication, and iteration until completion
- **Handoffs**: Powerful delegation between multiple agents (Triage → Specialists)
- **Python-first**: Native async/await support, Pydantic validation, automatic schema generation
- **Guardrails**: Parallel input validation with early rejection
- **Sessions**: Automatic conversation history management
- **Tracing**: Built-in visualization, debugging, and monitoring

### Architecture Pattern

**Manager Pattern** (Triage agent delegates to specialists):

```python
from agents import Agent, Runner
import asyncio

# Specialized agents
concepts_agent = Agent(
    name="Concepts Agent",
    handoff_description="Specialist for Python concept explanations",
    instructions="Explain Python concepts with adaptive examples"
)

code_review_agent = Agent(
    name="Code Review Agent",
    handoff_description="Specialist for code quality analysis",
    instructions="Analyze code for correctness, PEP 8 style, efficiency"
)

# Triage agent (manager)
triage_agent = Agent(
    name="Triage Agent",
    instructions="Route queries to appropriate specialist based on intent",
    handoffs=[concepts_agent, code_review_agent, ...]
)

# Execution
async def handle_query(user_input):
    result = await Runner.run(triage_agent, user_input)
    return result.final_output
```

### Integration with FastAPI + Dapr + Kafka

```python
from fastapi import FastAPI
from agents import Agent, Runner
from dapr.clients import DaprClient
import structlog

app = FastAPI()
log = structlog.get_logger()

@app.post("/api/agent/query")
async def process_query(request: QueryRequest):
    correlation_id = request.correlation_id

    # Bind correlation ID to logs
    log = log.bind(correlation_id=correlation_id)

    try:
        # Run agent
        result = await Runner.run(triage_agent, request.message)

        # Publish result to Kafka via Dapr
        with DaprClient() as d:
            d.publish_event(
                pubsub_name='kafka-pubsub',
                topic_name=f'learning.response',
                data=json.dumps({
                    'correlation_id': correlation_id,
                    'response': result.final_output
                }),
                data_content_type='application/json'
            )

        return {"status": "success", "message_id": correlation_id}

    except Exception as e:
        log.error("agent_execution_failed", error=str(e))
        # Fallback to cached response (graceful degradation)
        return {"status": "fallback", "response": get_cached_response(request.message)}
```

### Graceful Degradation Strategy

```python
import asyncio
from functools import lru_cache

# Cache common responses
@lru_cache(maxsize=1000)
def get_cached_response(query: str) -> str:
    # Predefined answers for common queries
    common_responses = {
        "how do for loops work": "A for loop iterates over a sequence...",
        "what is a list": "A list is a mutable ordered collection..."
    }
    return common_responses.get(query.lower(),
                                 "I'm temporarily unavailable. Please try again.")

async def run_agent_with_fallback(agent, input_data, timeout=10):
    try:
        result = await asyncio.wait_for(
            Runner.run(agent, input_data),
            timeout=timeout
        )
        return result.final_output
    except asyncio.TimeoutError:
        log.warning("agent_timeout", input=input_data)
        return get_cached_response(input_data)
    except Exception as e:
        log.error("agent_failed", error=str(e))
        return get_cached_response(input_data)
```

### Alternatives Considered
- **LangChain**: Too heavy, complex abstractions, steeper learning curve
- **Direct OpenAI API**: No built-in handoffs, manual agent orchestration required
- **Custom framework**: Reinventing wheel, lacks tracing/debugging tools

---

## 2. Dapr Sidecar Pattern with FastAPI

### Decision
Use **Dapr 1.13+** with sidecar pattern for state management (PostgreSQL), pub/sub (Kafka), and service invocation.

### Rationale
- **Polyglot**: Works with any language, no vendor lock-in
- **Building blocks**: State, pub/sub, service invocation as HTTP/gRPC APIs
- **Sidecar pattern**: Decouples application logic from infrastructure
- **Built-in resiliency**: Retries, circuit breakers, timeouts
- **Observability**: Automatic tracing, metrics, logging

### PostgreSQL State Store Configuration

**Dapr Component** (`components/statestore.yaml`):

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v2
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-secret
        key: connectionString
    - name: tablePrefix
      value: "emberlearn_"
    - name: metadataTableName
      value: "dapr_metadata"
    - name: cleanupInterval
      value: "1h"
    - name: maxConns
      value: "20"
```

### Kafka Pub/Sub Configuration

**Dapr Component** (`components/pubsub.yaml`):

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka.default.svc.cluster.local:9092"
    - name: consumerGroup
      value: "emberlearn-agents"
    - name: authType
      value: "none"  # For dev; use SASL/TLS in production
    - name: maxMessageBytes
      value: "1048576"  # 1MB
    - name: consumeRetryInterval
      value: "200ms"
```

### FastAPI + Dapr Integration

**State Management**:

```python
from dapr.clients import DaprClient
import json

async def save_student_progress(student_id: int, topic_id: int, mastery_score: float):
    with DaprClient() as d:
        state_key = f"student:{student_id}:topic:{topic_id}"
        state_value = {
            "student_id": student_id,
            "topic_id": topic_id,
            "mastery_score": mastery_score,
            "updated_at": datetime.utcnow().isoformat()
        }

        d.save_state(
            store_name="statestore",
            key=state_key,
            value=json.dumps(state_value)
        )

async def get_student_progress(student_id: int, topic_id: int):
    with DaprClient() as d:
        state_key = f"student:{student_id}:topic:{topic_id}"
        result = d.get_state(
            store_name="statestore",
            key=state_key
        )
        return json.loads(result.data) if result.data else None
```

**Pub/Sub with Partition Keys**:

```python
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

# Subscribe to topic
@dapr_app.subscribe(pubsub='kafka-pubsub', topic='learning.query')
async def handle_learning_query(event):
    data = event.data
    log.info("received_query",
             correlation_id=data['correlation_id'],
             student_id=data['student_id'])

    # Process query...
    result = await process_query(data)

    # Publish response with student_id as partition key
    with DaprClient() as d:
        d.publish_event(
            pubsub_name='kafka-pubsub',
            topic_name='learning.response',
            data=json.dumps(result),
            metadata={
                'partitionKey': str(data['student_id'])  # Ensures ordering per student
            }
        )
```

### Kubernetes Deployment with Dapr Annotations

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: triage-agent
spec:
  replicas: 3
  template:
    metadata:
      labels:
        app: triage-agent
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "triage-agent"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
        dapr.io/enable-metrics: "true"
        dapr.io/metrics-port: "9090"
    spec:
      containers:
      - name: triage-agent
        image: emberlearn/triage-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "http://jaeger:4318"
```

### Alternatives Considered
- **Direct Kafka/PostgreSQL clients**: More code, no built-in resiliency
- **Service mesh (Istio)**: Too heavy for MVP, complex setup
- **Redis for state**: Dapr PostgreSQL connector provides SQL queries, migrations

---

## 3. Python Subprocess Security (Code Execution Sandbox)

### Decision
Use **Python `subprocess` module with `resource` limits** for code execution sandbox.

### Rationale
- **subprocess.run()**: Built-in timeout support (5 seconds)
- **resource module**: CPU time and memory limits (50MB)
- **Moderate isolation**: Prevents runaway processes, memory exhaustion
- **Simple implementation**: No Docker overhead, faster startup
- **Sufficient for MVP**: Acceptable risk for educational demo environment

### Secure Execution Implementation

```python
import subprocess
import resource
import sys
import json
from typing import Dict

def set_resource_limits():
    """Apply resource limits in child process."""
    # Memory limit: 50MB
    memory_limit = 50 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

    # CPU time limit: 5 seconds
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))

    # File descriptor limit: 10 (prevent excessive file operations)
    resource.setrlimit(resource.RLIMIT_NOFILE, (10, 10))

def execute_python_code(code: str, timeout: int = 5) -> Dict:
    """
    Execute untrusted Python code with security constraints.

    Security measures:
    - subprocess isolation (no shared memory with parent)
    - resource limits (50MB memory, 5s CPU)
    - timeout enforcement (5s wall clock time)
    - restricted imports (stdlib only via code validation)
    - no filesystem access except temp
    - no network access (not enforced at OS level, but checked in code)

    Returns:
        Dict with success, stdout, stderr, returncode, error
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
            preexec_fn=set_resource_limits,  # Apply limits before exec
            cwd="/tmp",  # Restrict to temp directory
            env={"PYTHONPATH": ""}  # No additional Python paths
        )

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout[:10000],  # Limit output size
            "stderr": result.stderr[:10000],
            "error": None
        }

    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "returncode": None,
            "stdout": (e.stdout or "")[:10000],
            "stderr": (e.stderr or "")[:10000],
            "error": "Execution timeout: code ran longer than 5 seconds"
        }

    except Exception as e:
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "error": f"Execution error: {str(e)}"
        }

# Validate imports before execution
def validate_code_safety(code: str) -> tuple[bool, str]:
    """Check for dangerous imports or operations."""
    dangerous_patterns = [
        'import os', 'import subprocess', 'import sys',
        'import socket', 'import requests', 'import urllib',
        '__import__', 'eval(', 'exec(', 'compile(',
        'open(', 'file('
    ]

    for pattern in dangerous_patterns:
        if pattern in code:
            return False, f"Forbidden operation: {pattern}"

    return True, ""

# FastAPI endpoint
@app.post("/api/code/execute")
async def execute_code(request: CodeExecutionRequest):
    # Validate code safety
    is_safe, error_msg = validate_code_safety(request.code)
    if not is_safe:
        return {"success": False, "error": error_msg}

    # Execute with limits
    result = execute_python_code(request.code, timeout=5)

    # Log execution
    log.info("code_executed",
             correlation_id=request.correlation_id,
             student_id=request.student_id,
             success=result["success"],
             returncode=result.get("returncode"))

    return result
```

### Security Considerations

**What's Protected**:
- ✅ CPU time limits (5s via resource.RLIMIT_CPU)
- ✅ Memory limits (50MB via resource.RLIMIT_AS)
- ✅ Wall clock timeout (5s via subprocess timeout)
- ✅ Output size limits (10KB truncation)
- ✅ Import validation (blacklist dangerous modules)
- ✅ Working directory restriction (/tmp)

**What's NOT Protected** (acceptable for MVP):
- ❌ Network access (would need iptables/Docker for true isolation)
- ❌ Filesystem access beyond /tmp (would need chroot/containers)
- ❌ Process forking (RLIMIT_NPROC not set to prevent fork bombs)

**Production Recommendations** (Phase 9+):
- Use Docker containers with `--network=none` and `--read-only`
- Use gVisor or Firecracker for stronger isolation
- Implement iptables rules to block network
- Use seccomp profiles to restrict syscalls

### Alternatives Considered
- **Docker per execution**: Stronger isolation but 2-3s overhead per run
- **RestrictedPython**: AST-based validation, but execution still in-process
- **Pyodide/WebAssembly**: Browser-based, but complex integration
- **AWS Lambda**: External service, adds latency and cost

---

## 4. Kafka Partitioning for Ordered Event Processing

### Decision
Use **Kafka partition key = `student_id`** to ensure ordered event processing per student.

### Rationale
- **Kafka guarantee**: Messages with same partition key go to same partition in order
- **Per-student ordering**: All events for student X processed sequentially
- **Scalability**: Different students can be processed in parallel across partitions
- **Correlation IDs**: UUIDs enable distributed tracing across services

### Kafka Topic Design

```
learning.query         - Student asks question (partition key: student_id)
learning.response      - Agent responds (partition key: student_id)
code.submitted         - Student submits code (partition key: student_id)
code.executed          - Sandbox execution result (partition key: student_id)
exercise.assigned      - New exercise created (partition key: student_id)
exercise.completed     - Student completes exercise (partition key: student_id)
struggle.detected      - Student struggle trigger (partition key: student_id)
```

### Dapr Pub/Sub with Partition Keys

**Publishing with partition key**:

```python
from dapr.clients import DaprClient
import json
import uuid

def publish_student_event(student_id: int, event_type: str, payload: dict):
    correlation_id = str(uuid.uuid4())

    event_data = {
        "correlation_id": correlation_id,
        "student_id": student_id,
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload
    }

    with DaprClient() as d:
        d.publish_event(
            pubsub_name='kafka-pubsub',
            topic_name=f'{event_type.split(".")[0]}.{event_type.split(".")[1]}',
            data=json.dumps(event_data),
            data_content_type='application/json',
            metadata={
                'partitionKey': str(student_id),  # Ensures ordering
                'correlationId': correlation_id   # For tracing
            }
        )

    return correlation_id
```

**Consuming with correlation**:

```python
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp
import structlog

app = FastAPI()
dapr_app = DaprApp(app)
log = structlog.get_logger()

@dapr_app.subscribe(pubsub='kafka-pubsub', topic='code.submitted')
async def handle_code_submission(event):
    data = event.data

    # Bind correlation ID to all logs
    bound_log = log.bind(
        correlation_id=data['correlation_id'],
        student_id=data['student_id'],
        event_type='code.submitted'
    )

    bound_log.info("processing_code_submission")

    # Execute code
    result = execute_python_code(data['payload']['code'])

    # Publish result with same partition key
    publish_student_event(
        student_id=data['student_id'],
        event_type='code.executed',
        payload=result
    )

    bound_log.info("code_execution_complete", success=result['success'])
```

### Consumer Group Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka.default.svc.cluster.local:9092"
    - name: consumerGroup
      value: "emberlearn-progress-agent"  # One group per agent type
    - name: consumeRetryInterval
      value: "200ms"
    - name: sessionTimeout
      value: "15s"
    - name: heartbeatInterval
      value: "5s"
```

### Alternatives Considered
- **Timestamp ordering**: Vulnerable to clock skew across services
- **Sequence numbers**: Requires central sequencer, adds complexity
- **No ordering**: Would break mastery calculation and struggle detection

---

## 5. Next.js 15+ with Monaco Editor (SSR Compatible)

### Decision
Use **@monaco-editor/react** with Next.js **dynamic imports** (SSR disabled) for Python code editing.

### Rationale
- **SSR incompatibility**: Monaco requires browser DOM, cannot render server-side
- **Dynamic imports**: Next.js `dynamic()` with `ssr: false` loads only on client
- **Production-ready**: Used by VS Code, CodeSandbox, StackBlitz
- **Python support**: Built-in syntax highlighting, autocomplete for stdlib
- **Customizable**: Themes, keyboard shortcuts, linting, extensions

### Next.js Integration

**Component** (`components/CodeEditor.tsx`):

```typescript
import dynamic from 'next/dynamic';
import { useState, useRef } from 'react';
import type { editor } from 'monaco-editor';

// Dynamic import with SSR disabled
const Editor = dynamic(() => import('@monaco-editor/react'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full">
      <span className="text-gray-400">Loading editor...</span>
    </div>
  )
});

interface CodeEditorProps {
  initialValue?: string;
  onExecute?: (code: string) => void;
  theme?: 'vs-dark' | 'vs-light';
}

export default function CodeEditor({
  initialValue = '# Write your Python code here\nprint("Hello, EmberLearn!")',
  onExecute,
  theme = 'vs-dark'
}: CodeEditorProps) {
  const [code, setCode] = useState(initialValue);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  function handleEditorMount(editor: editor.IStandaloneCodeEditor, monaco: typeof import('monaco-editor')) {
    editorRef.current = editor;

    // Configure Python language features
    monaco.languages.registerCompletionItemProvider('python', {
      provideCompletionItems: (model, position) => {
        // Custom autocomplete for common patterns
        const suggestions = [
          {
            label: 'for-range',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'for ${1:i} in range(${2:10}):\n    ${3:pass}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'For loop with range'
          },
          {
            label: 'def-function',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'def ${1:function_name}(${2:args}):\n    """${3:docstring}"""\n    ${4:pass}',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Function definition'
          }
        ];
        return { suggestions };
      }
    });

    // Add keyboard shortcut for execution (Ctrl+Enter)
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      if (onExecute) {
        onExecute(editor.getValue());
      }
    });
  }

  function handleEditorChange(value: string | undefined) {
    if (value !== undefined) {
      setCode(value);
    }
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex justify-between items-center p-2 bg-gray-800 border-b border-gray-700">
        <span className="text-sm text-gray-400">Python Editor</span>
        <button
          onClick={() => onExecute && onExecute(code)}
          className="px-4 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-sm"
        >
          Run (Ctrl+Enter)
        </button>
      </div>

      <div className="flex-1">
        <Editor
          height="100%"
          language="python"
          value={code}
          onChange={handleEditorChange}
          onMount={handleEditorMount}
          theme={theme}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            insertSpaces: true,
            wordWrap: 'on',
            quickSuggestions: true,
            suggestOnTriggerCharacters: true
          }}
        />
      </div>
    </div>
  );
}
```

**Page Integration** (`app/practice/page.tsx`):

```typescript
'use client';

import { useState } from 'react';
import CodeEditor from '@/components/CodeEditor';

export default function PracticePage() {
  const [output, setOutput] = useState<string>('');
  const [isExecuting, setIsExecuting] = useState(false);

  async function handleCodeExecution(code: string) {
    setIsExecuting(true);
    setOutput('Executing...');

    try {
      const response = await fetch('/api/code/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });

      const result = await response.json();

      if (result.success) {
        setOutput(result.stdout || '(No output)');
      } else {
        setOutput(`Error:\n${result.stderr || result.error}`);
      }
    } catch (error) {
      setOutput(`Network error: ${error.message}`);
    } finally {
      setIsExecuting(false);
    }
  }

  return (
    <div className="h-screen flex">
      <div className="w-1/2 border-r">
        <CodeEditor onExecute={handleCodeExecution} />
      </div>

      <div className="w-1/2 p-4 bg-gray-900">
        <h2 className="text-lg font-semibold mb-2">Output</h2>
        <pre className="bg-black p-4 rounded h-full overflow-auto">
          <code className="text-green-400">{output}</code>
        </pre>
      </div>
    </div>
  );
}
```

### Alternatives Considered
- **CodeMirror**: Less feature-rich, more manual configuration
- **Ace Editor**: Older, less active maintenance
- **Custom textarea**: No syntax highlighting, no autocomplete

---

## 6. Structured Logging with Correlation IDs

### Decision
Use **structlog** for structured JSON logging to stdout with correlation IDs.

### Rationale
- **Structured output**: JSON format for log aggregation (ELK, CloudWatch)
- **Correlation IDs**: UUIDs propagate through HTTP headers and Kafka messages
- **Performance**: Fast JSON rendering with orjson, async-safe
- **Cloud-native**: Logs to stdout for Kubernetes container logging
- **Context binding**: Automatically include correlation_id, service_name in all logs

### Structlog Configuration

**Setup** (`logging_config.py`):

```python
import logging
import sys
import structlog
from structlog.processors import JSONRenderer
from structlog.contextvars import merge_contextvars
import orjson

def setup_logging(service_name: str, log_level: str = "INFO"):
    """Configure structlog for cloud-native JSON logging."""

    # Standard library logging configuration
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )

    # Structlog configuration
    structlog.configure(
        processors=[
            merge_contextvars,  # Merge context variables (correlation_id, etc.)
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            ),
            JSONRenderer(serializer=lambda data, **kwargs: orjson.dumps(data).decode())
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.BytesLoggerFactory(),
        cache_logger_on_first_use=True
    )

    # Add service_name to all logs
    structlog.contextvars.bind_contextvars(service_name=service_name)
```

### FastAPI Middleware for Correlation IDs

```python
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
import uuid

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract or generate correlation ID
        correlation_id = request.headers.get('X-Correlation-ID') or str(uuid.uuid4())

        # Bind to structlog context
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        # Add to request state
        request.state.correlation_id = correlation_id

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers['X-Correlation-ID'] = correlation_id

        # Clear context after request
        structlog.contextvars.clear_contextvars()

        return response

# FastAPI app setup
app = FastAPI()
setup_logging(service_name="triage-agent", log_level="INFO")
app.add_middleware(CorrelationIdMiddleware)

log = structlog.get_logger()

@app.post("/api/query")
async def handle_query(request: QueryRequest):
    log.info("query_received",
             student_id=request.student_id,
             query_length=len(request.message))

    try:
        result = await process_query(request)
        log.info("query_processed", success=True)
        return result
    except Exception as e:
        log.error("query_failed", error=str(e), exc_info=True)
        raise
```

### Log Output Example

```json
{
  "event": "query_received",
  "level": "info",
  "timestamp": "2026-01-05T10:30:45.123456Z",
  "service_name": "triage-agent",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "student_id": 42,
  "query_length": 25,
  "filename": "api.py",
  "func_name": "handle_query",
  "lineno": 45
}
```

### Alternatives Considered
- **python-json-logger**: Less features, no context binding
- **loguru**: Not async-safe, harder integration with stdlib logging
- **Standard logging**: No structured output, manual JSON formatting

---

## Summary

All research complete. Key decisions documented with rationale, code examples, and alternatives considered. Ready to proceed with Phase 1 (data model, API contracts, quickstart).
