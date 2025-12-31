"""
AI Emotion Detection System - Backend Server
Uses DeepFace library for real-time facial emotion recognition
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import base64
from deepface import DeepFace
import logging
from datetime import datetime
import traceback
import os

app = Flask(__name__)
CORS(app)

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Emotion metadata for enhanced responses
EMOTION_DATA = {
    'happy': {
        'color': '#FFD700',
        'description': 'Positive emotional state',
        'intensity': 'high'
    },
    'sad': {
        'color': '#4A90E2',
        'description': 'Melancholic emotional state',
        'intensity': 'medium'
    },
    'angry': {
        'color': '#FF4757',
        'description': 'Aggressive emotional state',
        'intensity': 'high'
    },
    'surprise': {
        'color': '#FFA502',
        'description': 'Startled emotional state',
        'intensity': 'high'
    },
    'fear': {
        'color': '#A55EEA',
        'description': 'Anxious emotional state',
        'intensity': 'medium'
    },
    'disgust': {
        'color': '#26DE81',
        'description': 'Aversive emotional state',
        'intensity': 'medium'
    },
    'neutral': {
        'color': '#778CA3',
        'description': 'Calm emotional state',
        'intensity': 'low'
    }
}

@app.route('/')
def index():
    """Serve the main interface"""
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/api/detect', methods=['POST'])
def detect_emotion():
    """
    Analyze facial emotions from base64 encoded image
    Returns emotion probabilities and dominant emotion
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'No image data provided'
            }), 400
        
        # Decode base64 image
        try:
            image_data = data['image'].split(',')[1]
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValueError("Failed to decode image")
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Image decoding failed: {str(e)}'
            }), 400
        
        # Perform emotion analysis
        logger.info("Analyzing emotions...")
        
        try:
            result = DeepFace.analyze(
                img_path=img,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv'
            )
        except Exception as e:
            logger.error(f"DeepFace analysis failed: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Emotion analysis failed: {str(e)}',
                'face_detected': False
            }), 500
        
        # Handle both single and multiple face results
        if isinstance(result, list):
            result = result[0]
        
        emotions = result['emotion']
        dominant = result['dominant_emotion']
        
        # Convert NumPy types to Python native types for JSON serialization
        emotions_dict = {k: float(round(v, 2)) for k, v in emotions.items()}
        confidence = float(round(emotions[dominant], 2))
        
        # Enrich response with metadata
        response = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'dominant_emotion': str(dominant),
            'confidence': confidence,
            'emotions': emotions_dict,
            'metadata': EMOTION_DATA.get(dominant, {}),
            'face_detected': True
        }
        
        logger.info(f"✓ Detected: {dominant} ({emotions[dominant]:.1f}%)")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e),
            'face_detected': False
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'operational',
        'service': 'emotion-detection-api',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🧠 AI EMOTION DETECTION SYSTEM")
    print("="*70)
    print("\n🚀 Server Status: INITIALIZING")
    print("📡 Endpoint: http://localhost:5000")
    print("🔬 AI Model: DeepFace (Multi-task CNN)")
    print("🎯 Detection: 7 Emotion Categories")
    print("\n💡 TIP: Allow camera access when prompted by your browser")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)