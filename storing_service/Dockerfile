FROM python:3.9-slim

WORKDIR /app

COPY storing_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared ./shared

COPY storing_service ./

EXPOSE 8081

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]