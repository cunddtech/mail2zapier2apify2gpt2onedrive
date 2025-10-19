FROM python:3.11-slim

WORKDIR /usr/src/app

# Install only necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set memory-efficient environment variables
ENV PYTHONUNBUFFERED=1
ENV MALLOC_TRIM_THRESHOLD_=100000
ENV MALLOC_MMAP_THRESHOLD_=100000

# Limit workers and threads to reduce memory usage
# Railway has ~512MB-1GB RAM, we need to be conservative
CMD ["uvicorn", "production_langgraph_orchestrator:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--timeout-keep-alive", "30", "--limit-concurrency", "5"]