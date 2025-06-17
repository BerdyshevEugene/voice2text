import os
import json

from aio_pika import connect_robust, Message, exceptions
from loguru import logger


RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost/')
V2T_RESULTS_QUEUE = os.getenv('QUEUE_NAME', 'v2t_dg_queue')
V2T_VERBAMETRICS_QUEUE = os.getenv(
    'V2T_VERBAMETRICS_QUEUE', 'v2t_verbaMetrics')


async def publish_results_to_queue(data: dict):
    '''
    отправка преобразованных аудио в текст в очередь для datagate
    '''
    try:
        connection = await connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                Message(body=json.dumps(data).encode(), delivery_mode=2),
                routing_key=V2T_RESULTS_QUEUE
            )
            logger.success(
                f'data published to queue {V2T_RESULTS_QUEUE}: {data}')
    except exceptions.AMQPConnectionError as e:
        logger.error(f'failed to connect to RabbitMQ: {e}')
    except Exception as e:
        logger.error(f'error publishing message to RabbitMQ: {e}')


async def publish_results_to_v2t_vrbmtrcs_queue(data: dict):
    '''
    отправка преобразованных аудио в текст в очередь для verbaMetrics
    '''
    try:
        connection = await connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue(V2T_VERBAMETRICS_QUEUE, durable=True, passive=True)
            await channel.default_exchange.publish(
                Message(body=json.dumps(data).encode(), delivery_mode=2),
                routing_key=V2T_VERBAMETRICS_QUEUE
            )
            logger.success(
                f'data published to queue {V2T_VERBAMETRICS_QUEUE}: {data}')
    except exceptions.AMQPConnectionError as e:
        logger.error(f'failed to connect to RabbitMQ: {e}')
    except Exception as e:
        logger.error(f'error publishing message to RabbitMQ: {e}')
