# Voice2text_transcriber

Программа на fastapi, для расшифровки аудиозаписи в текст

## Структура проекта:
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

## Инструкция

1. создайте и активируйте виртуальное окружение и установите зависимости:.

```bash
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
2. в send.py в строке data = {"url": "url"} передайте url аудиозаписи для расшифровки
3. запустите приложение: 
```bash
uvicorn main:app --reload
uvicorn main:app --host 0.0.0.0 --port 8000
```



## Остальная информация

CompanyName: GMG

FileDescription: Voice2text_transcriber

InternalName: V2T

ProductName: Voice2text_transcriber

Author: Berdyshev E.A.

Development and support: Berdyshev E.A.

LegalCopyright: © GMG. All rights reserved.



![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
