# Используем официальный образ Python
FROM python:3.9-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения (из контекста ./gateway)
COPY . .

# Открываем порт приложения
EXPOSE 8000

# Запуск FastAPI через Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
