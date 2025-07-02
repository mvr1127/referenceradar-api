import re
import json
import subprocess
from fastapi import FastAPI, Query, HTTPException

YOUTUBE_REGEX = re.compile(r"^https?://(www\.)?(youtube\.com|youtu\.be)/")

app = FastAPI()

@app.get("/youtube-chapters")
async def get_chapters(url: str = Query(...)):
    if not YOUTUBE_REGEX.match(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    try:
        result = subprocess.run(
            ['yt-dlp', '-j', url],
            capture_output=True,
            text=True,
            timeout=20
        )
        if result.returncode != 0:
            raise Exception(f"yt-dlp failed: {result.stderr}")

        data = json.loads(result.stdout)
        chapters = data.get("chapters", [])

        # Add end_time to each chapter
        for i in range(len(chapters) - 1):
            chapters[i]["end_time"] = chapters[i + 1]["start_time"]
        if chapters:
            chapters[-1]["end_time"] = data.get("duration")

        return {
            "title": data.get("title"),
            "videoId": data.get("id"),
            "duration": data.get("duration"),
            "chapters": chapters
        }
    except Exception as e:
        # For debugging, return the error message. Remove or sanitize in production!
        raise HTTPException(status_code=500, detail=f"Failed to extract chapters: {str(e)}")