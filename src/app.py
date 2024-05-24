import os
import json
import numpy as np
import requests
import sys
import wave

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tempfile import NamedTemporaryFile
from vosk import Model, KaldiRecognizer, SpkModel, SetLogLevel
from sklearn.cluster import KMeans


SetLogLevel(-1)

load_dotenv()

SPK_MODEL_PATH = os.getenv('SPK_MODEL_PATH')
VOSK_MODEL_PATH = os.getenv('VOSK_MODEL_PATH')

app = FastAPI()

class AudioRequest(BaseModel):
    url: str

def download_audio(url):
    response = requests.get(url)
    if response.status_code == 200:
        with NamedTemporaryFile(delete=True, suffix='.wav') as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    else:
        raise Exception(f'failed to download audio from: {url}')


@app.post('/process_audio/')
async def process_audio_endpoint(request=AudioRequest):
    file_path = download_audio(request.url)
    if not os.path.isfile(file_path):
        raise HTTPException(satus_code=400, detail=f'file not found: {file_path}')
    try:
        transcriptions = process_audio(file_path)
        return {'transcriptions': transcriptions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'internal server error: {str(e)}')


def extract_audio_features(file_path):
    with wave.open(file_path, 'rb') as wf:
        sample_rate = wf.getframerate()
        duration = wf.getnframes() / sample_rate
        audio = wf.readframes(wf.getnframes())
    
    audio = np.frombuffer(audio, dtype=np.int16)
    threshold = 1000
    is_silent = audio < threshold
    pauses = [i for i, silent in enumerate(is_silent) if silent]
    
    return duration, pauses


def diarization(answer, duration, pauses):
    transcriptions = []
    n_clusters = 2
    kmeans = None
    def last_spk_toggle(last):
        return 1 if last == 0 else 0
    X = [x['spk'] for x in answer if 'spk' in x]
    if len(X) >= n_clusters:
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(X)
    last_spk = 0
    for frase in answer:
        if 'spk' in frase and kmeans:
            last_spk = int(kmeans.predict([frase['spk']])[0])
        else:
            last_spk = last_spk_toggle(last_spk)
        try:
            transcriptions.append({'text': frase['text'], 'result': frase['result'], 'spk': last_spk})
        except:
            pass
    return transcriptions


def process_audio(file_path):
    transcriptions = []
    duration, pauses = extract_audio_features(file_path)
    
    wf = wave.open(file_path, 'rb')
    sample_rate = wf.getframerate()
    if sample_rate > 16000:
        sample_rate = 16000
    if sample_rate < 8000:
        sample_rate = 8000

    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != 'NONE':
        print('audio file must be WAV format mono PCM.')
        sys.exit(1)

    model = Model(VOSK_MODEL_PATH)
    spk_model = SpkModel(SPK_MODEL_PATH)
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetSpkModel(spk_model)
    rec.SetMaxAlternatives(0)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            if 'spk' in res:
                res['result'] = [{'start': 0}]
                transcriptions.append(res)

    res = json.loads(rec.FinalResult())
    if 'spk' in res:
        res['result'] = [{'start': 0}]
        transcriptions.append(res)

    wf.close()

    if len(transcriptions) > 0:
        transcriptions = diarization(transcriptions, duration, pauses)

    transcriptions.sort(key=lambda x: x['result'][0]['start'])
    return transcriptions
