import os
from typing import Optional

# from pydantic import BaseModel, Field
import serpapi
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool


class FlightsInput(BaseModel):
    departure_airport: Optional[str] = Field(description='Departure airport code (IATA)')
    arrival_airport: Optional[str] = Field(description='Arrival airport code (IATA)')
    outbound_date: Optional[str] = Field(description='Parameter defines the outbound date. The format is YYYY-MM-DD. e.g. 2024-06-22')
    return_date: Optional[str] = Field(description='Parameter defines the return date for round-trip flights. Leave empty for one-way flights. The format is YYYY-MM-DD. e.g. 2024-06-28')
    adults: Optional[int] = Field(1, description='Parameter defines the number of adults. Default to 1.')
    children: Optional[int] = Field(0, description='Parameter defines the number of children. Default to 0.')
    infants_in_seat: Optional[int] = Field(0, description='Parameter defines the number of infants in seat. Default to 0.')
    infants_on_lap: Optional[int] = Field(0, description='Parameter defines the number of infants on lap. Default to 0.')


class FlightsInputSchema(BaseModel):
    params: FlightsInput


@tool(args_schema=FlightsInputSchema)
def flights_finder(params: FlightsInput):
    '''
    Find flights using the Google Flights engine.

    Returns:
        dict: Flight search results.
    '''

    search_params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'google_flights',
        'hl': os.environ.get('SERPAPI_HL', 'en'),
        'gl': os.environ.get('SERPAPI_GL', 'us'),
        'departure_id': params.departure_airport,
        'arrival_id': params.arrival_airport,
        'outbound_date': params.outbound_date,
        'currency': os.environ.get('CURRENCY', 'USD'),
        'adults': params.adults,
        'infants_in_seat': params.infants_in_seat,
        'infants_on_lap': params.infants_on_lap,
        'children': params.children
    }
    
    # Set flight type and return_date based on whether return_date is provided
    # Handle both None and empty string cases for one-way flights
    if params.return_date and params.return_date.strip():
        search_params['type'] = '1'  # Round trip
        search_params['return_date'] = params.return_date
    else:
        search_params['type'] = '2'  # One way

    # Allow runtime override from sidebar settings
    override_type = os.environ.get('FLIGHTS_TYPE_OVERRIDE')
    if override_type in {'1', '2'}:
        search_params['type'] = override_type

    try:
        safe_params = dict(search_params)
        if 'api_key' in safe_params:
            safe_params['api_key'] = '***'
        print(f"DEBUG: Search params being sent to SerpAPI (masked): {safe_params}")
        search = serpapi.search(search_params)
        data = getattr(search, 'data', {}) or {}
        print(f"DEBUG: SerpAPI response keys: {list(data.keys())}")
        results = data.get('best_flights', [])
    except serpapi.SerpApiError as e:
        print(f"DEBUG: SerpAPI error: {str(e)}")
        results = []
    return results
