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
├── README.md
│
├── docker-compose.yml - для запуска приложения через docker compose
├── Dockerfile - сборка приложения в Docker
│
├── Jenkinsfile - файл конфигурации pipline Jenkins
├── ssh_key_docker_jenkins - SSH ключ для подключения к серверу с Docker (по умолчанию отсутвует)
│
├── ansible.cfg - настройки для Ansible
├── inventory.ini - список хостов для Ansible (по умолчанию отсутвует)
└── playbook.yml - сценарий для Ansible
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

## Инструкция Docker

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
docker compose up
```

## CI/CD

### Jenkins

В web-интерфейсе создать новый проект и указать репозиторий. В  Config File Management создать файлы:
1. inventory.ini (ID - voice2text_inventory)
2. .env	(ID - voice2text.env)

В Credentials добавить:
1. ftp_credentials - Логин и пароль от FTP
2. docker-hub-cred - Логин и пароль от Docker Hub
3. ssh-docker-server-key - SSH ключ от сервера с Docker
4. bot_token - Token от бота Telegram
5. chat_id - ID чата Telegram
6. message_thread_id - ID темы супергруппы Telegram

### Ansible

Для ручного запуска необходимо в корне репозитория положить ssh ключ ssh_key_docker_jenkins и выполнить команду
```
ansible-playbook playbook.yml --extra-vars "docker_user=ЛОГИН docker_password=ПАРОЛЬ"
```
## Остальная информация

CompanyName: GMG

FileDescription: Voice2text_transcriber

InternalName: V2T

ProductName: Voice2text_transcriber

Author: Berdyshev E.A.

CI/CD Author: Moldon E.D.

Development and support: Berdyshev E.A.

LegalCopyright: © GMG. All rights reserved.


![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=jenkins&logoColor=white)

![Ansible](https://img.shields.io/badge/Ansible-EE0000?style=for-the-badge&logo=ansible&logoColor=white)