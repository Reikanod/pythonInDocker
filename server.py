from flask import Flask, request
import subprocess
import sys
import json

app = Flask(__name__)

# Запустить get_captions.py - получает субтитры из ютуб видео. Ссылку на видео получает в json виде от n8n
@app.route("/get_captions", methods=["POST"])
@app.route("/get_captions/", methods=["POST"])
def get_captions():
    data = request.json or {}

    video_url = data.get("video_url")
    if not video_url:
        return {"error": "Missing 'video_url' in request"}, 400

    try:
        result = subprocess.run(
            [sys.executable, "get_captions.py", video_url],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        try:
            error_data = json.loads(e.stdout)
            return error_data, 500
        except Exception:
            return {
                "status": "error",
                "stdout": e.stdout,
                "stderr": e.stderr
            }, 500





# Запустить myscript.py
@app.route("/run", methods=["POST", "GET"])
def run_script():
    try:
        result = subprocess.run(
            [sys.executable, "myscript.py"],
            capture_output=True,
            text=True,
            check=True
        )
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "output": e.stderr}, 500



# Проверить статус работы сервера
@app.route("/check")
def check():
    return {"status": "alive"}

