from pydub import AudioSegment
from pydub.effects import normalize, low_pass_filter, high_pass_filter
import os
import wave
import json
import numpy as np
import noisereduce as nr
import sys

from dotenv import load_dotenv
from loguru import logger
from vosk import Model, KaldiRecognizer, SpkModel, SetLogLevel

from handlers.dict import replacement_dict

SetLogLevel(-1)

load_dotenv()
SPK_MODEL_PATH = os.getenv('SPK_MODEL_PATH')
VOSK_MODEL_PATH = os.getenv('VOSK_MODEL_PATH')


def reduce_noise(file_path):
    '''мягкое шумоподавление с сохранением высоких частот'''
    audio = AudioSegment.from_wav(file_path)
    samples = np.array(audio.get_array_of_samples())

    reduced_noise = nr.reduce_noise(
        y=samples,
        sr=audio.frame_rate,
        prop_decrease=0.5,  # Уменьшаем шум на ...%
        stationary=False,   # Для нестационарного шума
        n_fft=1024,         # Размер окна для FFT
        win_length=512,     # Длина окна
        hop_length=256      # Шаг окна
    )

    # восстановление высоких частот
    filtered_audio = high_pass_filter(
        AudioSegment(
            reduced_noise.tobytes(),
            frame_rate=audio.frame_rate,
            sample_width=audio.sample_width,
            channels=audio.channels
        ),
        cutoff=2000
    )

    temp_file = file_path.replace('.wav', '_noise_reduced.wav')
    filtered_audio.export(temp_file, format='wav')
    return temp_file


def normalize_audio(file_path):
    '''нормализация и фильтрация шума в аудиофайле'''
    audio = AudioSegment.from_wav(file_path)
    normalized_audio = normalize(audio)
    temp_file = file_path.replace('.wav', '_normalized.wav')
    normalized_audio.export(temp_file, format='wav')
    return temp_file


def improve_audio_quality(file_path):
    file_path = reduce_noise(file_path)
    file_path = normalize_audio(file_path)
    return file_path


def correct_transcription(text):
    '''функция для замены ошибочных фраз в тексте'''
    for wrong, correct in replacement_dict.items():
        if wrong in text:
            text = text.replace(wrong, correct)
            logger.info(f'"{wrong}" -> "{correct}"')
    return text


def process_audio(file_path):
    file_path = improve_audio_quality(file_path)
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
    rec_left.SetPartialWords(True)

    rec_right = KaldiRecognizer(model, sample_rate)
    rec_right.SetSpkModel(spk_model)
    rec_right.SetPartialWords(True)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break

        # разделение на левый и правый канал
        left_channel = np.frombuffer(data, dtype=np.int16)[0::2]
        right_channel = np.frombuffer(data, dtype=np.int16)[1::2]

        # обработка левого канала (абонент)
        if rec_left.AcceptWaveform(left_channel.tobytes()):
            res = json.loads(rec_left.Result())
            if 'text' in res:
                res['spk'] = 0  # абонент
                transcriptions.append(res)

        # обработка правого канала (оператор)
        if rec_right.AcceptWaveform(right_channel.tobytes()):
            res = json.loads(rec_right.Result())
            if 'text' in res:
                res['spk'] = 1  # оператор
                transcriptions.append(res)

    # завершение распознавания для левого канала
    res_left = json.loads(rec_left.FinalResult())
    if 'text' in res_left:
        res_left['spk'] = 0
        transcriptions.append(res_left)

    # завершение распознавания для правого канала
    res_right = json.loads(rec_right.FinalResult())
    if 'text' in res_right:
        res_right['spk'] = 1
        transcriptions.append(res_right)

    wf.close()

    # форматирование результатов
    structured_text = []
    for item in transcriptions:
        if item['text'].strip():
            speaker = 'абонент' if item['spk'] == 0 else 'оператор'
            corrected_text = correct_transcription(item['text'])
            structured_text.append(f'{speaker}: {corrected_text}')

    formatted_text = "\n".join(structured_text)
    print(f'formatted Text: {formatted_text}')  # убрать после отладки
    return structured_text
