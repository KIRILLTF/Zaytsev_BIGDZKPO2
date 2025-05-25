# storing_service/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 1) копируем и устанавливаем зависимости
COPY storing_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) копируем общий пакет shared из корня проекта
COPY shared ./shared

# 3) копируем код самого сервиса
COPY storing_service ./

# выставляем порт
EXPOSE 8081

# запускаем приложение из папки /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
