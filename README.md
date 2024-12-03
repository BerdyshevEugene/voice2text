# Voice2text_transcriber

Программа на fastapi, для расшифроки аудиозаписи в текст.

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
uvicorn app:app --reload
uvicorn app:app --host 0.0.0.0 --port 8000
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
