import json
import subprocess
from urllib.parse import parse_qs

def handler(request, response):
    # Parse the query string for the 'url' parameter
    query = request.query_string
    params = parse_qs(query)
    url = params.get('url', [None])[0]
    if not url:
        response.status_code = 400
        response.body = json.dumps({'error': 'Missing or invalid YouTube URL'})
        return response

    try:
        # Run yt-dlp to get JSON metadata
        result = subprocess.run([
            'yt-dlp', '-j', url
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            response.status_code = 500
            response.body = json.dumps({'error': 'yt-dlp failed', 'details': result.stderr})
            return response

        data = json.loads(result.stdout)
        raw_chapters = data.get('chapters', [])

        # Add end_time to each chapter
        for i in range(len(raw_chapters) - 1):
            raw_chapters[i]['end_time'] = raw_chapters[i + 1]['start_time']
        if raw_chapters:
            raw_chapters[-1]['end_time'] = data.get('duration')

        response.status_code = 200
        response.body = json.dumps({
            'chapters': raw_chapters,
            'duration': data.get('duration'),
            'title': data.get('title'),
            'videoId': data.get('id'),
        })
        return response
    except Exception as e:
        response.status_code = 500
        response.body = json.dumps({'error': 'Failed to extract chapters', 'details': str(e)})
        return response 