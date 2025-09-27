# pylint: disable = invalid-name
import os
import uuid
import datetime
import re
import json

import streamlit as st
from langchain_core.messages import HumanMessage

from agents.agent import Agent
from utils import get_env_var

from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()
 
def clean_html_content(content):
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





def initialize_agent():
    if 'agent' not in st.session_state:
        st.session_state.agent = Agent()


def render_weather_widget():
    """Render a modern weather widget"""
    # Get current time for demo weather
    current_hour = datetime.datetime.now(datetime.timezone.utc).hour
    
    # Simple weather logic based on time
    if 6 <= current_hour < 12:
        weather_icon = "☀️"
        weather_desc = "Sunny"
        temp = "22°C"
    elif 12 <= current_hour < 18:
        weather_icon = "⛅"
        weather_desc = "Partly Cloudy"
        temp = "25°C"
    elif 18 <= current_hour < 22:
        weather_icon = "🌤️"
        weather_desc = "Clear"
        temp = "20°C"
    else:
        weather_icon = "🌙"
        weather_desc = "Clear Night"
        temp = "16°C"
    
    # Weather widget HTML
    weather_html = f"""
    <div style="
        position: absolute;
        top: 20px;
        right: 20px;
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 16px 20px;
        backdrop-filter: blur(20px);
        box-shadow: var(--shadow-lg);
        z-index: 20;
        min-width: 140px;
        text-align: center;
    ">
        <div style="font-size: 32px; margin-bottom: 8px;">{weather_icon}</div>
        <div style="font-size: 24px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">{temp}</div>
        <div style="font-size: 14px; color: var(--text-secondary); font-weight: 500;">{weather_desc}</div>
        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Local Weather</div>
    </div>
    """
    
    st.markdown(weather_html, unsafe_allow_html=True)


def render_recent_chats_widget():
    """Render recent chats widget"""
    recent_chats = [
        {"title": "Trip to Paris", "time": "2 hours ago"},
        {"title": "Weekend in Rome", "time": "1 day ago"},
        {"title": "Business trip NYC", "time": "3 days ago"}
    ]
    
    recent_html = """
    <div style="
        position: absolute;
        bottom: 40px;
        left: 20px;
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(20px);
        box-shadow: var(--shadow-lg);
        z-index: 20;
        min-width: 280px;
        max-width: 320px;
    ">
        <div style="
            font-size: 16px; 
            font-weight: 600; 
            color: var(--text-primary); 
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        ">
            <span>💬</span>
            Your recent chats
        </div>
    """
    
    for chat in recent_chats:
        recent_html += f"""
        <div style="
            padding: 12px 0;
            border-bottom: 1px solid var(--card-border);
            cursor: pointer;
            transition: all 0.2s ease;
        " onmouseover="this.style.backgroundColor='var(--chip-bg)'" onmouseout="this.style.backgroundColor='transparent'">
            <div style="font-size: 14px; font-weight: 500; color: var(--text-secondary); margin-bottom: 4px;">
                {chat['title']}
            </div>
            <div style="font-size: 12px; color: var(--text-muted);">
                {chat['time']}
            </div>
        </div>
        """
    
    recent_html += "</div>"
    st.markdown(recent_html, unsafe_allow_html=True)


def render_custom_css():
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def _time_of_day():
    """Get time of day greeting based on current hour"""
    try:
        # Use timezone-aware UTC time for consistent behavior on Streamlit Cloud
        hour = datetime.datetime.now(datetime.timezone.utc).hour
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        else:
            return 'evening'
    except Exception:
        # Fallback to a default greeting if there's any issue
        return 'day'


def render_ui():
    # Main container with modern layout
    st.markdown('<div class="app-wrap">', unsafe_allow_html=True)
    
    # Render weather widget
    render_weather_widget()
    
    # Render recent chats widget
    render_recent_chats_widget()

    # Top navigation / Home button with improved styling
    st.markdown('''
    <div style="
        display: flex; 
        justify-content: center; 
        margin-bottom: 8px;
        position: relative;
        z-index: 15;
    ">
        <a href="https://lesleykaps.github.io/ai-travel-agent/" 
           class="btn-link" 
           target="_self" 
           aria-label="Go to Home"
           style="
               color: var(--text-secondary);
               text-decoration: none;
               font-weight: 500;
               font-size: 14px;
               padding: 8px 16px;
               border-radius: 12px;
               background: var(--chip-bg);
               border: 1px solid var(--card-border);
               transition: all 0.2s ease;
               backdrop-filter: blur(10px);
           "
           onmouseover="this.style.color='var(--text-primary)'; this.style.background='var(--chip-hover)'"
           onmouseout="this.style.color='var(--text-secondary)'; this.style.background='var(--chip-bg)'">
            ⟵ Home
        </a>
    </div>
    ''', unsafe_allow_html=True)

    # Enhanced greeting container with orb
    st.markdown('''
    <div class="greeting-container" style="
        position: relative; 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        margin-bottom: 12px;
        z-index: 10;
    ">
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="orb"></div>', unsafe_allow_html=True)
    
    # Get time-based greeting with proper formatting
    time_greeting = _time_of_day()
    greeting_text = f"Good {time_greeting.capitalize()}, Iqbal"
    st.markdown(f'<div class="greeting">{greeting_text}</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">How can I help you?</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Modern suggestion chips with icons
    suggestions = [
        {'icon': '✈️', 'text': 'Create itinerary'},
        {'icon': '📍', 'text': 'Make a plan'},
        {'icon': '📋', 'text': 'Summarize text'},
        {'icon': '💡', 'text': 'Help me write'},
        {'icon': '🌍', 'text': 'Brainstorm'}
    ]
    
    st.markdown('<div class="chips">', unsafe_allow_html=True)
    chip_cols = st.columns(len(suggestions))
    for i, suggestion in enumerate(suggestions):
        with chip_cols[i]:
            chip_html = f"""
            <div style="
                background: var(--chip-bg);
                border: 1px solid var(--card-border);
                border-radius: 12px;
                padding: 12px 16px;
                text-align: center;
                cursor: pointer;
                transition: all 0.2s ease;
                backdrop-filter: blur(10px);
                box-shadow: var(--shadow-sm);
                margin: 4px;
            " onclick="document.querySelector('[data-testid=\\"stTextArea\\"] textarea').value = '{suggestion['text']}'; document.querySelector('[data-testid=\\"stTextArea\\"] textarea').focus();"
               onmouseover="this.style.background='var(--chip-hover)'; this.style.borderColor='var(--accent-primary)'; this.style.transform='translateY(-2px)'; this.style.boxShadow='var(--shadow-md)'"
               onmouseout="this.style.background='var(--chip-bg)'; this.style.borderColor='var(--card-border)'; this.style.transform='translateY(0)'; this.style.boxShadow='var(--shadow-sm)'">
                <div style="font-size: 20px; margin-bottom: 6px;">{suggestion['icon']}</div>
                <div style="font-size: 13px; font-weight: 500; color: var(--text-secondary);">{suggestion['text']}</div>
            </div>
            """
            st.markdown(chip_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Enhanced query input with modern styling
    st.markdown('''
    <div class="query-input-container" role="region" aria-labelledby="query-label" style="
        position: relative;
        margin: 20px 0;
    ">
        <label id="query-label" class="sr-only">Travel Query Input</label>
        <div class="query-card">
    ''', unsafe_allow_html=True)
    
    user_input = st.text_area(
        'Travel Query',
        height=120,
        key='query',
        placeholder='Ask Synapse AI...',
        label_visibility='collapsed',
        help='Enter your query. Press Ctrl+Enter to submit or Enter for a new line.'
    )
    
    st.markdown('''
        </div>
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 12px;
            padding: 0 4px;
        ">
            <div style="
                font-size: 12px;
                color: var(--text-muted);
                display: flex;
                align-items: center;
                gap: 8px;
            ">
                <span>💡</span>
                <span>Try asking about travel plans, destinations, or itineraries</span>
            </div>
            <div style="
                font-size: 11px;
                color: var(--text-muted);
                background: var(--chip-bg);
                padding: 4px 8px;
                border-radius: 6px;
                border: 1px solid var(--card-border);
            ">
                Ctrl + Enter to send
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # Enhanced primary action button
    st.markdown('<div class="primary-actions">', unsafe_allow_html=True)
    submit_clicked = st.button('✨ Generate Response', use_container_width=True, key='submit_btn')
    st.markdown('</div>', unsafe_allow_html=True)

    # JavaScript for Enter key functionality
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Validation message functions
        function showValidationMessage(message) {
            clearValidationMessage();
            const validationDiv = document.createElement('div');
            validationDiv.id = 'validation-error';
            validationDiv.className = 'validation-message error';
            validationDiv.setAttribute('role', 'alert');
            validationDiv.setAttribute('aria-live', 'polite');
            validationDiv.textContent = message;
            
            const textArea = document.querySelector('textarea[aria-label="Travel Query"]');
            if (textArea && textArea.parentNode) {
                textArea.parentNode.appendChild(validationDiv);
            }
        }
        
        function clearValidationMessage() {
            const existingMessage = document.getElementById('validation-error');
            if (existingMessage) {
                existingMessage.remove();
            }
        }
        
        // Function to handle Enter key press
        function handleEnterKey() {
            const textArea = document.querySelector('textarea[aria-label="Travel Query"]');
            const submitButton = document.querySelector('button[kind="primary"]');
            
            if (textArea && submitButton) {
                // Add ARIA attributes for accessibility
                textArea.setAttribute('aria-describedby', 'enter-key-help');
                textArea.setAttribute('role', 'textbox');
                textArea.setAttribute('aria-multiline', 'true');
                
                // Add helper text for accessibility
                if (!document.getElementById('enter-key-help')) {
                    const helpText = document.createElement('div');
                    helpText.id = 'enter-key-help';
                    helpText.className = 'sr-only';
                    helpText.textContent = 'Press Ctrl+Enter to submit, or Enter for new line';
                    textArea.parentNode.appendChild(helpText);
                }
                
                textArea.addEventListener('keydown', function(event) {
                     // Ctrl+Enter or Cmd+Enter to submit (for accessibility and multi-line support)
                     if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
                         event.preventDefault();
                         
                         // Enhanced validation before submission
                         const inputValue = textArea.value.trim();
                         
                         // Check for empty input
                         if (inputValue.length === 0) {
                             textArea.setAttribute('aria-invalid', 'true');
                             textArea.setAttribute('aria-describedby', 'enter-key-help validation-error');
                             showValidationMessage('Please enter a travel query before submitting.');
                             textArea.focus();
                             return;
                         }
                         
                         // Check for minimum length (basic validation)
                         if (inputValue.length < 3) {
                             textArea.setAttribute('aria-invalid', 'true');
                             textArea.setAttribute('aria-describedby', 'enter-key-help validation-error');
                             showValidationMessage('Please enter a more detailed travel query (at least 3 characters).');
                             textArea.focus();
                             return;
                         }
                         
                         // Check if button is already disabled (preventing double submission)
                         if (submitButton.disabled || submitButton.getAttribute('aria-disabled') === 'true') {
                             showValidationMessage('Please wait, your request is being processed.');
                             return;
                         }
                         
                         // Clear any previous validation errors
                         textArea.removeAttribute('aria-invalid');
                         textArea.setAttribute('aria-describedby', 'enter-key-help');
                         clearValidationMessage();
                         
                         // Trigger button click
                         submitButton.click();
                     }
                     // Regular Enter for new line (default behavior)
                     else if (event.key === 'Enter' && !event.ctrlKey && !event.metaKey) {
                         // Clear validation errors when user continues typing
                         textArea.removeAttribute('aria-invalid');
                         textArea.setAttribute('aria-describedby', 'enter-key-help');
                         clearValidationMessage();
                         return;
                     }
                 });
                 
                 // Add input event listener to clear validation errors while typing
                 textArea.addEventListener('input', function() {
                     if (textArea.getAttribute('aria-invalid') === 'true') {
                         textArea.removeAttribute('aria-invalid');
                         textArea.setAttribute('aria-describedby', 'enter-key-help');
                         clearValidationMessage();
                     }
                 });
                
                // Add visual indicator for keyboard shortcuts
                const shortcutHint = document.createElement('div');
                shortcutHint.className = 'keyboard-shortcut-hint';
                shortcutHint.innerHTML = '<small style="color: #6b7280; font-size: 0.75rem;">💡 Tip: Press Ctrl+Enter to submit</small>';
                textArea.parentNode.appendChild(shortcutHint);
            }
        }
        
        // Initial setup
        handleEnterKey();
        
        // Re-setup after Streamlit reruns
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length > 0) {
                    setTimeout(handleEnterKey, 100);
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
    </script>
    """, unsafe_allow_html=True)

    st.markdown('<div class="helper">AI Travel Agent may make mistakes. Verify important details.</div>', unsafe_allow_html=True)

    # Close the app-wrap div
    st.markdown('</div>', unsafe_allow_html=True)

    return user_input, submit_clicked


# Brand mapping tables for stylized badges (fallback when logo URLs aren’t present)
AIRLINE_BRANDS = {
    'delta': {'abbr': 'DL', 'color': '#1D4ED8'},
    'united': {'abbr': 'UA', 'color': '#1E3A8A'},
    'american': {'abbr': 'AA', 'color': '#DC2626'},
    'lufthansa': {'abbr': 'LH', 'color': '#F59E0B'},
    'air france': {'abbr': 'AF', 'color': '#0EA5E9'},
    'ryanair': {'abbr': 'FR', 'color': '#2563EB'},
    'easyjet': {'abbr': 'U2', 'color': '#F97316'},
    'emirates': {'abbr': 'EK', 'color': '#991B1B'},
    'qatar': {'abbr': 'QR', 'color': '#7C3AED'},
    'singapore': {'abbr': 'SQ', 'color': '#10B981'},
}
HOTEL_BRANDS = {
    'marriott': {'abbr': 'MR', 'color': '#7C3AED'},
    'hilton': {'abbr': 'HL', 'color': '#2563EB'},
    'hyatt': {'abbr': 'HY', 'color': '#0EA5E9'},
    'ihg': {'abbr': 'IH', 'color': '#F59E0B'},
    'accor': {'abbr': 'AC', 'color': '#10B981'},
    'radisson': {'abbr': 'RD', 'color': '#DC2626'},
}


# Real SVG logo mapping via SimpleIcons CDN (fallback to badges if not found)
AIRLINE_LOGOS = {
    'delta': 'https://cdn.simpleicons.org/deltaairlines?viewbox=auto',
    'united': 'https://cdn.simpleicons.org/unitedairlines?viewbox=auto',
    'american': 'https://cdn.simpleicons.org/americanairlines?viewbox=auto',
    'lufthansa': 'https://cdn.simpleicons.org/lufthansa?viewbox=auto',
    'air france': 'https://cdn.simpleicons.org/airfrance?viewbox=auto',
}
HOTEL_LOGOS = {
    'marriott': 'https://cdn.simpleicons.org/marriott?viewbox=auto',
    'hilton': 'https://cdn.simpleicons.org/hilton?viewbox=auto',
    'hyatt': 'https://cdn.simpleicons.org/hyatt?viewbox=auto',
    'ihg': 'https://cdn.simpleicons.org/ihg?viewbox=auto',
    'accor': 'https://cdn.simpleicons.org/accor?viewbox=auto',
}


def _brand_badge_html(name: str, mapping: dict, default_icon: str) -> str:
    if not name:
        return default_icon
    key = name.strip().lower()
    # Loose matching for multi-word brand names
    for brand, meta in mapping.items():
        if brand in key:
            abbr = meta.get('abbr', brand[:2].upper())
            color = meta.get('color', '#3b82f6')
            return f'<span class="brand-badge" style="background:{color}">{abbr}</span>'
    return default_icon

# Prefer real SVG logos when available

def _brand_logo_html(name: str, svg_map: dict, default_icon: str, css_class: str = 'airline-logo') -> str:
    if not name:
        return default_icon
    key = name.strip().lower()
    for brand, url in svg_map.items():
        if brand in key and url:
            return f'<img src="{url}" class="{css_class}" alt="{name}">'  # URL and name are already cleaned upstream
    return default_icon

def parse_flight_data(flight_data):
    """Parse individual flight data and return formatted HTML"""
    import re
    import html
    
    def clean_html(text):
        """Remove HTML tags and clean text content"""
        if not text:
            return ""
        
        text_str = str(text)
        
        # Remove all HTML tags (including self-closing and malformed ones)
        clean_text = re.sub(r'<[^>]*>', '', text_str)
        
        # Remove HTML entities and convert common ones to text
        clean_text = re.sub(r'&nbsp;', ' ', clean_text)
        clean_text = re.sub(r'&amp;', '&', clean_text)
        clean_text = re.sub(r'&lt;', '<', clean_text)
        clean_text = re.sub(r'&gt;', '>', clean_text)
        clean_text = re.sub(r'&quot;', '"', clean_text)
        clean_text = re.sub(r'&#39;', "'", clean_text)
        clean_text = re.sub(r'&[a-zA-Z0-9#]+;', '', clean_text)
        
        # Remove extra whitespace and newlines
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Don't escape - we want clean text, not HTML entities
        return clean_text
    
    try:
        # Extract flight information
        flights = flight_data.get('flights', [{}])
        # Segment-aware selection: use first and last segments for dep/arr
        first_segment = flights[0] if flights else {}
        last_segment = flights[-1] if flights else first_segment
        
        # Airline/logo (prefer segment airline if present, else fallback)
        airline = clean_html(first_segment.get('airline') or flight_data.get('airline') or 'Unknown Airline')
        airline_logo = first_segment.get('airline_logo') or flight_data.get('airline_logo') or ''
        # Prefer real SVG brand logo when available; fallback to provided logo URL, then badge
        logo_html = (
            f'<img src="{airline_logo}" class="airline-logo" alt="{airline}">' if airline_logo else _brand_logo_html(airline, AIRLINE_LOGOS, _brand_badge_html(airline, AIRLINE_BRANDS, '✈️'), 'airline-logo')
        )
        
        # Airports: departure from first segment, arrival from last segment (handles connections)
        departure_airport = first_segment.get('departure_airport') or flight_data.get('departure_airport') or {}
        arrival_airport = last_segment.get('arrival_airport') or flight_data.get('arrival_airport') or {}
        
        dep_name = clean_html(departure_airport.get('name') or departure_airport.get('city') or 'Unknown')
        dep_id = clean_html(departure_airport.get('id') or departure_airport.get('code') or '')
        arr_name = clean_html(arrival_airport.get('name') or arrival_airport.get('city') or 'Unknown')
        arr_id = clean_html(arrival_airport.get('id') or arrival_airport.get('code') or '')
        
        # Times: prefer segment times; fallback to possible alternative keys
        departure_time = clean_html(
            first_segment.get('departure_time')
            or first_segment.get('departs_at')
            or (departure_airport.get('time') if isinstance(departure_airport, dict) else None)
            or flight_data.get('departure_time')
            or 'Unknown'
        )
        arrival_time = clean_html(
            last_segment.get('arrival_time')
            or last_segment.get('arrives_at')
            or (arrival_airport.get('time') if isinstance(arrival_airport, dict) else None)
            or flight_data.get('arrival_time')
            or 'Unknown'
        )
        
        duration = clean_html(flight_data.get('total_duration', 'Unknown'))
        price = clean_html(flight_data.get('price', 'Price not available'))
        booking_link = flight_data.get('link', '')
        
        # Additional details
        stops = len(flights) - 1 if len(flights) > 1 else 0
        stops_text = f"{stops} stop{'s' if stops != 1 else ''}" if stops > 0 else "Direct"
        aircraft = clean_html(first_segment.get('aircraft') or flight_data.get('aircraft') or 'Unknown aircraft')
        travel_class = clean_html(first_segment.get('travel_class') or flight_data.get('travel_class') or 'Economy')
        flight_number = clean_html(first_segment.get('flight_number') or flight_data.get('flight_number') or '')
        
        link_html = f'<a href="{booking_link}" class="btn-link" target="_blank" rel="noopener">View on Google Flights</a>' if booking_link else ''
        
        return f"""
        <div class="travel-card-item">
            <div class="card-header">
                <div class="card-icon">{logo_html}</div>
                <div>
                    <h3 class="card-title">{airline} {flight_number}</h3>
                    <p class="card-subtitle">{dep_name} ({dep_id}) → {arr_name} ({arr_id})</p>
                </div>
            </div>
            <div class="card-content">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 1rem;">
                    <div>
                        <p><strong>Departure:</strong><br>{departure_time}</p>
                        <p><strong>Arrival:</strong><br>{arrival_time}</p>
                    </div>
                    <div>
                        <p><strong>Duration:</strong><br>{duration}</p>
                        <p><strong>Stops:</strong><br>{stops_text}</p>
                    </div>
                </div>
                <div style="border-top: 1px solid rgba(59, 130, 246, 0.2); padding-top: 1rem;">
                    <p><strong>Aircraft:</strong> {aircraft}</p>
                    <p><strong>Class:</strong> {travel_class}</p>
                    <p><strong>Price:</strong> <span class="price-highlight">{price}</span></p>
                    <div>{link_html}</div>
                </div>
            </div>
        </div>
        """
    except Exception as e:
        return f"""
        <div class="travel-card-item">
            <div class="card-header">
                <div class="card-icon">✈️</div>
                <div>
                    <h3 class="card-title">Flight Option</h3>
                    <p class="card-subtitle">Flight details</p>
                </div>
            </div>
            <div class="card-content">
                <p>Flight information available</p>
            </div>
        </div>
        """

def render_sidebar_settings():
    st.sidebar.header('Settings')
    # Currency
    currency_options = ['USD', 'EUR', 'GBP', 'JPY', 'ILS']
    currency_default = os.environ.get('CURRENCY', 'USD')
    try:
        currency_index = currency_options.index(currency_default)
    except ValueError:
        currency_index = 0
    currency = st.sidebar.selectbox('Currency', currency_options, index=currency_index)

    # Language (hl)
    hl_options = ['en', 'es', 'de', 'fr', 'ja', 'he']
    hl_default = os.environ.get('SERPAPI_HL', 'en')
    try:
        hl_index = hl_options.index(hl_default)
    except ValueError:
        hl_index = 0
    hl = st.sidebar.selectbox('Language (hl)', hl_options, index=hl_index)

    # Region (gl)
    gl_options = ['us', 'uk', 'de', 'fr', 'es', 'jp', 'il']
    gl_default = os.environ.get('SERPAPI_GL', 'us')
    try:
        gl_index = gl_options.index(gl_default)
    except ValueError:
        gl_index = 0
    gl = st.sidebar.selectbox('Region (gl)', gl_options, index=gl_index)

    # Flight type override (SerpAPI type: 1=Round trip, 2=One way)
    flight_type_map = {'Round trip': '1', 'One way': '2'}
    flight_type_default = os.environ.get('FLIGHTS_TYPE_OVERRIDE', '')
    ft_label_default = 'Round trip' if flight_type_default == '1' else ('One way' if flight_type_default == '2' else 'Round trip')
    flight_type_label = st.sidebar.selectbox('Flight Type', list(flight_type_map.keys()), index=list(flight_type_map.keys()).index(ft_label_default))
    flights_type_override = flight_type_map[flight_type_label]

    # Hotel sort_by override
    # Common options: 8=Highest rating, 2=Price low->high, 3=Price high->low, 6=Distance
    hotel_sort_options = [('Default', ''), ('Highest rating (8)', '8'), ('Price: Low to High (2)', '2'), ('Price: High to Low (3)', '3'), ('Distance (6)', '6')]
    sort_default = os.environ.get('HOTELS_SORT_BY_OVERRIDE', '')
    sort_index = next((i for i, (_, code) in enumerate(hotel_sort_options) if code == sort_default), 0)
    sort_label, sort_code = st.sidebar.selectbox('Hotel Sort By', hotel_sort_options, index=sort_index)

    # Apply settings immediately for runtime tools
    os.environ['CURRENCY'] = currency
    os.environ['SERPAPI_HL'] = hl
    os.environ['SERPAPI_GL'] = gl
    os.environ['FLIGHTS_TYPE_OVERRIDE'] = flights_type_override
    os.environ['HOTELS_SORT_BY_OVERRIDE'] = sort_code

    st.sidebar.caption('Settings apply to new searches.')

def parse_hotel_data(hotel_data):
    """Parse individual hotel data and return formatted HTML"""
    import re
    import html
    
    def clean_html(text):
        """Remove HTML tags and clean text content"""
        if not text:
            return ""
        
        text_str = str(text)
        
        # Remove all HTML tags (including self-closing and malformed ones)
        clean_text = re.sub(r'<[^>]*>', '', text_str)
        
        # Remove HTML entities and convert common ones to text
        clean_text = re.sub(r'&nbsp;', ' ', clean_text)
        clean_text = re.sub(r'&amp;', '&', clean_text)
        clean_text = re.sub(r'&lt;', '<', clean_text)
        clean_text = re.sub(r'&gt;', '>', clean_text)
        clean_text = re.sub(r'&quot;', '"', clean_text)
        clean_text = re.sub(r'&#39;', "'", clean_text)
        clean_text = re.sub(r'&[a-zA-Z0-9#]+;', '', clean_text)
        
        # Remove extra whitespace and newlines
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Return clean text without HTML escaping
        return clean_text
    
    try:
        # Extract hotel information and clean HTML
        name = clean_html(hotel_data.get('name', 'Unknown Hotel'))
        location = clean_html(hotel_data.get('location', 'Unknown Location'))
        rating = clean_html(hotel_data.get('overall_rating', 'No rating'))
        reviews = clean_html(hotel_data.get('reviews', 'No reviews'))
        
        # Price information
        rate_info = hotel_data.get('rate_per_night', {})
        price = clean_html(rate_info.get('lowest', 'Price not available'))
        price_currency = clean_html(rate_info.get('currency', ''))
        price_display = f"{price} {price_currency}" if price_currency and price != 'Price not available' else price
        
        # Additional details
        hotel_class = clean_html(hotel_data.get('hotel_class', 'Not specified'))
        property_type = clean_html(hotel_data.get('type', 'Hotel'))
        distance = clean_html(hotel_data.get('distance_from_search_location', ''))
        
        # Amenities
        amenities = hotel_data.get('amenities', [])
        top_amenities = [clean_html(amenity) for amenity in amenities[:4]] if amenities else ['Standard amenities']
        amenities_text = ', '.join(top_amenities)
        
        # Images
        images = hotel_data.get('images', [])
        main_image = images[0] if images else ''
        
        # Rating display
        rating_display = f"⭐ {rating}/5" if rating != 'No rating' else 'No rating'
        reviews_display = f"({reviews} reviews)" if reviews != 'No reviews' else ''
        
        # Distance display
        distance_text = f"📍 {distance}" if distance else ''
        link = hotel_data.get('link', '')
        link_html = f'<a href="{link}" class="btn-link" target="_blank" rel="noopener">View on Google Hotels</a>' if link else ''
        image_html = f'<img src="{main_image}" alt="{name}" style="width:100%; height:200px; object-fit:cover; border-radius:8px; margin-bottom:0.75rem;" />' if main_image else ''
        
        # Brand badge in header
        brand_html = _brand_badge_html(name, HOTEL_BRANDS, '🏨')
        
        return f"""
        <div class="travel-card-item">
            <div class="card-header">
                <div class="card-icon">{brand_html}</div>
                <div>
                    <h3 class="card-title">{name}</h3>
                    <p class="card-subtitle">{location}</p>
                </div>
            </div>
            <div class="card-content">
                {image_html}
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 1rem;">
                    <div>
                        <p><strong>Rating:</strong><br>{rating_display}</p>
                        <p><strong>Type:</strong><br>{property_type}</p>
                    </div>
                    <div>
                        <p><strong>Class:</strong><br>{hotel_class} star</p>
                        <p><strong>Reviews:</strong><br>{reviews_display}</p>
                    </div>
                </div>
                <div style="border-top: 1px solid rgba(59, 130, 246, 0.2); padding-top: 1rem;">
                    <p><strong>Amenities:</strong> {amenities_text}</p>
                    <p><strong>Price per night:</strong> <span class="price-highlight">{price_display}</span></p>
                    <div>{link_html}</div>
                </div>
            </div>
        </div>
        """
    except Exception as e:
        return f"""
        <div class="travel-card-item">
            <div class="card-header">
                <div class="card-icon">🏨</div>
                <div>
                    <h3 class="card-title">Hotel Option</h3>
                    <p class="card-subtitle">Hotel details</p>
                </div>
            </div>
            <div class="card-content">
                <p>Hotel information available</p>
            </div>
        </div>
        """

def process_query(user_input):
    if user_input:
        try:
            thread_id = str(uuid.uuid4())
            messages = [HumanMessage(content=user_input)]
            config = {'configurable': {'thread_id': thread_id}}

            result = st.session_state.agent.graph.invoke({'messages': messages}, config=config)
            
            # Clean non-tool message content to remove any HTML tags including pre tags
            if 'messages' in result:
                for message in result['messages']:
                    if hasattr(message, 'content'):
                        # Preserve tool outputs (JSON) for parsing
                        if hasattr(message, 'name') and message.name in ('flights_finder', 'hotels_finder'):
                            continue
                        message.content = clean_html_content(str(message.content))

            # Display response header
            st.markdown('<div class="travel-response-container">', unsafe_allow_html=True)
            st.markdown('''
                <div class="travel-response-header">
                    <h2 class="travel-response-title">Your Travel Results</h2>
                    <p class="travel-response-subtitle">Here are the individual options I found for you</p>
                </div>
            ''', unsafe_allow_html=True)

            # Check if we have tool results with structured data
            has_structured_data = False
            flights_data = []
            hotels_data = []
            
            # Look for tool messages in the conversation
            for message in result['messages']:
                if hasattr(message, 'name') and hasattr(message, 'content'):
                    if message.name == 'flights_finder':
                        try:
                            if isinstance(message.content, list):
                                flights_data = message.content
                            else:
                                flights_data = json.loads(str(message.content))
                            if isinstance(flights_data, list):
                                has_structured_data = True
                        except Exception:
                            pass
                    elif message.name == 'hotels_finder':
                        try:
                            if isinstance(message.content, list):
                                hotels_data = message.content
                            else:
                                hotels_data = json.loads(str(message.content))
                            if isinstance(hotels_data, list):
                                has_structured_data = True
                        except Exception:
                            pass

            if has_structured_data and (flights_data or hotels_data):
                # Display structured data as individual cards
                st.markdown('<div class="travel-cards-grid">', unsafe_allow_html=True)
                
                # Display flight cards or empty state
                if flights_data:
                    for flight in flights_data[:6]:  # Limit to 6 results
                        flight_html = parse_flight_data(flight)
                        st.markdown(flight_html, unsafe_allow_html=True)
                else:
                    st.markdown('''
                        <div class="travel-card-item">
                            <div class="card-header">
                                <div class="card-icon">✈️</div>
                                <div>
                                    <h3 class="card-title">No Flights Found</h3>
                                    <p class="card-subtitle">Try adjusting dates, airports, or budget.</p>
                                </div>
                            </div>
                            <div class="card-content">
                                <p>No flight options matched your criteria.</p>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                
                # Display hotel cards or empty state
                if hotels_data:
                    for hotel in hotels_data[:6]:  # Limit to 6 results
                        hotel_html = parse_hotel_data(hotel)
                        st.markdown(hotel_html, unsafe_allow_html=True)
                else:
                    st.markdown('''
                        <div class="travel-card-item">
                            <div class="card-header">
                                <div class="card-icon">🏨</div>
                                <div>
                                    <h3 class="card-title">No Hotels Found</h3>
                                    <p class="card-subtitle">Try changing location, dates, or rating/class.</p>
                                </div>
                            </div>
                            <div class="card-content">
                                <p>No hotel options matched your criteria.</p>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # If no structured data is available, show a simple message
                st.markdown('''
                    <div class="travel-card">
                        <div class="travel-card-header">
                            <div class="travel-card-icon">✈️</div>
                            <h3 class="travel-card-title">Travel Information</h3>
                        </div>
                        <div class="travel-card-content">
                            <p>I'm working on finding travel options for you. Please try refining your search with specific dates, locations, or preferences.</p>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.markdown('<div class="travel-response-container">', unsafe_allow_html=True)
            st.markdown('''
                <div class="travel-card">
                    <div class="travel-card-header">
                        <div class="travel-card-icon">⚠️</div>
                        <h3 class="travel-card-title">Error</h3>
                    </div>
                    <div class="travel-card-content">
            ''', unsafe_allow_html=True)
            st.error(f'Error: {e}')
            st.markdown('''
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="travel-response-container">', unsafe_allow_html=True)
        st.markdown('''
            <div class="travel-card">
                <div class="travel-card-header">
                    <div class="travel-card-icon">📝</div>
                    <h3 class="travel-card-title">Missing Information</h3>
                </div>
                <div class="travel-card-content">
        ''', unsafe_allow_html=True)
        st.error('Please enter a travel query.')
        st.markdown('''
                </div>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)





def main():
    st.set_page_config(page_title='AI Travel Agent', page_icon='✈️', layout='centered', initial_sidebar_state='collapsed')
    initialize_agent()
    render_custom_css()
    render_sidebar_settings()
    # Environment warnings for missing keys
    missing_env = []
    if not get_env_var('SERPAPI_API_KEY'):
        missing_env.append('SERPAPI_API_KEY')
    if not get_env_var('GOOGLE_API_KEY'):
        missing_env.append('GOOGLE_API_KEY')
    if missing_env:
        st.warning(f"Missing environment variables: {', '.join(missing_env)}. Set them in your environment, .env file, Streamlit secrets, or via the sidebar.")
    user_input, submit_clicked = render_ui()
    if submit_clicked:
        process_query(user_input)


if __name__ == '__main__':
    main()
