#!/usr/bin/env python3
"""
Elephant AI Backend API Server (Python/Flask)
Uses GROQ for NL2SQL query generation
"""

import sys
from pathlib import Path

# Add parent directory to path for groq_client import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, request, jsonify
from flask_cors import CORS
from groq_client import GroqClient, CompletionConfig, Temperature
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Load system prompt
SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / 'prompts' / 'candidates_nl2sql_system_prompt.txt'
try:
    with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
        SYSTEM_PROMPT = f.read()
    print('[OK] System prompt loaded successfully')
except Exception as e:
    print(f'[ERROR] Failed to load system prompt: {e}')
    sys.exit(1)

# Initialize GROQ client
try:
    groq_client = GroqClient()
    print('[OK] GROQ client initialized successfully')
except Exception as e:
    print(f'[ERROR] Failed to initialize GROQ client: {e}')
    sys.exit(1)

# In-memory conversation storage
conversations = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Elephant AI Backend (Python)',
        'groq': True,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        session_id = data.get('sessionId', 'default')
        use_history = data.get('useHistory', True)

        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400

        print(f'[{datetime.utcnow().isoformat()}] Chat request:', {
            'sessionId': session_id,
            'message': message[:100],
            'useHistory': use_history
        })

        # Get or create conversation history
        if session_id not in conversations:
            conversations[session_id] = []

        # Use conversation history if enabled
        conversation_id = session_id if use_history else None

        # Call GROQ with system prompt
        start_time = datetime.now()

        config = CompletionConfig(
            model='llama-3.3-70b-versatile',
            temperature=Temperature.CONSERVATIVE.value,  # 0.3 for consistent SQL
            max_tokens=2000,
            top_p=0.9
        )

        response = groq_client.complete(
            prompt=message,
            system_prompt=SYSTEM_PROMPT,
            config=config,
            conversation_id=conversation_id
        )

        response_time = int((datetime.now() - start_time).total_seconds() * 1000)

        print(f'[{datetime.utcnow().isoformat()}] Response generated in {response_time}ms')

        # Return response
        return jsonify({
            'success': True,
            'message': response.content,
            'metadata': {
                'model': response.model,
                'tokens': response.usage,
                'responseTime': response_time,
                'sessionId': session_id,
                'historyLength': len(groq_client.get_conversation_history(session_id)) if conversation_id else 0
            }
        })

    except Exception as e:
        print(f'Chat endpoint error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to process chat request',
            'details': str(e)
        }), 500

@app.route('/api/chat/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history"""
    data = request.json
    session_id = data.get('sessionId', 'default')

    groq_client.clear_conversation(session_id)

    print(f'Cleared conversation history for session: {session_id}')

    return jsonify({
        'success': True,
        'message': 'Conversation history cleared',
        'sessionId': session_id
    })

@app.route('/api/chat/stats', methods=['GET'])
def get_stats():
    """Get conversation statistics"""
    stats = {
        'totalSessions': len(conversations),
        'sessions': [
            {
                'sessionId': sid,
                'messageCount': len(groq_client.get_conversation_history(sid)),
                'lastActivity': datetime.utcnow().isoformat()
            }
            for sid in conversations.keys()
        ]
    }

    return jsonify(stats)

if __name__ == '__main__':
    PORT = int(os.getenv('BACKEND_PORT', 3001))

    print('')
    print('=' * 60)
    print('')
    print('        ELEPHANT AI BACKEND SERVER RUNNING')
    print('                 (Python/Flask)')
    print('')
    print('=' * 60)
    print('')
    print(f'  [OK] Server:      http://localhost:{PORT}')
    print(f'  [OK] Health:      http://localhost:{PORT}/health')
    print(f'  [OK] Chat API:    POST http://localhost:{PORT}/api/chat')
    print('  [OK] GROQ Model:  llama-3.3-70b-versatile')
    print('  [OK] System Prompt: NL2SQL for candidates database')
    print('')
    print('  Ready to process queries!')
    print('')

    app.run(host='0.0.0.0', port=PORT, debug=False)
