import sys
import json
import json
import os
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime

async def show_res(api_id, api_hash):
    # Проверяем, существует ли файл сессии
    if not os.path.exists("session.session"):
        raise Exception("Файл сессии session.session не найден!")

    # Используем имя сессии "session" — оно соответствует файлу session.session
    client = TelegramClient("session", api_id, api_hash, system_version='4.16.30-vxCUSTOM')

    # Запускаем клиент
    await client.start()  # если аккаунт с двухфакторной аутентификацией

    # Пример: получение собственного username
    me = await client.get_me()
    raise Exception(f"Вы вошли как {me.username}")

    return client
