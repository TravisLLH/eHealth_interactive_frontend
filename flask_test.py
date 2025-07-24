from flask import Flask, request, jsonify
import redis
import json
import logging
from utils import get_base64_image

app = Flask(__name__)

# Configure logging for traceability
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Fallback stores
data_store = {}
video_command_store = {}
session_id_store = None


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
        'language': data.get('language', 'en'),  # Default to English if not provided
        'question_format': data.get('question_format'),
        # Scale specific fields
        'order': data.get('order'),
        'MIN': data.get('MIN'),
        'MAX': data.get('MAX'),
        # Video specific fields
        'start_at': data.get('start_at'),  # Optional field for video start time
        'end_at': data.get('end_at'),       # Optional field for video end time
        'subtitle': data.get('subtitle', True),  # Default to True if not provided
        # Plain Text
        'font_size': data.get('font_size', 100)  # Default font size for plain text
    }
    redis_client.set(f'message:{session_id}', json.dumps(message_payload))
    data_store[session_id] = message_payload
    logging.info(f"Message stored for {session_id}")

    # When a new message is posted, always reset the video command to 'stop'.
    # This prevents a new video from auto-playing based on a previous command.
    stop_command_payload = {
        'session_id': session_id,
        'start_or_stop': False,
        'move_to': None
    }
    redis_client.set(f'video_command:{session_id}', json.dumps(stop_command_payload))
    video_command_store[session_id] = stop_command_payload
    logging.info(f"Video command for {session_id} has been reset to 'stop'.")

    return jsonify({"message": "Message stored"}), 201


@app.route('/get_message/<session_id>', methods=['GET'])
def get_message(session_id):
    message = redis_client.get(f'message:{session_id}')
    if message:
        return jsonify(json.loads(message)), 200
    if session_id in data_store:
        return jsonify(data_store[session_id]), 200
    logging.warning(f"Message not found for {session_id}")
    return jsonify(None), 404


@app.route('/post_video_command', methods=['POST'])
def post_video_command():
    """
    This endpoint allows clients to send video control commands for a specific session.
    Commands can include:
    1. Starting or stopping the video
    2. Directing the video to a specific timestamp
    """

    data = request.get_json()
    if not data or 'session_id' not in data or 'start_or_stop' not in data:
        logging.error("Invalid video_command request")
        return jsonify({"error": "session_id and start_or_stop required"}), 400

    session_id = data.get('session_id')
    start_or_stop = data.get('start_or_stop', None)
    move_to = data.get('move_to', None)   # Testing

    if move_to is None and start_or_stop is None:
        logging.error("Invalid video_command request: both start_or_stop and move_to are None")
        return jsonify({"error": "start_or_stop or move_to required"}), 400

    command_payload = {
        'session_id': session_id,
        'start_or_stop': start_or_stop,
        'move_to': move_to   # Testing
    }

    logging.info(f"Video command for {session_id}: {'Start' if start_or_stop else 'Stop'}")

    redis_client.set(f'video_command:{session_id}', json.dumps(command_payload))
    video_command_store[session_id] = command_payload

    return jsonify({"message": "Command stored"}), 201


@app.route('/get_video_command/<session_id>', methods=['GET'])
def get_video_command(session_id):
    command = redis_client.get(f'video_command:{session_id}')
    if command:
        return jsonify(json.loads(command)), 200
    if session_id in video_command_store:
        return jsonify(video_command_store[session_id]), 200
    logging.warning(f"Command not found for {session_id}")
    return jsonify({}), 200


@app.route('/post_session_id', methods=['POST'])
def post_session_id():
    data = request.get_json()
    session_id = data.get('session_id')

    global session_id_store
    if session_id is None:
        redis_client.delete('current_session_id')
        session_id_store = None
        logging.info("Session ID cleared")
        return jsonify({"message": "Session ID cleared"}), 201
    else:
        redis_client.set('current_session_id', str(session_id))
        session_id_store = session_id
        logging.info(f"Session ID set to {session_id}")

        # #------------- Set default intro image message for the new/updated session_id ------------
        # default_image_path = 'images/eHealth_12Domains.png'  # Default image for eHealth 12 Domains Intro
        # base64_img = get_base64_image(default_image_path)  

        message_payload = {
            'session_id': session_id,
            'type': 'image',
            # 'message': base64_img
            'message': "intro_page"
        }
        redis_client.set(f'message:{session_id}', json.dumps(message_payload))
        data_store[session_id] = message_payload
        logging.info(f"Default intro image stored for {session_id}")
        # # -----------------------------------------------------------------------------------------

        return jsonify({"message": "Session ID set"}), 201


@app.route('/get_session_id', methods=['GET'])
def get_session_id():
    sid = redis_client.get('current_session_id') or session_id_store
    return jsonify({"session_id": sid}), 200




## Video Control API
def get_video_timestamp(session_id):
    pass

def post_video_timestamp(session_id, timestamp):
    pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)