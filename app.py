# pylint: disable = invalid-name
import os
import uuid
import datetime
import re
import json

from langchain_core.messages import HumanMessage

from agents.agent import Agent
from agents.utils.env_utils import get_env_var

from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

class TravelAgentBackend:
    """Backend-only Fly Buddy"""
    
    def __init__(self):
        self.agent = None
        self.initialize_agent()
    
    def initialize_agent(self):
        """Initialize the AI agent"""
        if not self.agent:
            self.agent = Agent()
    
    def clean_html_content(self, content):
        """Remove all HTML tags including pre tags and their content"""
        if not content:
            return content
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove pre tags
        for pre in soup.find_all('pre'):
            pre.decompose()
            
        # Get text
        text = soup.get_text()
        
        # Remove code blocks (triple backticks)
        text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
        
        # Remove single backticks
        text = re.sub(r'`[^`]*`', '', text)
        
        return text.strip()
    
    def parse_hotel_data(self, hotel_data):
        """Parse individual hotel data and return structured information"""
        def clean_html(text):
            """Remove HTML tags and clean text content"""
            if not text:
                return ""
            
            text_str = str(text)
            
            # Remove all HTML tags
            clean_text = re.sub(r'<[^>]*>', '', text_str)
            
            # Remove HTML entities
            clean_text = re.sub(r'&nbsp;', ' ', clean_text)
            clean_text = re.sub(r'&amp;', '&', clean_text)
            clean_text = re.sub(r'&lt;', '<', clean_text)
            clean_text = re.sub(r'&gt;', '>', clean_text)
            clean_text = re.sub(r'&quot;', '"', clean_text)
            clean_text = re.sub(r'&#39;', "'", clean_text)
            clean_text = re.sub(r'&[a-zA-Z0-9#]+;', '', clean_text)
            
            # Remove extra whitespace
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            return clean_text
        
        try:
            # Extract hotel information
            name = clean_html(hotel_data.get('name', 'Unknown Hotel'))
            location = clean_html(hotel_data.get('location', 'Unknown Location'))
            rating = clean_html(hotel_data.get('overall_rating', 'No rating'))
            reviews = clean_html(hotel_data.get('reviews', 'No reviews'))
            
            # Price information
            rate_info = hotel_data.get('rate_per_night', {})
            price = clean_html(rate_info.get('lowest', 'Price not available'))
            price_currency = clean_html(rate_info.get('currency', ''))
            
            # Additional details
            hotel_class = clean_html(hotel_data.get('hotel_class', 'Not specified'))
            property_type = clean_html(hotel_data.get('type', 'Hotel'))
            distance = clean_html(hotel_data.get('distance_from_search_location', ''))
            
            # Amenities
            amenities = hotel_data.get('amenities', [])
            top_amenities = [clean_html(amenity) for amenity in amenities[:4]] if amenities else []
            
            # Images and link
            images = hotel_data.get('images', [])
            main_image = images[0] if images else ''
            link = hotel_data.get('link', '')
            
            return {
                'name': name,
                'location': location,
                'rating': rating,
                'reviews': reviews,
                'price': price,
                'currency': price_currency,
                'hotel_class': hotel_class,
                'property_type': property_type,
                'distance': distance,
                'amenities': top_amenities,
                'image': main_image,
                'link': link
            }
        except Exception as e:
            return {
                'name': 'Hotel Option',
                'location': 'Hotel details',
                'error': str(e)
            }
    
    def parse_flight_data(self, flight_data):
        """Parse individual flight data and return structured information"""
        try:
            # Handle different data structures (real API vs sample data)
            if 'flights' in flight_data:
                # Sample data structure with nested flights array
                flight_info = flight_data['flights'][0] if flight_data['flights'] else {}
                price = f"${flight_data.get('price', 'N/A')}"
            else:
                # Real SerpAPI structure
                flight_info = flight_data
                price = flight_data.get('price', 'Price not available')
            
            # Extract basic flight information
            departure_airport = flight_info.get('departure_airport', {})
            arrival_airport = flight_info.get('arrival_airport', {})
            
            departure_code = departure_airport.get('id', 'Unknown')
            departure_name = departure_airport.get('name', 'Unknown Airport')
            arrival_code = arrival_airport.get('id', 'Unknown')
            arrival_name = arrival_airport.get('name', 'Unknown Airport')
            
            # Flight details
            airline = flight_info.get('airline', 'Unknown Airline')
            flight_number = flight_info.get('flight_number', 'Unknown')
            departure_time = flight_info.get('departure_time', 'Unknown')
            arrival_time = flight_info.get('arrival_time', 'Unknown')
            duration = flight_info.get('duration', 'Unknown')
            
            # Additional details
            aircraft = flight_info.get('aircraft', 'Unknown')
            stops = flight_info.get('stops', 0)
            
            flight_data = {
                'airline': airline,
                'flightNumber': flight_number,
                'departure': {
                    'airport': f"{departure_code} - {departure_name}",
                    'time': departure_time
                },
                'arrival': {
                    'airport': f"{arrival_code} - {arrival_name}",
                    'time': arrival_time
                },
                'duration': duration,
                'price': price,
                'aircraft': aircraft,
                'stops': stops,
                'details': f"Aircraft: {aircraft}, Stops: {stops}"
            }
            return flight_data
        except Exception as e:
            return {
                'airline': 'Flight Option',
                'error': str(e)
            }
    
    def process_query(self, user_input):
        """Process a travel query and return structured results"""
        if not user_input:
            return {'error': 'Please provide a travel query.'}
        
        try:
            thread_id = str(uuid.uuid4())
            messages = [HumanMessage(content=user_input)]
            config = {'configurable': {'thread_id': thread_id}}

            result = self.agent.graph.invoke({'messages': messages}, config=config)
            
            # Clean non-tool message content
            if 'messages' in result:
                for message in result['messages']:
                    if hasattr(message, 'content'):
                        # Preserve tool outputs for parsing
                        if hasattr(message, 'name') and message.name in ('flights_finder', 'hotels_finder'):
                            continue
                        message.content = self.clean_html_content(str(message.content))

            # Extract structured data
            flights_data = []
            hotels_data = []
            response_text = ""
            
            # Look for tool messages and regular responses
            for message in result['messages']:
                if hasattr(message, 'name') and hasattr(message, 'content'):
                    if message.name == 'flights_finder':
                        try:
                            if isinstance(message.content, list):
                                flights_data = message.content
                            else:
                                flights_data = json.loads(str(message.content))
                        except Exception:
                            pass
                    elif message.name == 'hotels_finder':
                        try:
                            if isinstance(message.content, list):
                                hotels_data = message.content
                            else:
                                hotels_data = json.loads(str(message.content))
                        except Exception:
                            pass
                elif hasattr(message, 'content'):
                    # Check if this is an AI response (not a tool message or human message)
                    message_type = type(message).__name__
                    if message_type == 'AIMessage' or (not hasattr(message, 'name') and message_type != 'HumanMessage'):
                        content = str(message.content).strip()
                        if content and content not in response_text:
                            response_text += content + "\n"

            # Parse the structured data
            parsed_flights = []
            parsed_hotels = []
            
            if flights_data and isinstance(flights_data, list):
                parsed_flights = [self.parse_flight_data(flight) for flight in flights_data[:6]]
            
            if hotels_data and isinstance(hotels_data, list):
                parsed_hotels = [self.parse_hotel_data(hotel) for hotel in hotels_data[:6]]

            # Generate response text if none was provided by the AI
            if not response_text.strip():
                if parsed_flights and parsed_hotels:
                    # Create detailed response with flight and hotel information
                    flight_summary = f"✈️ **Flight Options ({len(parsed_flights)} found):**\n"
                    for i, flight in enumerate(parsed_flights[:3], 1):
                        airline = flight.get('airline', 'Unknown')
                        price = flight.get('price', 'N/A')
                        duration = flight.get('duration', 'N/A')
                        flight_summary += f"{i}. {airline} - {price} ({duration})\n"
                    
                    hotel_summary = f"\n🏨 **Hotel Options ({len(parsed_hotels)} found):**\n"
                    for i, hotel in enumerate(parsed_hotels[:3], 1):
                        name = hotel.get('name', 'Unknown Hotel')
                        price = hotel.get('price', 'N/A')
                        rating = hotel.get('rating', 'N/A')
                        hotel_summary += f"{i}. {name} - {price}/night (⭐{rating})\n"
                    
                    response_text = f"I found great travel options for you!\n\n{flight_summary}{hotel_summary}\nWould you like more details about any of these options?"
                    
                elif parsed_flights:
                    flight_summary = f"✈️ **Flight Options ({len(parsed_flights)} found):**\n"
                    for i, flight in enumerate(parsed_flights[:3], 1):
                        airline = flight.get('airline', 'Unknown')
                        price = flight.get('price', 'N/A')
                        duration = flight.get('duration', 'N/A')
                        departure = flight.get('departure', {}).get('time', 'N/A')
                        arrival = flight.get('arrival', {}).get('time', 'N/A')
                        flight_summary += f"{i}. {airline} - {price}\n   Departure: {departure} | Arrival: {arrival} | Duration: {duration}\n"
                    
                    response_text = f"I found {len(parsed_flights)} flight options for your trip:\n\n{flight_summary}\nWould you like me to search for hotels as well?"
                    
                elif parsed_hotels:
                    hotel_summary = f"🏨 **Hotel Options ({len(parsed_hotels)} found):**\n"
                    for i, hotel in enumerate(parsed_hotels[:3], 1):
                        name = hotel.get('name', 'Unknown Hotel')
                        price = hotel.get('price', 'N/A')
                        rating = hotel.get('rating', 'N/A')
                        location = hotel.get('location', 'N/A')
                        hotel_summary += f"{i}. {name} - {price}/night\n   Rating: ⭐{rating} | Location: {location}\n"
                    
                    response_text = f"I found {len(parsed_hotels)} hotel options for your stay:\n\n{hotel_summary}\nWould you like me to search for flights as well?"
                else:
                    response_text = "I've processed your travel request. Let me help you find the best options for your trip."

            return {
                'success': True,
                'response_text': response_text.strip(),
                'flights': parsed_flights,
                'hotels': parsed_hotels,
                'thread_id': thread_id
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_environment(self):
        """Check if required environment variables are set"""
        missing_env = []
        if not get_env_var('SERPAPI_API_KEY'):
            missing_env.append('SERPAPI_API_KEY')
        if not get_env_var('GOOGLE_API_KEY'):
            missing_env.append('GOOGLE_API_KEY')
        
        return {
            'missing_variables': missing_env,
            'is_configured': len(missing_env) == 0
        }


def main():
    """Main function for backend usage"""
    # Initialize the backend
    backend = TravelAgentBackend()
    
    # Check environment
    env_status = backend.check_environment()
    if not env_status['is_configured']:
        print(f"Warning: Missing environment variables: {', '.join(env_status['missing_variables'])}")
        print("Please set them in your .env file or environment.")
    
    # Example usage
    print("Fly Buddy Backend initialized successfully!")
    print("Use backend.process_query('your travel request') to get results.")
    
    return backend


if __name__ == '__main__':
    travel_backend = main()
    
    # Example query for testing
    example_query = "Find flights from New York to Paris for next week"
    print(f"\nExample query: {example_query}")
    result = travel_backend.process_query(example_query)
    print(f"Result: {result}")
