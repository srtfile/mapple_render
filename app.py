import json
import time
import base64
import requests
from urllib.parse import quote
from flask import Flask, request, render_template

app = Flask(__name__)

# Constants
KEY = "nanananananananananananaBatman!"
DEFAULT_DOMAIN = "https://mapple.uk"
USER_AGENT = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"

def encrypt_data(url: str) -> str:
    payload = json.dumps({"url": url, "timestamp": int(time.time() * 1000)}, separators=(',', ':'))
    encoded = quote(payload)
    key_len = len(KEY)
    xored_bytes = bytes(
        ord(ch) ^ ord(KEY[i % key_len]) for i, ch in enumerate(encoded)
    )
    return base64.urlsafe_b64encode(xored_bytes).decode().rstrip('=')

def extract_stream(media_id, media_type, season=None, episode=None):
    # Build payload based on media type
    data = {
        'mediaId': int(media_id),
        'mediaType': media_type,
        'source': 'mapple',
        'tv_slug': f'{season}-{episode}' if media_type == 'tv' else ''
    }

    # Encrypt the payload
    inner_json = json.dumps(data, separators=(',', ':'))
    encrypted_data = encrypt_data(inner_json)
    api_url = f'{DEFAULT_DOMAIN}/api/stream-encrypted?data={encrypted_data}'

    headers = {
        "Referer": DEFAULT_DOMAIN,
        "User-Agent": USER_AGENT
    }

    try:
        response = requests.get(api_url, headers=headers).json()
        if not response.get('success'):
            return {"error": response.get('error', 'Unknown API Error')}
        
        return {
            "stream_url": response.get('data', {}).get('stream_url'),
            "headers": headers
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        media_type = request.form.get('media_type')
        media_id = request.form.get('media_id')
        season = request.form.get('season')
        episode = request.form.get('episode')
        
        result = extract_stream(media_id, media_type, season, episode)
        
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
