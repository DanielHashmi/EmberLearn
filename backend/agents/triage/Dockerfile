FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir .

# Copy shared module
COPY backend/shared/ ./shared/

# Copy agents module
COPY backend/agents/ ./agents/

# Set working directory
WORKDIR /app

# Run the service
CMD ["uvicorn", "agents.triage.app:app", "--host", "0.0.0.0", "--port", "8000"]
