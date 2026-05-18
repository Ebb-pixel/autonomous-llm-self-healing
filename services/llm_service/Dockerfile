FROM python:3.10-slim
WORKDIR /app
COPY requiements.txt .
RUN pip install -r requirements
COPY . .
CMD ["uvicorn", "services.llm_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
