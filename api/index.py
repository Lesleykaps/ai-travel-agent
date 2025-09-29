#!/usr/bin/env python3
"""
Vercel Serverless Function for AI Travel Agent
Handles all API requests in a serverless environment
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
import logging
import os
import sys
from datetime import datetime

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the backend service
try:
    from app import TravelAgentBackend
    logger.info("Successfully imported TravelAgentBackend")
except ImportError as e:
    logger.warning(f"Could not import TravelAgentBackend: {e}")
    TravelAgentBackend = None
except Exception as e:
    logger.error(f"Unexpected error importing TravelAgentBackend: {e}")
    TravelAgentBackend = None

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize backend (will be created on first request to handle cold starts)
backend = None

def get_backend():
    """Get or create backend instance"""
    global backend
    if backend is None:
        if TravelAgentBackend:
            try:
                logger.info("Attempting to initialize TravelAgentBackend...")
                backend = TravelAgentBackend()
                logger.info("TravelAgentBackend initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize TravelAgentBackend: {e}")
                logger.info("Falling back to MockBackend")
                backend = MockBackend()
        else:
            logger.info("TravelAgentBackend not available, using MockBackend")
            backend = MockBackend()
    return backend

class MockBackend:
    """Mock backend for when the real backend is not available"""
    
    def process_query(self, message):
        """Process user query with mock responses"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['flight', 'fly', 'plane', 'ticket', 'airport']):
            return {
                'success': True,
                'response_text': "I'd be happy to help you find flights! To provide you with the best options, I'll need a few details:\n\n✈️ **Flight Search:**\n- Departure city/airport\n- Destination city/airport\n- Departure date\n- Return date (if round trip)\n- Number of passengers\n- Preferred class (Economy, Business, First)\n\nPlease share these details and I'll find the best flight options for you!",
                'flights': [],
                'hotels': [],
                'thread_id': f"mock_thread_{int(time.time())}"
            }
        elif any(word in message_lower for word in ['hotel', 'accommodation', 'stay', 'room', 'booking']):
            return {
                'success': True,
                'response_text': "I'll help you find the perfect accommodation! To get started, please provide:\n\n🏨 **Hotel Search:**\n- Destination city\n- Check-in date\n- Check-out date\n- Number of guests\n- Number of rooms\n- Preferred amenities (pool, gym, spa, etc.)\n- Budget range\n\nShare these details and I'll find great hotel options for you!",
                'flights': [],
                'hotels': [],
                'thread_id': f"mock_thread_{int(time.time())}"
            }
        elif any(word in message_lower for word in ['destination', 'where', 'recommend', 'suggest', 'travel']):
            return {
                'success': True,
                'response_text': "Based on current trends and seasonal considerations, here are some amazing destinations I'd recommend:\n\n🌍 **Top Destinations:**\n\n🏖️ **Beach Destinations:**\n- Maldives (Perfect for relaxation)\n- Bali, Indonesia (Culture + beaches)\n- Santorini, Greece (Romantic getaway)\n\n🏔️ **Adventure Destinations:**\n- Swiss Alps (Hiking & skiing)\n- New Zealand (Outdoor activities)\n- Costa Rica (Wildlife & nature)\n\n🏛️ **Cultural Destinations:**\n- Kyoto, Japan (Traditional culture)\n- Rome, Italy (Historical sites)\n- Istanbul, Turkey (East meets West)\n\nWhat type of experience are you looking for?",
                'flights': [],
                'hotels': [],
                'thread_id': f"mock_thread_{int(time.time())}"
            }
        else:
            return {
                'success': True,
                'response_text': "Thank you for your question! I'm here to help you with all your travel needs. I can assist you with:\n\n✈️ **Flight bookings** - Find the best deals and routes\n🏨 **Hotel reservations** - Discover perfect accommodations\n📅 **Trip planning** - Create detailed itineraries\n🌍 **Destination advice** - Get personalized recommendations\n💰 **Budget planning** - Optimize your travel expenses\n📋 **Travel tips** - Essential information for your journey\n\nWhat specific aspect of your travel would you like help with?",
                'flights': [],
                'hotels': [],
                'thread_id': f"mock_thread_{int(time.time())}"
            }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'backend_available': TravelAgentBackend is not None,
        'environment': 'vercel'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint for processing user messages"""
    try:
        logger.info("Chat endpoint called")
        
        data = request.get_json()
        logger.info(f"Request data received: {data is not None}")
        
        if not data or 'message' not in data:
            logger.warning("Invalid request: missing message")
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            logger.warning("Empty message received")
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        logger.info(f"Processing message: {user_message[:100]}...")
        
        # Get backend instance
        try:
            backend_instance = get_backend()
            logger.info(f"Backend instance obtained: {type(backend_instance).__name__}")
        except Exception as e:
            logger.error(f"Failed to get backend instance: {e}")
            raise
        
        # Process the message
        start_time = time.time()
        try:
            result = backend_instance.process_query(user_message)
            logger.info(f"Backend processing completed: {result.get('success', False)}")
        except Exception as e:
            logger.error(f"Backend processing failed: {e}")
            raise
        processing_time = time.time() - start_time
        
        if result.get('success', False):
            response = {
                'response': result.get('response_text', 'I found some information for you!'),
                'data': {
                    'flights': result.get('flights', []),
                    'hotels': result.get('hotels', []),
                    'thread_id': result.get('thread_id')
                },
                'processing_time': round(processing_time, 2),
                'timestamp': datetime.now().isoformat()
            }
            logger.info(f"Successfully processed message in {processing_time:.2f}s")
            return jsonify(response)
        else:
            error_msg = result.get('error', 'Failed to process your request')
            logger.error(f"Backend processing failed: {error_msg}")
            return jsonify({
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/feedback', methods=['POST'])
def feedback():
    """Feedback endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Feedback data is required'}), 400
        
        # Log feedback (in production, you'd save to database)
        logger.info(f"Feedback received: {json.dumps(data, indent=2)}")
        
        return jsonify({
            'message': 'Thank you for your feedback!',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in feedback endpoint: {str(e)}")
        return jsonify({
            'error': 'Failed to process feedback',
            'timestamp': datetime.now().isoformat()
        }), 500

# Vercel serverless function handler
def handler(request):
    """Main handler for Vercel serverless function"""
    return app(request.environ, lambda status, headers: None)

# For local testing
if __name__ == '__main__':
    app.run(debug=True, port=5001)