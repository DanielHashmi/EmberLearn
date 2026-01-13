FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY ../shared /app/shared

# Copy sandbox code
COPY main.py .
COPY executor.py .
COPY validator.py .

# Create non-root user for security
RUN useradd -m -u 1000 sandbox
USER sandbox

# Expose port
EXPOSE 8007

# Run with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8007"]
