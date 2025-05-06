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


@app.route("/get_captions", methods=["POST", "GET"])
def get_captions():
    try:
        if not request.is_json:
            return {"error": "Request must have 'Content-Type: application/json'"}, 400
        return {"status": "valid JSON"}

        data = request.get_json()
        video_url = data.get("video_url")
        if not video_url:
            return {"error": "Missing 'video_url' in request"}, 400

        logging.info(f"Received video_url: {video_url}")

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
            return {"status": "error", "stderr": e.stderr}, 500

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return {"error": "Invalid JSON request"}, 400




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
