# ---------------------------
# Zynex AI Platform - Dockerfile
# ---------------------------
FROM python:3.10-bullseye

WORKDIR /app

COPY . .

# Faster pip setup + retry + longer timeout
RUN pip install --upgrade pip
RUN pip install --default-timeout=120 --retries 10 --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
