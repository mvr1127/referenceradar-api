import json
import subprocess
from urllib.parse import parse_qs

def handler(request):
    # Parse the query string for the 'url' parameter
    query = request.query_string.decode() if hasattr(request.query_string, 'decode') else request.query_string
    params = parse_qs(query)
    url = params.get('url', [None])[0]
    if not url:
        return (json.dumps({'error': 'Missing or invalid YouTube URL'}), 400, {'Content-Type': 'application/json'})

    try:
        # Run yt-dlp to get JSON metadata
        result = subprocess.run(
            ['yt-dlp', '-j', url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            return (json.dumps({'error': 'yt-dlp failed', 'details': result.stderr}), 500, {'Content-Type': 'application/json'})

        data = json.loads(result.stdout)
        raw_chapters = data.get('chapters', [])

        # Add end_time to each chapter
        for i in range(len(raw_chapters) - 1):
            raw_chapters[i]['end_time'] = raw_chapters[i + 1]['start_time']
        if raw_chapters:
            raw_chapters[-1]['end_time'] = data.get('duration')

        return (
            json.dumps({
                'chapters': raw_chapters,
                'duration': data.get('duration'),
                'title': data.get('title'),
                'videoId': data.get('id'),
            }),
            200,
            {'Content-Type': 'application/json'}
        )
    except Exception as e:
        return (json.dumps({'error': 'Failed to extract chapters', 'details': str(e)}), 500, {'Content-Type': 'application/json'})