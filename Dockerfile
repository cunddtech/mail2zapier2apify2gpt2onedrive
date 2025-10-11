FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start the production LangGraph orchestrator
CMD ["python3", "production_langgraph_orchestrator.py"]