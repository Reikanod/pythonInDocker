import sys
import json
import subprocess


def fetch_auto_captions(video_url):
    try:
        # Запускаем yt-dlp для получения автоматических субтитров в формате JSON
        result = subprocess.run(
            [
                "yt-dlp",
                "--skip-download",
                "--write-auto-sub",
                "--sub-format", "json3",
                "-o", "/dev/null",
                video_url
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        # Ищем имя файла с субтитрами в stderr
        for line in result.stderr.splitlines():
            if "Writing auto-subtitle to" in line:
                filename = line.split("‘")[1].split("’")[0]

                with open(filename, "r", encoding="utf-8") as f:
                    captions_data = json.load(f)

                return {
                    "status": "success",
                    "video_url": video_url,
                    "captions": captions_data
                }

        return {
            "status": "error",
            "message": "Subtitles file not found in output"
        }

    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "stdout": e.stdout,
            "stderr": e.stderr
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No video URL provided"}))
        sys.exit(1)

    video_url = sys.argv[1]
    response = fetch_auto_captions(video_url)
    print(json.dumps(response, ensure_ascii=False, indent=2))
