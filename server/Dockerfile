# Используем официальный Python образ
FROM python:3.10-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY ./server/requirements.txt . 

# Устанавливаем все зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем только серверные файлы
COPY server/ /app/


# Открываем порт для FastAPI
EXPOSE 8000

# Запускаем приложение через Uvicorn
# CMD ["uvicorn", "server.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

