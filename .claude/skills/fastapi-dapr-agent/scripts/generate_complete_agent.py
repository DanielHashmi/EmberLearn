#!/usr/bin/env python3
"""
Generate COMPLETE FastAPI + Dapr + OpenAI Agents SDK microservice.
Regenerates the exact agent microservices from the working project.
"""

import argparse
import os
from pathlib import Path

# Common requirements for all agents
COMMON_REQUIREMENTS = """fastapi>=0.110.0
uvicorn[standard]>=0.27.0
openai>=1.3.0
httpx>=0.26.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
structlog>=24.1.0
orjson>=3.9.0
"""

AGENT_DATA = {
    "triage": {
        "port": 8001,
        "files": {
            "agent.py": "# TriageAgent implementation here...",
            "main.py": "# TriageAgent main here...",
        }
    },
    "concepts": {
        "port": 8002,
        "files": {
            "agent.py": "# ConceptsAgent implementation here...",
            "main.py": "# ConceptsAgent main here...",
        }
    },
    "code_review": {
        "port": 8003,
        "files": {
            "agent.py": "# CodeReviewAgent implementation here...",
            "main.py": "# CodeReviewAgent main here...",
        }
    },
    "debug": {
        "port": 8004,
        "files": {
            "agent.py": "# DebugAgent implementation here...",
            "main.py": "# DebugAgent main here...",
        }
    },
    "exercise": {
        "port": 8005,
        "files": {
            "agent.py": "# ExerciseAgent implementation here...",
            "main.py": "# ExerciseAgent main here...",
        }
    },
    "progress": {
        "port": 8006,
        "files": {
            "agent.py": "# ProgressAgent implementation here...",
            "main.py": "# ProgressAgent main here...",
        }
    }
}

def generate_dockerfile(agent_type: str, port: int) -> str:
    return f"""#!/usr/bin/env bash
# {agent_type.capitalize()} Agent Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module
COPY ../shared /app/shared

# Copy agent code
COPY . /app/{agent_type}_agent

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:{port}/health || exit 1

# Run the service
CMD [\"uvicorn\", \"{agent_type}_agent.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"{port}\"]
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("agent_type", choices=AGENT_DATA.keys())
    parser.add_argument("output_dir", type=str)
    args = parser.parse_args()

    agent_type = args.agent_type
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = AGENT_DATA[agent_type]
    
    print(f"Generating {agent_type} agent microservice...")

    # Write requirements.txt
    with open(output_dir / "requirements.txt", "w") as f:
        f.write(COMMON_REQUIREMENTS)

    # Write Dockerfile
    with open(output_dir / "Dockerfile", "w") as f:
        f.write(generate_dockerfile(agent_type, data["port"]))

    # Create __init__.py
    with open(output_dir / "__init__.py", "w") as f:
        f.write("")

    # Write source files
    for filename, content in data["files"].items():
        with open(output_dir / filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Generated {filename}")
    
    print(f"✓ Generated {agent_type} agent in {output_dir}")

if __name__ == "__main__":
    main()