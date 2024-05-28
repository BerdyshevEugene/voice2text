import os
import json
import numpy as np
import requests
import sys
import socket

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tempfile import NamedTemporaryFile
from sklearn.cluster import KMeans

from handlers.audio_processing import process_audio

app = FastAPI()

load_dotenv()
DB_HOST = os.getenv('MW_DB_HOST')
DB_PORT = os.getenv('MW_DB_PORT')
LOCAL_HOST = os.getenv('HOST')
LOCAL_PORT = os.getenv('PORT')
DB_SERVER = os.getenv('MW_DB_SERVER')
DB_USER = os.getenv('MW_DB_USER')
DB_PASS = os.getenv('MW_DB_PASS')
DB_NAME = os.getenv('MW_DB_NAME')


class AudioRequest(BaseModel):
    url: str


def download_audio(url):
    response = requests.get(url)
    if response.status_code == 200:
        with NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    else:
        raise Exception(f'failed to download audio from: {url}')


def send_data_to_socket(data):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((LOCAL_HOST, int(LOCAL_PORT)))
        json_data = json.dumps(data)
        client_socket.sendall(json_data.encode('utf-8'))
        client_socket.close()
    except Exception as e:
        print('ошибка при отправке данных в сокет: ', e)



@app.post('/process_audio/')
async def process_audio_endpoint(request: AudioRequest):
    file_path = download_audio(request.url)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=400, detail=f'file not found: {file_path}')
    try:
        transcriptions = process_audio(file_path)
        send_data_to_socket(transcriptions)
        return {'transcriptions': transcriptions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'internal server error: {str(e)}')