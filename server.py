from flask import Flask, request
import subprocess
import sys
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route("/check")
def check():
    logging.info("Received /check request")
    return {"status": "alive"}

@app.route("/get_captions", methods=["POST"])
def get_captions():
    logging.info("Received POST request to /get_captions")
    data = request.json or {}
    video_url = data.get("video_url")
    if not video_url:
        logging.error("Missing 'video_url' in request")
        return {"error": "Missing 'video_url' in request"}, 400

    try:
        result = subprocess.run(
            [sys.executable, "get_captions.py", video_url],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info(f"Captions fetched successfully: {result.stdout}")
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error fetching captions: {e.stderr}")
        try:
            error_data = json.loads(e.stdout)
            return error_data, 500
        except Exception:
            return {
                "status": "error",
                "stdout": e.stdout,
                "stderr": e.stderr
            }, 500

@app.route("/run", methods=["POST", "GET"])
def run_script():
    logging.info("Received request to /run")
    try:
        result = subprocess.run(
            [sys.executable, "myscript.py"],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info(f"Script executed successfully: {result.stdout}")
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running script: {e.stderr}")
        return {"status": "error", "output": e.stderr}, 500
