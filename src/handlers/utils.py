import requests

from tempfile import NamedTemporaryFile


def download_audio(url):
    '''
    функция скачивает .wav файл по ссылке
    '''
    response = requests.get(url)
    if response.status_code == 200:
        with NamedTemporaryFile(delete=True, suffix='.wav') as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    else:
        raise Exception(f'failed to download audio from: {url}')
