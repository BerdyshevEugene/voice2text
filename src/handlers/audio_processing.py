import aiohttp
import aiofiles
import asyncio
import os

from loguru import logger
from tempfile import NamedTemporaryFile

from handlers.socket_communication import send_data_to_socket
from handlers.audio_vosk import process_audio


async def download_audio(url: str) -> str | None:
    try:
        logger.info(f'downloading audio from {url}')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    tmp_file = NamedTemporaryFile(delete=False, suffix='.wav')
                    async with aiofiles.open(tmp_file.name, 'wb') as f:
                        await f.write(await response.read())
                    logger.info(f'temporary file created: {tmp_file.name}')
                    return tmp_file.name
                else:
                    logger.error(
                        f'failed to download audio: {response.status}')
                    return None
    except Exception as e:
        logger.error(f'error in download_audio: {e}')
        return None


async def process_audio_background(master_id: int, url: str):
    try:
        logger.info(f'processing audio for MasterID {master_id}, URL: {url}')
        file_path = await download_audio(url)
        if not file_path or not os.path.isfile(file_path):
            logger.error(f'file not found or invalid: {file_path}')
            return

        transcriptions = await asyncio.to_thread(process_audio, file_path)
        text_content = '\n'.join(transcriptions)

        await send_data_to_socket({
            'ChannelName': 'IncomingCall',
            'Event': 'voice2text',
            'MasterID': master_id,
            'text': text_content
        })

        logger.success(
            f'audio processed successfully for MasterID {master_id}')
        os.remove(file_path)  # удаляем временный файл после обработки
        logger.info(f'temporary file deleted: {file_path}')
    except Exception as e:
        logger.error(f'error processing audio: {e}')
