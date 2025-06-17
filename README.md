
[![Ruff](https://github.com/BerdyshevEugene/voice2text_transcriber/actions/workflows/ruff.yml/badge.svg)](https://github.com/BerdyshevEugene/voice2text_transcriber/actions/workflows/ruff.yml)

# Voice2text_transcriber

Программа на fastapi, для расшифровки аудиозаписи в текст

## Структура проекта:

<details>

```python

voice2text_transcriber
│
├── src
│   ├── handlers - обработчики
│   │   ├── audio_processing.py - работает с аудио и отправляет результат в обработчик
│   │   ├── audio_vosk.py - улучшение кач-ва аудио, форматирует аудио в текст
│   │   ├── message_handler.py - обработка данных из RabbitMQ
│   │   ├── socket_communication.py - отправка данных в сокет datagate
│   │   ├── utils.py - функция скачивает .wav файл по ссылке (удалить позднее) 
│   │   │
│   │   ├── queries.py - здесь содержатся запросы для обработки данных и вставку в БД
│   │   └── routes_handler.py - содержит роуты по котороым обрабатываются данные
│   │
│   ├── logger
│   ├── logs
│   │
│   ├── rabbitmq
│   │   ├── connection.py - подключение и регистрация обработчика сообщений
│   │   └── publisher.py - отправка преобразованных аудио в текст в очередь
│   │
│   └── main.py - запуск программы
│
└── README.md
```

</details>

---

## Установка и использование UV

<details>
<summary>📦 Способы установки UV</summary>

### 1. Установка через автономные установщики (рекомендуется)

**Для macOS и Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Для Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Установка через PyPI (альтернативный способ)
```bash
pip install uv
```

### Обновление UV
После установки вы можете обновить UV до последней версии:
```bash
uv self update
```

🔗 Подробнее об установке: [Официальная документация](https://docs.astral.sh/uv/getting-started/installation/)
</details>

---

<summary>🚀 Основные команды UV</summary>

<details>

### Управление Python-окружением

**Установка конкретной версии Python:**
```bash
uv python install 3.13  # Установит Python 3.13
```

### Управление зависимостями

**Синхронизация зависимостей проекта:**
```bash
uv sync  # Аналог pip install + pip-compile
```

**Запуск команд в окружении проекта:**
```bash
uv run <COMMAND>  # Например: uv run pytest
```

**Запуск Django-сервера:**
```bash
uv run manage.py runserver  # Альтернатива python manage.py runserver
```
</details>

---


<summary>🔍 Интеграция с Ruff</summary>

<details>

[Ruff](https://github.com/astral-sh/ruff) - это молниеносный линтер для Python, также разработанный Astral.

**Установка Ruff через UV:**
```bash
uvx ruff  # Установит последнюю версию Ruff
```

**Проверка кода с помощью Ruff:**
```bash
uvx ruff check .  # Проверит все файлы в текущей директории
```
</details>

---

## Инструкция по запуску проекта

<details>

### Установка и запуск окружения:
```bash
uv venv -p 3.11 .venv  # создаём виртуальное окружение на python 3.11
uv pip install -r requirements.txt  # ставим зависимости
```

### Запуск программы:
```bash
cd src
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

программа автоматически подключается к очереди RabbitMQ и получает данные для расшифровки в виде словаря

## Запуск проекта в Docker

### Сборка
1. Авторизация в Docker Hub 
```
docker login
``` 
2. Сборка Docker-образа 
```
docker build -t gsssupport/myvoice2text_transcriberapp:latest .
```
3. Публикация образа в Docker Hub
```
docker push gsssupport/myvoice2text_transcriberapp:latest
```

### Запуск
1. Авторизация в Docker Hub 
```
docker login
``` 
2. Запуск Docker-контейнера
```
docker-compose up
```

</details>

---

## Остальная информация

<details>

```
CompanyName: GMG
FileDescription: voice2text
InternalName: V2T
ProductName: voice2text
Author: Berdyshev E.A.
Development and support: Berdyshev E.A.
LegalCopyright: © GMG. All rights reserved.
```

</details>
