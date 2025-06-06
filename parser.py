import sys
import json
import json
import os
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime

async def parse_news(api_id, api_hash):
    # Проверяем, существует ли файл сессии
    if not os.path.exists("session.session"):
        raise Exception("Файл сессии session.session не найден!")

    # Используем имя сессии "session" — оно соответствует файлу session.session
    client = TelegramClient("session", api_id, api_hash, system_version='4.16.30-vxCUSTOM')

    # Запускаем клиент
    await client.start()

    # Каналы для парсинга
    channels = ['spletnicca', 'skosoi']

    # Парсинг
    for channel in channels:
        try:
            entity = await client.get_entity(channel)
            async for message in client.iter_messages(entity, limit=5):  # последние 5 постов
                print(f"Канал: {channel}, Текст: {message.text}\n{'-'*40}")
        except Exception as e:
            print(f"Ошибка при парсинге канала {channel}: {e}")