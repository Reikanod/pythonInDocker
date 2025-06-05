import json
import os
import sys
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime

# Получение аргумента и распаковка
def load_credentials_from_args():
    try:
        input_json = sys.argv[1]
        data = json.loads(input_json)
        return int(data["api_id"]), data["api_hash"], data["password"]
    except Exception as e:
        print(f"[ERROR] Ошибка загрузки аргументов: {e}")
        sys.exit(1)

api_id, api_hash, password = load_credentials_from_args()

# (опционально) Проверка пароля
if password != "твой_секретный_пароль":  # Заменить на реальный
    print("[ERROR] Неверный пароль")
    sys.exit(1)

# Список каналов
channels = [
    "spletnicca", "skosoi"
]

# Создание клиента
client = TelegramClient("session", api_id, api_hash, system_version='4.16.30-vxCUSTOM')

# Парсинг постов
def fetch_posts(channel_name, last_date=None, limit=100):
    result = []
    newest_date = last_date
    try:
        entity = client.get_entity(channel_name)
        history = client(GetHistoryRequest(
            peer=entity,
            limit=limit,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))

        for msg in history.messages:
            if msg.message and (last_date is None or msg.date > last_date):
                result.append({
                    "channel": channel_name,
                    "content": msg.message,
                    "date": msg.date.strftime('%Y-%m-%d %H:%M:%S'),
                    "link": f"https://t.me/{channel_name}/{msg.id}"
                })
                if newest_date is None or msg.date > newest_date:
                    newest_date = msg.date

    except Exception as e:
        print(f"[ERROR] Канал {channel_name}: {e}")

    return result, newest_date


# Путь к файлу с датой последнего парсинга
DATA_DIR = os.path.join(os.path.dirname(__file__), "parser_data")
os.makedirs(DATA_DIR, exist_ok=True)
LAST_DATE_FILE = os.path.join(DATA_DIR, "last_parsed_date.txt")

def load_last_date():
    if os.path.exists(LAST_DATE_FILE):
        with open(LAST_DATE_FILE, "r") as f:
            return datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")
    return None

def save_last_date(date):
    with open(LAST_DATE_FILE, "w") as f:
        f.write(date.strftime("%Y-%m-%d %H:%M:%S"))

# Основной блок
client.start()
all_posts = []
MAX_POSTS = 500

last_date = load_last_date()
max_new_date = last_date

for ch in channels:
    print(f"Чтение канала: {ch}")
    posts, new_date = fetch_posts(ch, last_date=last_date, limit=100)
    all_posts.extend(posts)

    if new_date and (max_new_date is None or new_date > max_new_date):
        max_new_date = new_date

    if len(all_posts) >= MAX_POSTS:
        all_posts = all_posts[:MAX_POSTS]
        break

if max_new_date:
    save_last_date(max_new_date)

# Сохранение в JSON
output_path = os.path.join(DATA_DIR, "parsed_posts.json")
with open(output_path, "w", encoding='utf-8') as f:
    json.dump(all_posts, f, ensure_ascii=False, indent=2)

print(f"Готово. Сохранено {len(all_posts)} постов.")
