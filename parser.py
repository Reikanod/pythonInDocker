import sys
import os
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime
import json
import base64
import asyncio
from telethon import TelegramClient
import requests

# Константы
GIT_LAST_POSTS = "https://api.github.com/repos/Reikanod/pythonInDocker/contents/last_posts.json"
GIT_PARSED_POSTS = "https://api.github.com/repos/Reikanod/pythonInDocker/contents/parsed_posts.json"

CHANNELS = ['spletnicca', 'skosoi']

def get_last_posts_from_github(git_token):
    HEADERS = {
        "Authorization": f"Bearer {git_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(GIT_LAST_POSTS, headers=HEADERS)
    if response.status_code == 200:
        content = response.json()['content']
        decoded = base64.b64decode(content).decode('utf-8')
        return json.loads(decoded)
    else:
        return {
            "Error" : f"last_posts.json не загружается с GitHub. Тело ответа: {response.text}"}

async def parse_news(api_id, api_hash, git_token):
    # Проверяем, существует ли файл сессии
    if not os.path.exists("session.session"):
        raise Exception("Файл сессии session.session не найден!")

    # Используем имя сессии "session" — оно соответствует файлу session.session
    client = TelegramClient("session", api_id, api_hash, system_version='4.16.30-vxCUSTOM')
    await client.start()

    # Получаем текущее состояние из GitHub
    state = get_last_posts_from_github(git_token)
    return {
        "Текущий статус": state
    }

"""
    for channel in CHANNELS:
        try:
            entity = await client.get_entity(channel)
            async for message in client.iter_messages(entity, limit=10):  # проверяем последние 10 сообщений
                if str(message.id) == state.get(channel):
                    print(f"Достигнут последний уже обработанный пост в канале {channel}")
                    break

                print(f"[{channel}] Новый пост ID {message.id}: {message.text[:50]}...")

            # Сохраняем ID последнего обработанного сообщения
            if message:
                state[channel] = str(message.id)

        except Exception as e:
            print(f"Ошибка при работе с каналом {channel}: {e}")

    # Сохраняем обновлённое состояние обратно на GitHub
    save_last_posts_to_github(state)"""