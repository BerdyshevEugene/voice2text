import asyncio
import json
import os

from loguru import logger
from aio_pika import IncomingMessage

from handlers.audio_processing import process_audio_background


async def handle_message(message: IncomingMessage):
    '''
    обработка сообщений RabbitMQ
    '''
    try:
        data = json.loads(message.body)
        logger.info(f'received message: {data}')

        master_id = data.get('MasterID')
        url = data.get('url')
        if not master_id or not url:
            logger.error('invalid message format, rejecting')
            await message.reject()
            return

        await process_audio_background(master_id, url)
        await message.ack()
    except Exception as e:
        logger.error(f'error in handle_message: {e}')
        await message.reject()
