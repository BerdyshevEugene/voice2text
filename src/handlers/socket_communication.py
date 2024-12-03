import aiohttp
import os

from dotenv import load_dotenv

from loguru import logger

load_dotenv()

LOCAL_HOST = os.getenv('HOST', 'localhost')
LOCAL_PORT = os.getenv('PORT', '64121')


async def send_data_to_socket(data):
    '''
    отправка данных в сокет
    '''
    try:
        url = f'http://{LOCAL_HOST}:{LOCAL_PORT}/process_data'
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    logger.success(f'data successfully sent: {data}')
                else:
                    logger.error(f'failed to send data: {response.status}')
    except Exception as e:
        logger.error(f'error in send_data_to_socket: {e}')
