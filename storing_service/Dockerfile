# Базовый образ
FROM python:3.9-slim

WORKDIR /app

# Копируем и устанавливаем зависимости именно из папки storing_service
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY . .

EXPOSE 8081

# Запуск FastAPI через Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
