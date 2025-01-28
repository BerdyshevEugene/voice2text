# Используем официальный базовый образ Python
FROM python:3.11.11-slim-bookworm

# Устанавливаем переменные окружения
# This flag is important to output python logs correctly in docker!
# Flag to optimize container size a bit by removing runtime python cache
#ENV PYTHONUNBUFFERED=1 \
#    PYTHONDONTWRITEBYTECODE=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости системы и Python
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
	portaudio19-dev \
    ffmpeg \
    && python3 -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install -r requirements.txt \
    && apt-get remove -y \
    gcc \
    libpq-dev \
	portaudio19-dev \
    && apt-get autoremove -y \
	&& apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Копируем исходный код приложения
COPY src /app/src

COPY vosk /app/vosk

WORKDIR /app/src

# Указываем команду для запуска приложения
CMD ["/bin/bash", "-c", "source /venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000"]
