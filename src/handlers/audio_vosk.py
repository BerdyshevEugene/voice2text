import os
import wave
import json
import numpy as np
import sys

from dotenv import load_dotenv
from loguru import logger
from vosk import Model, KaldiRecognizer, SpkModel, SetLogLevel
from sklearn.cluster import KMeans

SetLogLevel(-1)

load_dotenv()

SPK_MODEL_PATH = r'C:\Users\adm03\Desktop\work\programming\prjct_vosk\src\models\vosk-model-spk-0.4'
VOSK_MODEL_PATH = r'C:\Users\adm03\Desktop\work\programming\prjct_vosk\src\models\vosk-model-ru-0.42\vosk-model-ru-0.42'


def diarization(answer):
    transcriptions = []
    n_clusters = 2
    kmeans = None

    X = [x['spk'] for x in answer if 'spk' in x]
    X = np.array(X).reshape(-1, 1)  # преобразуем в двумерный массив
    if len(X) >= n_clusters:
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(X)

    first_spk = None
    last_spk = None

    for frase in answer:
        if 'spk' in frase and kmeans:
            spk = int(kmeans.predict(np.array(frase['spk']).reshape(1, -1))[0])
            if first_spk is None:
                first_spk = spk
            last_spk = spk
        else:
            last_spk = 1 if last_spk == 0 else 0

        try:
            transcriptions.append({'text': frase['text'], 'spk': last_spk})
        except Exception as e:
            logger.error(f'Error appending transcription: {e}')
            pass

    for item in transcriptions:
        if item['spk'] == first_spk:
            item['spk'] = 0
        else:
            item['spk'] = 1

    return transcriptions


def process_audio(file_path):
    transcriptions = []

    wf = wave.open(file_path, 'rb')
    sample_rate = wf.getframerate()
    if sample_rate > 16000:
        sample_rate = 16000
    elif sample_rate < 8000:
        sample_rate = 8000

    if wf.getsampwidth() != 2 or wf.getcomptype() != 'NONE':
        logger.info('audio file must be WAV format')
        sys.exit(1)

    model = Model(VOSK_MODEL_PATH)
    spk_model = SpkModel(SPK_MODEL_PATH)

    rec_left = KaldiRecognizer(model, sample_rate)
    rec_left.SetSpkModel(spk_model)

    rec_right = KaldiRecognizer(model, sample_rate)
    rec_right.SetSpkModel(spk_model)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break

        left_channel = np.frombuffer(data, dtype=np.int16)[0::2]
        right_channel = np.frombuffer(data, dtype=np.int16)[1::2]

        if rec_left.AcceptWaveform(left_channel.tobytes()):
            res = json.loads(rec_left.Result())
            if 'text' in res:
                res['spk'] = 0
                transcriptions.append(res)

        if rec_right.AcceptWaveform(right_channel.tobytes()):
            res = json.loads(rec_right.Result())
            if 'text' in res:
                res['spk'] = 1
                transcriptions.append(res)

    res_left = json.loads(rec_left.FinalResult())
    if 'text' in res_left:
        res_left['spk'] = 0
        transcriptions.append(res_left)

    res_right = json.loads(rec_right.FinalResult())
    if 'text' in res_right:
        res_right['spk'] = 1
        transcriptions.append(res_right)

    wf.close()

    if len(transcriptions) > 0:
        transcriptions = diarization(transcriptions)

    structured_text = []
    for item in transcriptions:
        if item['text'].strip():
            speaker = 'абонент' if item['spk'] == 0 else 'оператор'
            structured_text.append(f'{speaker}: {item["text"]}')

    formatted_text = "\n".join(structured_text)
    print(f'formatted Text: {formatted_text}')  # убрать, после отладки
    return structured_text
