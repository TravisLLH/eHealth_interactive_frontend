from flask import Flask, request, jsonify
from flask_cors import CORS
import redis
import json
import logging
import requests # Import the requests library

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# In-memory stores for fallback if Redis is down (not used in this logic but kept for consistency)
data_store = {}
video_command_store = {}
session_id_store = None
loading_gif_store = {}


@app.route('/post_message', methods=['POST'])
def post_message():
    data = request.get_json()
    if not data or 'session_id' not in data or 'message' not in data:
        logging.error("Invalid post_message request")
        return jsonify({"error": "session_id and message required"}), 400
    
    session_id = data['session_id']
    message_payload = {
        'session_id': session_id,
        'message': data['message'],
        'type': data.get('type'),
        'language': data.get('language', 'en'),
        'question_format': data.get('question_format'),
        'order': data.get('order'),
        'MIN': data.get('MIN'),
        'MAX': data.get('MAX'),
        'start_at': data.get('start_at'),
        'end_at': data.get('end_at'),
        'subtitle': data.get('subtitle', True),
        'font_size': data.get('font_size', 100)
    }
    redis_client.set(f'message:{session_id}', json.dumps(message_payload))
    logging.info(f"Message stored for {session_id}")

    # When a new message (especially a video) is posted, reset any lingering play commands
    stop_command_payload = {'session_id': session_id, 'start_or_stop': False, 'move_to': None}
    redis_client.set(f'video_command:{session_id}', json.dumps(stop_command_payload))
    logging.info(f"Video command for {session_id} has been reset to 'stop'.")
    
    return jsonify({"message": "Message stored"}), 201


@app.route('/video_ended', methods=['POST'], strict_slashes=False)
def video_ended():
    data = request.get_json()
    if not data or 'session_id' not in data:
        logging.error("Invalid video_ended request")
        return jsonify({"error": "session_id required"}), 400

    session_id = data['session_id']
    logging.info(f"SUCCESS: Video playback ended notification received for session: {session_id}")
    
    # In a real system, another process could now post the next message.
    # For now, this endpoint successfully receives the notice.
    return jsonify({"message": "Video ended notification received"}), 200


@app.route('/get_message/<session_id>', methods=['GET'])
def get_message(session_id):
    message = redis_client.get(f'message:{session_id}')
    if message: return jsonify(json.loads(message)), 200
    logging.warning(f"Message not found for {session_id}")
    return jsonify(None), 404


@app.route('/post_video_command', methods=['POST'])
def post_video_command():
    data = request.get_json()
    if not data or 'session_id' not in data:
        logging.error("Invalid video_command request: session_id missing")
        return jsonify({"error": "session_id required"}), 400

    session_id = data.get('session_id')
    start_or_stop = data.get('start_or_stop')
    move_to = data.get('move_to', None)

    if start_or_stop is None and move_to is None:
        logging.error("Invalid video_command request: start_or_stop or move_to required")
        return jsonify({"error": "start_or_stop or move_to required"}), 400

    # Publish the command to Redis for the frontend to consume
    command_payload = {'session_id': session_id, 'start_or_stop': start_or_stop, 'move_to': move_to}
    redis_client.set(f'video_command:{session_id}', json.dumps(command_payload))
    logging.info(f"Video command for {session_id} ({'Start' if start_or_stop else 'Stop'}) published to Redis.")

    # **THE DEFINITIVE FIX:** If the command is to stop the video, the backend triggers the /video_ended event itself.
    if start_or_stop is False:
        logging.info(f"Stop command received for {session_id}. Triggering /video_ended event.")
        try:
            # Construct the full URL for the /video_ended endpoint
            ended_url = request.url_root + 'video_ended'
            payload = {'session_id': session_id}
            # Make an internal POST request to the video_ended endpoint
            requests.post(ended_url, json=payload, timeout=5)
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to internally call /video_ended: {str(e)}")
    
    return jsonify({"message": "Command stored"}), 201


@app.route('/get_video_command/<session_id>', methods=['GET'])
def get_video_command(session_id):
    command = redis_client.get(f'video_command:{session_id}')
    if command: return jsonify(json.loads(command)), 200
    logging.warning(f"Command not found for {session_id}")
    return jsonify({}), 200


@app.route('/post_session_id', methods=['POST'])
def post_session_id():
    data = request.get_json()
    session_id = data.get('session_id')
    if session_id is None:
        redis_client.delete('current_session_id')
        logging.info("Session ID cleared")
        return jsonify({"message": "Session ID cleared"}), 201
    else:
        redis_client.set('current_session_id', str(session_id))
        logging.info(f"Session ID set to {session_id}")
        message_payload = {'session_id': session_id, 'type': 'image', 'message': "intro_page"}
        redis_client.set(f'message:{session_id}', json.dumps(message_payload))
        logging.info(f"Default intro image stored for {session_id}")
        return jsonify({"message": "Session ID set"}), 201


@app.route('/get_session_id', methods=['GET'])
def get_session_id():
    sid = redis_client.get('current_session_id')
    return jsonify({"session_id": sid}), 200


@app.route('/post_loading_gif', methods=['POST'])
def post_loading_gif():
    data = request.get_json()
    if not data or 'session_id' not in data or 'load_or_unload' not in data:
        logging.error("Invalid loading_gif request")
        return jsonify({"error": "session_id and load_or_unload required"}), 400
    session_id = data['session_id']
    load_or_unload = data['load_or_unload']
    loading_payload = {'session_id': session_id, 'load': load_or_unload}
    redis_client.set(f'loading_gif:{session_id}', json.dumps(loading_payload))
    logging.info(f"Loading GIF command stored for {session_id}: {'Load' if load_or_unload else 'Unload'}")
    return jsonify({"message": "Loading GIF command stored"}), 201


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)