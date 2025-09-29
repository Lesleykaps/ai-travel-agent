#!/usr/bin/env python3
"""
Fly Buddy API Server
Provides REST API endpoints for the frontend to communicate with the backend service.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
import logging
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the backend service
try:
    from app import TravelAgentBackend
except ImportError as e:
    print(f"Warning: Could not import TravelAgentBackend: {e}")
    TravelAgentBackend = None

# Configure logging for production
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # Add file handler for production
        logging.FileHandler('api_server.log') if os.getenv('LOG_TO_FILE', 'False').lower() == 'true' else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize the backend service
backend = None
if TravelAgentBackend:
    try:
        backend = TravelAgentBackend()
        logger.info("TravelAgentBackend initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize TravelAgentBackend: {e}")
        backend = None
else:
    logger.warning("TravelAgentBackend not available, using mock responses")

class MockBackend:
    """Mock backend for testing when the real backend is not available"""
    
    def process_query(self, query):
        """Mock query processing"""
        time.sleep(1)  # Simulate processing time
        
        # Generate contextual responses based on query content
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['flight', 'fly', 'airline', 'airport']):
            return {
                'response': f"I found several flight options for your request. Here are some great deals:\n\n✈️ **Flight Options:**\n- Delta Airlines: $299 (Direct flight)\n- American Airlines: $275 (1 stop)\n- United Airlines: $320 (Direct flight)\n\nWould you like me to help you book one of these flights or search for different dates?",
                'type': 'flight_search',
                'data': {
                    'flights': [
                        {'airline': 'Delta', 'price': 299, 'type': 'Direct'},
                        {'airline': 'American', 'price': 275, 'type': '1 stop'},
                        {'airline': 'United', 'price': 320, 'type': 'Direct'}
                    ]
                }
            }
        elif any(word in query_lower for word in ['hotel', 'accommodation', 'stay', 'room']):
            return {
                'response': f"I found some excellent hotel options for you:\n\n🏨 **Hotel Recommendations:**\n- Grand Plaza Hotel: $150/night (4.5⭐)\n- City Center Inn: $89/night (4.2⭐)\n- Luxury Resort & Spa: $280/night (4.8⭐)\n\nAll hotels include free WiFi and breakfast. Would you like more details about any of these options?",
                'type': 'hotel_search',
                'data': {
                    'hotels': [
                        {'name': 'Grand Plaza Hotel', 'price': 150, 'rating': 4.5},
                        {'name': 'City Center Inn', 'price': 89, 'rating': 4.2},
                        {'name': 'Luxury Resort & Spa', 'price': 280, 'rating': 4.8}
                    ]
                }
            }
        elif any(word in query_lower for word in ['itinerary', 'plan', 'schedule', 'trip']):
            return {
                'response': f"I'd be happy to help you plan your trip! Here's a suggested itinerary:\n\n📅 **3-Day Itinerary:**\n\n**Day 1:** Arrival & City Exploration\n- Check into hotel\n- Visit downtown area\n- Dinner at local restaurant\n\n**Day 2:** Main Attractions\n- Morning: Museum tour\n- Afternoon: Scenic viewpoint\n- Evening: Cultural show\n\n**Day 3:** Departure\n- Last-minute shopping\n- Airport transfer\n\nWould you like me to customize this itinerary based on your specific interests?",
                'type': 'itinerary_planning'
            }
        elif any(word in query_lower for word in ['destination', 'where', 'recommend', 'suggest']):
            return {
                'response': f"Based on current trends and seasonal considerations, here are some amazing destinations I'd recommend:\n\n🌍 **Top Destinations:**\n\n🏖️ **Beach Destinations:**\n- Maldives (Perfect for relaxation)\n- Bali, Indonesia (Culture + beaches)\n- Santorini, Greece (Romantic getaway)\n\n🏔️ **Adventure Destinations:**\n- Swiss Alps (Hiking & skiing)\n- New Zealand (Outdoor activities)\n- Costa Rica (Wildlife & nature)\n\n🏛️ **Cultural Destinations:**\n- Kyoto, Japan (Traditional culture)\n- Rome, Italy (Historical sites)\n- Istanbul, Turkey (East meets West)\n\nWhat type of experience are you looking for?",
                'type': 'destination_recommendation'
            }
        else:
            return {
                'response': f"Thank you for your question! I'm here to help you with all your travel needs. I can assist you with:\n\n✈️ **Flight bookings** - Find the best deals and routes\n🏨 **Hotel reservations** - Discover perfect accommodations\n📅 **Trip planning** - Create detailed itineraries\n🌍 **Destination advice** - Get personalized recommendations\n💰 **Budget planning** - Optimize your travel expenses\n📋 **Travel tips** - Essential information for your journey\n\nWhat specific aspect of your travel would you like help with?",
                'type': 'general_assistance'
            }

# Initialize mock backend if real backend is not available
if not backend:
    backend = MockBackend()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'backend_available': isinstance(backend, TravelAgentBackend) if TravelAgentBackend else False
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint for processing user messages"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message'].strip()
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        logger.info(f"Processing message: {user_message[:100]}...")
        
        # Process the message with the backend
        start_time = time.time()
        
        if isinstance(backend, TravelAgentBackend):
            # Use real backend
            try:
                result = backend.process_query(user_message)
                if result.get('success', False):
                    response_text = result.get('response_text', 'I found some information for you!')
                    response_data = {
                        'flights': result.get('flights', []),
                        'hotels': result.get('hotels', []),
                        'thread_id': result.get('thread_id')
                    }
                    # Determine response type based on data
                    if result.get('flights') and result.get('hotels'):
                        response_type = 'travel_search'
                    elif result.get('flights'):
                        response_type = 'flight_search'
                    elif result.get('hotels'):
                        response_type = 'hotel_search'
                    else:
                        response_type = 'general'
                else:
                    logger.error(f"Backend processing failed: {result.get('error', 'Unknown error')}")
                    response_text = "I apologize, but I encountered an issue processing your request."
                    response_data = {}
                    response_type = 'error'
            except Exception as e:
                logger.error(f"Backend processing error: {e}")
                response_text = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment."
                response_data = {}
                response_type = 'error'
        else:
            # Use mock backend
            result = backend.process_query(user_message)
            response_text = result['response']
            response_data = result.get('data', {})
            response_type = result.get('type', 'general')
        
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Generate suggested follow-up questions based on response type
        suggestions = generate_suggestions(response_type, user_message)
        
        response = {
            'message': response_text,
            'type': response_type,
            'data': response_data,
            'suggestions': suggestions,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'processing_time': round(processing_time, 2),
                'backend_type': 'real' if isinstance(backend, TravelAgentBackend) else 'mock'
            }
        }
        
        logger.info(f"Response generated in {processing_time:.2f}ms")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'I apologize, but I encountered an unexpected error. Please try again.'
        }), 500

def generate_suggestions(response_type, user_message):
    """Generate contextual follow-up suggestions"""
    suggestions_map = {
        'flight_search': [
            "Show me hotels in the same area",
            "What's the baggage policy for these airlines?",
            "Can you find flights for different dates?",
            "Tell me about airport transportation options"
        ],
        'hotel_search': [
            "Find flights to this destination",
            "What are the local attractions nearby?",
            "Show me restaurant recommendations",
            "What's the cancellation policy?"
        ],
        'itinerary_planning': [
            "Find flights for these dates",
            "Recommend hotels for this itinerary",
            "What's the weather like during this time?",
            "Suggest local restaurants and activities"
        ],
        'destination_recommendation': [
            "Tell me more about [destination name]",
            "What's the best time to visit?",
            "Find flights to these destinations",
            "What's the average cost for this trip?"
        ],
        'general_assistance': [
            "Help me plan a weekend getaway",
            "Find flights for my next business trip",
            "Recommend family-friendly destinations",
            "What are the current travel restrictions?"
        ],
        'error': [
            "Try asking about flights",
            "Ask for hotel recommendations",
            "Request destination suggestions",
            "Get help with trip planning"
        ]
    }
    
    base_suggestions = suggestions_map.get(response_type, suggestions_map['general_assistance'])
    
    # Return 3 random suggestions
    import random
    return random.sample(base_suggestions, min(3, len(base_suggestions)))



@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.get_json()
        feedback_type = data.get('type', 'general')
        message = data.get('message', '')
        rating = data.get('rating')
        
        # Log feedback (in a real implementation, this would be saved to a database)
        logger.info(f"Feedback received - Type: {feedback_type}, Rating: {rating}, Message: {message[:100]}...")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback!'
        })
        
    except Exception as e:
        logger.error(f"Feedback endpoint error: {e}")
        return jsonify({'error': 'Failed to submit feedback'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Get environment configuration
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5001))
    host = os.getenv('HOST', '0.0.0.0')
    
    print("🚀 Starting Fly Buddy API Server...")
    print(f"📡 Backend service: {'Available' if isinstance(backend, TravelAgentBackend) else 'Mock mode'}")
    print(f"🌐 Server will be available at: http://{host}:{port}")
    print(f"🔧 Debug mode: {'Enabled' if debug_mode else 'Disabled (Production)'}")
    print("📋 API endpoints:")
    print("   - GET  /api/health - Health check")
    print("   - POST /api/chat - Send chat messages")
    print("   - POST /api/feedback - Submit feedback")
    print("\n✨ Ready to serve requests!")
    
    # Production-optimized configuration
    app.run(
        host=host, 
        port=port, 
        debug=debug_mode,
        threaded=True,  # Enable threading for better performance
        use_reloader=debug_mode  # Only use reloader in debug mode
    )