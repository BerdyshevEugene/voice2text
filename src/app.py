import os
import json
import requests
import socket

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from loguru import logger
from pydantic import BaseModel
from tempfile import NamedTemporaryFile
from sklearn.cluster import KMeans

from handlers.audio_processing import process_audio
from logger.logger import setup_logger

setup_logger()
app = FastAPI()

load_dotenv()
LOCAL_HOST = os.getenv('HOST')
LOCAL_PORT = os.getenv('PORT')


class AudioRequest(BaseModel):
    MasterID: int
    url: str


def download_audio(url):
    response = requests.get(url)
    if response.status_code == 200:
        with NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    else:
        logger.error(
            f'failed to download audio from: {url} with status code: {response.status_code}')
        return None


def send_data_to_socket(data):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((LOCAL_HOST, int(LOCAL_PORT)))
        json_data = json.dumps(data, ensure_ascii=False)
        client_socket.sendall(json_data.encode('utf-8'))
        client_socket.close()
        logger.info(f'data sent to socket: {json_data}')
    except Exception as e:
        logger.error(f'error sending data to the socket: {e}')


def process_audio_background(master_id: int, url: str):
    try:
        file_path = download_audio(url)
        if not os.path.isfile(file_path):
            logger.error(f'file not found: {file_path}')
            return
        transcriptions = process_audio(file_path)
        text_content = "\n".join(transcriptions)
        send_data_to_socket({'Event': 'voice2text', 'MasterID': master_id, 'text': text_content})
    except Exception as e:
        logger.error(f'error processing audio: {e}')


@app.post('/process_audio/')
async def process_audio_endpoint(request: AudioRequest, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(process_audio_background, request.MasterID, request.url)
        logger.info('status: processing started')
        return {'status': 'processing started'}
    except Exception as e:
        logger.error(f'error in process_audio_endpoint: {e}')
        raise HTTPException(status_code=500, detail=f'internal server error: {str(e)}')
