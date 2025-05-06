from flask import Flask
import subprocess
import sys

app = Flask(__name__)

@app.route("/run", methods=["POST"])
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
