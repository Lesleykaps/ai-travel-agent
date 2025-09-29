"""
City Standardization Utility

This module provides comprehensive city name standardization and airport code mapping
to ensure consistent formatting across all search operations.
"""

import re
from typing import Dict, Optional, Tuple
from difflib import get_close_matches


class CityStandardizer:
    """Handles city name standardization and airport code mapping."""
    
    def __init__(self):
        # Comprehensive city to airport code mapping
        self.city_to_airport = {
            # Major African Cities
            'durban': 'DUR',
            'harare': 'HRE',
            'cape town': 'CPT',
            'capetown': 'CPT',
            'johannesburg': 'JNB',
            'joburg': 'JNB',
            'jburg': 'JNB',
            'cairo': 'CAI',
            'lagos': 'LOS',
            'nairobi': 'NBO',
            'casablanca': 'CMN',
            'addis ababa': 'ADD',
            'dar es salaam': 'DAR',
            'accra': 'ACC',
            'tunis': 'TUN',
            'algiers': 'ALG',
            'kigali': 'KGL',
            'lusaka': 'LUN',
            'maputo': 'MPM',
            'windhoek': 'WDH',
            'gaborone': 'GBE',
            'maseru': 'MSU',
            'mbabane': 'MTS',
            'blantyre': 'BLZ',
            'lilongwe': 'LLW',
            
            # Major International Cities
            'london': 'LHR',
            'paris': 'CDG',
            'new york': 'JFK',
            'newyork': 'JFK',
            'nyc': 'JFK',
            'los angeles': 'LAX',
            'losangeles': 'LAX',
            'chicago': 'ORD',
            'miami': 'MIA',
            'toronto': 'YYZ',
            'vancouver': 'YVR',
            'sydney': 'SYD',
            'melbourne': 'MEL',
            'tokyo': 'NRT',
            'beijing': 'PEK',
            'shanghai': 'PVG',
            'hong kong': 'HKG',
            'hongkong': 'HKG',
            'singapore': 'SIN',
            'bangkok': 'BKK',
            'mumbai': 'BOM',
            'delhi': 'DEL',
            'new delhi': 'DEL',
            'newdelhi': 'DEL',
            'dubai': 'DXB',
            'doha': 'DOH',
            'istanbul': 'IST',
            'moscow': 'SVO',
            'amsterdam': 'AMS',
            'frankfurt': 'FRA',
            'zurich': 'ZUR',
            'madrid': 'MAD',
            'barcelona': 'BCN',
            'rome': 'FCO',
            'milan': 'MXP',
            'vienna': 'VIE',
            'brussels': 'BRU',
            'stockholm': 'ARN',
            'oslo': 'OSL',
            'copenhagen': 'CPH',
            'helsinki': 'HEL',
            'athens': 'ATH',
            'lisbon': 'LIS',
            'dublin': 'DUB',
            'edinburgh': 'EDI',
            'manchester': 'MAN',
            'birmingham': 'BHX',
            'glasgow': 'GLA',
            
            # US Cities
            'atlanta': 'ATL',
            'boston': 'BOS',
            'dallas': 'DFW',
            'denver': 'DEN',
            'detroit': 'DTW',
            'houston': 'IAH',
            'las vegas': 'LAS',
            'lasvegas': 'LAS',
            'vegas': 'LAS',
            'minneapolis': 'MSP',
            'orlando': 'MCO',
            'philadelphia': 'PHL',
            'phoenix': 'PHX',
            'portland': 'PDX',
            'san francisco': 'SFO',
            'sanfrancisco': 'SFO',
            'seattle': 'SEA',
            'washington': 'DCA',
            'washington dc': 'DCA',
            'washingtondc': 'DCA',
            
            # Additional variations and common misspellings
            'jo\'burg': 'JNB',
            'jo-burg': 'JNB',
            'new york city': 'JFK',
            'la': 'LAX',
            'sf': 'SFO',
            'dc': 'DCA',
        }
        
        # Alternative airport codes for cities with multiple airports
        self.alternative_airports = {
            'london': ['LHR', 'LGW', 'STN', 'LTN'],
            'new york': ['JFK', 'LGA', 'EWR'],
            'paris': ['CDG', 'ORY'],
            'tokyo': ['NRT', 'HND'],
            'milan': ['MXP', 'LIN'],
            'rome': ['FCO', 'CIA'],
            'chicago': ['ORD', 'MDW'],
            'houston': ['IAH', 'HOU'],
            'washington': ['DCA', 'IAD', 'BWI'],
        }
        
        # Country to major airport mappings
        self.country_to_airport = {
            # African Countries
            'ethiopia': 'ADD',  # Addis Ababa Bole International Airport
            'south africa': 'JNB',  # OR Tambo International Airport, Johannesburg
            'southafrica': 'JNB',
            'kenya': 'NBO',  # Jomo Kenyatta International Airport, Nairobi
            'nigeria': 'LOS',  # Murtala Muhammed International Airport, Lagos
            'egypt': 'CAI',  # Cairo International Airport
            'morocco': 'CMN',  # Mohammed V International Airport, Casablanca
            'ghana': 'ACC',  # Kotoka International Airport, Accra
            'tanzania': 'DAR',  # Julius Nyerere International Airport, Dar es Salaam
            'zimbabwe': 'HRE',  # Robert Gabriel Mugabe International Airport, Harare
            'zambia': 'LUN',  # Kenneth Kaunda International Airport, Lusaka
            'botswana': 'GBE',  # Sir Seretse Khama International Airport, Gaborone
            'namibia': 'WDH',  # Hosea Kutako International Airport, Windhoek
            'uganda': 'EBB',  # Entebbe International Airport
            'rwanda': 'KGL',  # Kigali International Airport
            'senegal': 'DKR',  # Blaise Diagne International Airport, Dakar
            'ivory coast': 'ABJ',  # Félix-Houphouët-Boigny International Airport, Abidjan
            'ivorycoast': 'ABJ',
            'cote d\'ivoire': 'ABJ',
            'cotedivoire': 'ABJ',
            'tunisia': 'TUN',  # Tunis-Carthage International Airport
            'algeria': 'ALG',  # Houari Boumediene Airport, Algiers
            'libya': 'TIP',  # Tripoli International Airport
            'sudan': 'KRT',  # Khartoum International Airport
            'madagascar': 'TNR',  # Ivato International Airport, Antananarivo
            'mauritius': 'MRU',  # Sir Seewoosagur Ramgoolam International Airport
            'seychelles': 'SEZ',  # Seychelles International Airport
            
            # Major International Countries
            'united states': 'JFK',  # John F. Kennedy International Airport, New York
            'unitedstates': 'JFK',
            'usa': 'JFK',
            'america': 'JFK',
            'united kingdom': 'LHR',  # Heathrow Airport, London
            'unitedkingdom': 'LHR',
            'uk': 'LHR',
            'britain': 'LHR',
            'england': 'LHR',
            'france': 'CDG',  # Charles de Gaulle Airport, Paris
            'germany': 'FRA',  # Frankfurt Airport
            'italy': 'FCO',  # Leonardo da Vinci International Airport, Rome
            'spain': 'MAD',  # Adolfo Suárez Madrid-Barajas Airport
            'netherlands': 'AMS',  # Amsterdam Airport Schiphol
            'switzerland': 'ZUR',  # Zurich Airport
            'austria': 'VIE',  # Vienna International Airport
            'belgium': 'BRU',  # Brussels Airport
            'sweden': 'ARN',  # Stockholm Arlanda Airport
            'norway': 'OSL',  # Oslo Airport
            'denmark': 'CPH',  # Copenhagen Airport
            'finland': 'HEL',  # Helsinki Airport
            'greece': 'ATH',  # Athens International Airport
            'portugal': 'LIS',  # Lisbon Airport
            'ireland': 'DUB',  # Dublin Airport
            'russia': 'SVO',  # Sheremetyevo International Airport, Moscow
            'turkey': 'IST',  # Istanbul Airport
            'china': 'PEK',  # Beijing Capital International Airport
            'japan': 'NRT',  # Narita International Airport, Tokyo
            'india': 'DEL',  # Indira Gandhi International Airport, New Delhi
            'australia': 'SYD',  # Kingsford Smith Airport, Sydney
            'canada': 'YYZ',  # Toronto Pearson International Airport
            'brazil': 'GRU',  # São Paulo/Guarulhos International Airport
            'argentina': 'EZE',  # Ezeiza International Airport, Buenos Aires
            'mexico': 'MEX',  # Mexico City International Airport
            'thailand': 'BKK',  # Suvarnabhumi Airport, Bangkok
            'singapore': 'SIN',  # Singapore Changi Airport
            'malaysia': 'KUL',  # Kuala Lumpur International Airport
            'indonesia': 'CGK',  # Soekarno-Hatta International Airport, Jakarta
            'philippines': 'MNL',  # Ninoy Aquino International Airport, Manila
            'vietnam': 'SGN',  # Tan Son Nhat International Airport, Ho Chi Minh City
            'south korea': 'ICN',  # Incheon International Airport, Seoul
            'southkorea': 'ICN',
            'uae': 'DXB',  # Dubai International Airport
            'united arab emirates': 'DXB',
            'unitedarabemirates': 'DXB',
            'qatar': 'DOH',  # Hamad International Airport, Doha
            'saudi arabia': 'RUH',  # King Khalid International Airport, Riyadh
            'saudiarabia': 'RUH',
            'israel': 'TLV',  # Ben Gurion Airport, Tel Aviv
            'iran': 'IKA',  # Imam Khomeini International Airport, Tehran
            'pakistan': 'KHI',  # Jinnah International Airport, Karachi
            'bangladesh': 'DAC',  # Hazrat Shahjalal International Airport, Dhaka
            'sri lanka': 'CMB',  # Bandaranaike International Airport, Colombo
            'srilanka': 'CMB',
        }
        
        # Common city name variations and aliases
        self.city_aliases = {
            'jo\'burg': 'johannesburg',
            'joburg': 'johannesburg',
            'jburg': 'johannesburg',
            'cape town': 'cape town',
            'capetown': 'cape town',
            'nyc': 'new york',
            'new york city': 'new york',
            'newyork': 'new york',
            'la': 'los angeles',
            'losangeles': 'los angeles',
            'sf': 'san francisco',
            'sanfrancisco': 'san francisco',
            'vegas': 'las vegas',
            'lasvegas': 'las vegas',
            'dc': 'washington',
            'washington dc': 'washington',
            'washingtondc': 'washington',
            'new delhi': 'delhi',
            'newdelhi': 'delhi',
            'hong kong': 'hong kong',
            'hongkong': 'hong kong',
        }
    
    def normalize_city_name(self, city_name: str) -> str:
        """
        Normalize city name by removing special characters, extra spaces,
        and converting to lowercase.
        
        Args:
            city_name: Raw city name input
            
        Returns:
            Normalized city name
        """
        if not city_name:
            return ""
        
        # Convert to lowercase and strip whitespace
        normalized = city_name.lower().strip()
        
        # Remove special characters except spaces, hyphens, and apostrophes
        normalized = re.sub(r'[^\w\s\-\']', '', normalized)
        
        # Replace multiple spaces with single space
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Handle common abbreviations and variations
        normalized = normalized.replace('st.', 'saint')
        normalized = normalized.replace('mt.', 'mount')
        
        return normalized.strip()
    
    def get_airport_code(self, city_name: str) -> Optional[str]:
        """
        Get airport code for a given city name or country name.
        
        Args:
            city_name: City name or country name (can be raw or normalized)
            
        Returns:
            Airport code if found, None otherwise
        """
        if not city_name:
            return None
        
        # First, normalize the city name
        normalized = self.normalize_city_name(city_name)
        
        # Check direct city mapping
        if normalized in self.city_to_airport:
            return self.city_to_airport[normalized]
        
        # Check country mapping
        if normalized in self.country_to_airport:
            return self.country_to_airport[normalized]
        
        # Check city aliases
        if normalized in self.city_aliases:
            canonical_name = self.city_aliases[normalized]
            if canonical_name in self.city_to_airport:
                return self.city_to_airport[canonical_name]
        
        # Try fuzzy matching for typos (include both city and country mappings)
        all_locations = (list(self.city_to_airport.keys()) + 
                        list(self.country_to_airport.keys()) + 
                        list(self.city_aliases.keys()))
        
        close_matches = get_close_matches(
            normalized, 
            all_locations,
            n=1, 
            cutoff=0.8
        )
        
        if close_matches:
            match = close_matches[0]
            if match in self.city_to_airport:
                return self.city_to_airport[match]
            elif match in self.country_to_airport:
                return self.country_to_airport[match]
            elif match in self.city_aliases:
                canonical_name = self.city_aliases[match]
                if canonical_name in self.city_to_airport:
                    return self.city_to_airport[canonical_name]
        
        return None
    
    def get_standardized_city_info(self, city_name: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Get comprehensive standardized city information.
        
        Args:
            city_name: Raw city name input
            
        Returns:
            Tuple of (normalized_name, airport_code, canonical_name)
        """
        if not city_name:
            return None, None, None
        
        normalized = self.normalize_city_name(city_name)
        airport_code = self.get_airport_code(city_name)
        
        # Find canonical name
        canonical_name = normalized
        if normalized in self.city_aliases:
            canonical_name = self.city_aliases[normalized]
        
        return normalized, airport_code, canonical_name
    
    def get_alternative_airports(self, city_name: str) -> list:
        """
        Get alternative airport codes for cities with multiple airports.
        
        Args:
            city_name: City name
            
        Returns:
            List of airport codes
        """
        normalized = self.normalize_city_name(city_name)
        canonical_name = self.city_aliases.get(normalized, normalized)
        
        return self.alternative_airports.get(canonical_name, [])
    
    def is_valid_airport_code(self, code: str) -> bool:
        """
        Check if a string is already a valid airport code.
        
        Args:
            code: Potential airport code
            
        Returns:
            True if it's a valid airport code format
        """
        if not code:
            return False
        
        # Airport codes are typically 3 uppercase letters
        return bool(re.match(r'^[A-Z]{3}$', code.upper()))
    
    def standardize_location_input(self, location: str) -> Dict[str, str]:
        """
        Comprehensive location standardization for search inputs.
        
        Args:
            location: Raw location input (city name or airport code)
            
        Returns:
            Dictionary with standardized location information
        """
        if not location:
            return {
                'original': '',
                'normalized': '',
                'airport_code': None,
                'canonical_name': '',
                'is_airport_code': False,
                'alternatives': []
            }
        
        original = location.strip()
        
        # Check if input is already an airport code
        if self.is_valid_airport_code(original):
            return {
                'original': original,
                'normalized': original.upper(),
                'airport_code': original.upper(),
                'canonical_name': original.upper(),
                'is_airport_code': True,
                'alternatives': []
            }
        
        # Process as city name
        normalized, airport_code, canonical_name = self.get_standardized_city_info(original)
        alternatives = self.get_alternative_airports(original) if airport_code else []
        
        return {
            'original': original,
            'normalized': normalized or '',
            'airport_code': airport_code,
            'canonical_name': canonical_name or '',
            'is_airport_code': False,
            'alternatives': alternatives
        }


# Global instance for easy access
city_standardizer = CityStandardizer()


def standardize_city(city_name: str) -> str:
    """
    Quick function to get airport code for a city name.
    
    Args:
        city_name: City name to standardize
        
    Returns:
        Airport code if found, original input otherwise
    """
    result = city_standardizer.standardize_location_input(city_name)
    return result['airport_code'] or result['original']


def get_city_info(city_name: str) -> Dict[str, str]:
    """
    Quick function to get comprehensive city information.
    
    Args:
        city_name: City name to analyze
        
    Returns:
        Dictionary with standardized city information
    """
    return city_standardizer.standardize_location_input(city_name)