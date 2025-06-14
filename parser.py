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
# У каждого канала сохраняется последний спарсенный message_id
GIT_LAST_POSTS = "https://api.github.com/repos/Reikanod/pythonInDocker/contents/last_posts.json"
# Все спарсенные посты
GIT_PARSED_POSTS = "https://api.github.com/repos/Reikanod/pythonInDocker/contents/parsed_posts.json"

CHANNELS = [
    'spletnicca', 'skosoi', "spletnicca", "skosoi", "MediaKiller2021", "nabludatels", "first_political", "bankrollo",
    "banksta", "ZE_kartel", "Taynaya_kantselyariya", "ZeRada1", "ASupersharij", "infantmilitario", "legitimniy",
    "rezident_ua", "the_military_analytics", "ejdailyru", "vchkogpu_ru", "boris_rozhin", "dimsmirnov175",
    "SergeyKolyasnikov", "rlz_the_kraken", "opersvodki", "russicaRU", "politnewstg", "Sandymustache",
    "mig41", "vysokygovorit", "crimsondigest", "dossiercenter", "underside_org", "maester", "stalin_gulag",
    "strelkovii", ""
]

# Получает весь файл last_posts.json, в котором хранятся названия каналов и message_id последнего спарсенного поста
def get_last_posts_from_github(git_token):
    HEADERS = {
        "Authorization": f"Bearer {git_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(GIT_LAST_POSTS, headers=HEADERS)
    if response.status_code == 200:
        content = response.json().get('content', '')
        if not content.strip():
            return {}  # файл пустой — возвращаем пустой словарь
        try:
            decoded = base64.b64decode(content).decode('utf-8')
            return json.loads(decoded)
        except Exception as e:
            print(f"[Ошибка] Не удалось декодировать last_posts.json: {e}")
            return {}
    else:
        print(f"[Ошибка] Не удалось получить last_posts.json с GitHub: {response.text}")
        return {}

# Обновляет last_posts на гитхабе
def update_last_posts_on_github(data_dict, git_token):
    HEADERS = {
        "Authorization": f"Bearer {git_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Получаем SHA текущей версии файла — требуется для обновления
    response = requests.get(GIT_LAST_POSTS, headers=HEADERS)
    if response.status_code != 200:
        print(f"[Ошибка] Не удалось получить SHA last_posts.json: {response.text}")
        return False

    sha = response.json().get("sha")
    new_content = base64.b64encode(json.dumps(data_dict, indent=2).encode("utf-8")).decode("utf-8")

    update_response = requests.put(
        GIT_LAST_POSTS,
        headers=HEADERS,
        json={
            "message": "Обновление last_posts.json",
            "content": new_content,
            "sha": sha
        }
    )

    return update_response.status_code == 200


# Основной парсер новостей. Ее вызываем из main
async def parse_news(api_id, api_hash, git_token):
    if not os.path.exists("session.session"):
        raise Exception("Файл сессии session.session не найден!")
    # Создаем коннект с тг
    client = TelegramClient("session", api_id, api_hash, system_version='4.16.30-vxCUSTOM')
    await client.start()

    last_posts = get_last_posts_from_github(git_token)
    new_posts_found = False

    for channel in CHANNELS:
        try:
            entity = await client.get_entity(channel)
            last_id = last_posts.get(channel)  # может быть None
            new_messages = []

            async for message in client.iter_messages(entity, limit=50):
                if last_id and message.id <= int(last_id):
                    print(f"Достигнут последний известный ID {last_id} в канале {channel}. Прерываю.")
                    break

                new_messages.append(message)
                print(f"[{channel}] Новый пост ID {message.id}: {message.text[:50]}...")

            if new_messages:
                last_posts[channel] = str(new_messages[0].id)
                new_posts_found = True
            elif channel not in last_posts:
                # Если нет постов, но канал новый — всё равно добавим пустое значение
                last_posts[channel] = None
                new_posts_found = True
                print(f"[{channel}] Новый канал добавлен в список без новых постов.")

        except Exception as e:
            print(f"Ошибка при работе с каналом {channel}: {e}")

    # Если были найдены новые посты — обновляем файл на GitHub
    if new_posts_found:
        success = update_last_posts_on_github(last_posts, git_token)
        if success:
            print("✅ Состояние успешно сохранено")
        else:
            print("❌ Не удалось сохранить состояние")
    else:
        print("ℹ️ Новых постов не найдено, обновление last_posts.json не требуется")