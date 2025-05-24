# Базовый образ
FROM python:3.9-slim

WORKDIR /app

# Копируем и устанавливаем зависимости именно из папки analysis_service
COPY analysis_service/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем общие модули
COPY shared/ shared/

# Копируем код анализ-сервиса
COPY analysis_service/ .

EXPOSE 8082

# Запуск FastAPI через Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082"]
