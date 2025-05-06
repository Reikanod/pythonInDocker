from flask import Flask
import subprocess
import sys

app = Flask(__name__)

@app.route("/test-post", methods=["POST"])
def test_post():
    return {"status": "post received"}

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

@app.route("/check")
def check():
    return {"status": "alive"}

