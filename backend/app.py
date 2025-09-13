from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.agents import vibe_check_agent

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for all routes

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/lesson', methods=['POST'])
def generate_lesson():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query parameter'}), 400

    query = data['query']
    subject = data.get('subject', 'Math')  # Default to Math if not provided
    language = data.get('language', 'English')  # Default to English if not provided

    try:
        result = vibe_check_agent(query, subject, language)
        # Extract meme URL if present
        import re
        urls = re.findall(r"https?://[^\s)]+", result)
        meme_url = urls[0] if urls and urls[0].endswith(('.jpg', '.jpeg', '.png')) else None

        response = {
            'lesson': result,
            'meme_url': meme_url if meme_url and 'failed' not in meme_url else None
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Changed port to 5001 to avoid conflict with AirPlay