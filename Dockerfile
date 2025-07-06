# Dockerfile

FROM python:3.11-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y gcc libpq-dev

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY . .

# Установка зависимостей Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Открываем порт
EXPOSE 5000

# Команда по умолчанию
CMD ["flask", "run", "--host=0.0.0.0"]
