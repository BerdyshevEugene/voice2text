import requests

url = 'http://127.0.0.1:8000/process_audio/'
data = {'url': 'url'}


try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    print('Transcriptions:', response.json())
except requests.exceptions.RequestException as e:
    print('Error:', e)