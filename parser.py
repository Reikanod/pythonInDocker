import os
import json
import base64
import asyncio
import logging
from telethon import TelegramClient
import requests

# Логирование в stdout (Railway автоматически видит stdout и stderr)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Константы GitHub API и каналы
GIT_LAST_POSTS = "https://api.github.com/repos/Reikanod/pythonInDocker/contents/last_posts.json"
GIT_PARSED_POSTS = "https://api.github.com/repos/Reikanod/pythonInDocker/contents/parsed_posts.json"

CHANNELS = list(set([
    'spletnicca', 'skosoi', "MediaKiller2021", "nabludatels", "first_political", "bankrollo",
    "banksta", "ZE_kartel", "Taynaya_kantselyariya", "ZeRada1", "ASupersharij", "infantmilitario", "legitimniy",
    "rezident_ua", "the_military_analytics", "ejdailyru", "vchkogpu_ru", "boris_rozhin", "dimsmirnov175",
    "SergeyKolyasnikov", "rlz_the_kraken", "opersvodki", "russicaRU", "politnewstg", "Sandymustache",
    "mig41", "vysokygovorit", "crimsondigest", "dossiercenter", "underside_org", "maester", "stalin_gulag",
    "strelkovii"
]))

# --- Вспомогательные функции для GitHub ---

def github_get_file(url, git_token):
    HEADERS = {
        "Authorization": f"Bearer {git_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            content = response.json().get('content', '')
            if not content:
                return {}
            decoded = base64.b64decode(content).decode('utf-8')
            return json.loads(decoded)
        else:
            logging.error(f"GitHub GET error {response.status_code}: {response.text}")
            return {}
    except Exception as e:
        logging.error(f"GitHub GET exception: {e}")
        return {}

def github_update_file(url, data_dict, git_token, commit_message):
    HEADERS = {
        "Authorization": f"Bearer {git_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        # Получаем sha текущего файла
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            logging.error(f"GitHub update: не удалось получить SHA файла {url}: {resp.text}")
            return False
        sha = resp.json().get("sha")
        new_content = base64.b64encode(json.dumps(data_dict, indent=2, ensure_ascii=False).encode("utf-8")).decode("utf-8")

        update_resp = requests.put(
            url,
            headers=HEADERS,
            json={
                "message": commit_message,
                "content": new_content,
                "sha": sha
            },
            timeout=20
        )
        if update_resp.status_code == 200:
            logging.info(f"GitHub файл обновлен успешно: {commit_message}")
            return True
        else:
            logging.error(f"GitHub PUT error {update_resp.status_code}: {update_resp.text}")
            return False
    except Exception as e:
        logging.error(f"GitHub PUT exception: {e}")
        return False

# --- Функции работы с last_posts.json ---

def get_last_posts_from_github(git_token):
    return github_get_file(GIT_LAST_POSTS, git_token)

def update_last_posts_on_github(data_dict, git_token):
    return github_update_file(GIT_LAST_POSTS, data_dict, git_token, "Обновление last_posts.json")

# --- Функции работы с parsed_posts.json ---

def get_parsed_posts_from_github(git_token):
    return github_get_file(GIT_PARSED_POSTS, git_token)

def update_parsed_posts_on_github(data_dict, git_token):
    return github_update_file(GIT_PARSED_POSTS, data_dict, git_token, "Обновление parsed_posts.json")

# --- Парсер новостей ---

async def parse_news(api_id, api_hash, git_token):
    session_file = "session.session"
    if not os.path.exists(session_file):
        raise Exception(f"Файл сессии {session_file} не найден!")

    client = TelegramClient("session", api_id, api_hash, system_version='4.16.30-vxCUSTOM')
    await client.start()

    last_posts = get_last_posts_from_github(git_token)
    if not isinstance(last_posts, dict):
        logging.warning("last_posts пустой или поврежден, инициализируем пустым словарем")
        last_posts = {}

    parsed_posts = get_parsed_posts_from_github(git_token)
    if not isinstance(parsed_posts, dict):
        logging.warning("parsed_posts пустой или поврежден, инициализируем пустым словарем")
        parsed_posts = {}

    new_posts_found = False

    for channel in CHANNELS:
        if not channel:
            continue  # пропускаем пустые строки

        try:
            entity = await client.get_entity(channel)
        except Exception as e:
            logging.error(f"[{channel}] Ошибка при получении entity: {e}")
            continue

        last_id_str = last_posts.get(channel)
        last_id = int(last_id_str) if last_id_str and last_id_str.isdigit() else 0
        new_messages = []

        try:
            async for message in client.iter_messages(entity, limit=50):
                if message.id <= last_id:
                    logging.info(f"[{channel}] Достигнут последний известный ID {last_id}. Прерываю.")
                    break

                new_messages.append(message)

            if new_messages:
                # Сохраняем самый новый ID
                last_posts[channel] = str(new_messages[0].id)
                new_posts_found = True

                # Обновляем parsed_posts для каждого нового сообщения
                if channel not in parsed_posts:
                    parsed_posts[channel] = {}

                for msg in reversed(new_messages):  # от старого к новому для логики
                    content_text = msg.text or ""
                    media_links = []

                    if msg.media:
                        # Собираем ссылки на медиа (картинки, видео)
                        try:
                            if hasattr(msg.media, 'photo'):
                                # Получить прямую ссылку на фото (пример через client.download_media)
                                # Но для GitHub, скорее всего, нужно просто URL
                                # Telegram API не даёт прямые ссылки, нужна загрузка или прокси
                                # Пока сохраняем placeholder
                                media_links.append("[photo]")
                            elif hasattr(msg.media, 'document'):
                                media_links.append("[document]")
                        except Exception as me:
                            logging.warning(f"[{channel}][msg {msg.id}] Ошибка получения медиа ссылок: {me}")

                    # Сохраняем по ID сообщения
                    parsed_posts[channel][str(msg.id)] = {
                        "content": content_text,
                        "media_links": media_links
                    }

                logging.info(f"[{channel}] Добавлено/обновлено {len(new_messages)} новых постов в parsed_posts.")

            elif channel not in last_posts:
                last_posts[channel] = "0"
                new_posts_found = True
                logging.info(f"[{channel}] Новый канал добавлен в last_posts без новых сообщений.")

        except Exception as e:
            logging.error(f"[{channel}] Ошибка при обработке сообщений: {e}")

    if new_posts_found:
        success_lp = update_last_posts_on_github(last_posts, git_token)
        success_pp = update_parsed_posts_on_github(parsed_posts, git_token)
        if success_lp and success_pp:
            logging.info("✅ Все данные успешно сохранены на GitHub")
        else:
            logging.error("❌ Ошибка при сохранении данных на GitHub")
    else:
        logging.info("ℹ️ Новых постов не найдено, обновление файлов не требуется")

    return {"status": "success", "message": "Новости обработаны"}
