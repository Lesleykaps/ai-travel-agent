import os
from typing import Optional

import serpapi
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool

# from pydantic import BaseModel, Field


class HotelsInput(BaseModel):
    q: str = Field(description='Location of the hotel')
    check_in_date: str = Field(description='Check-in date. The format is YYYY-MM-DD. e.g. 2024-06-22')
    check_out_date: str = Field(description='Check-out date. The format is YYYY-MM-DD. e.g. 2024-06-28')
    sort_by: Optional[int] = Field(8, description='Parameter is used for sorting the results. Default is sort by highest rating')
    adults: Optional[int] = Field(1, description='Number of adults. Default to 1.')
    children: Optional[int] = Field(0, description='Number of children. Default to 0.')
    rooms: Optional[int] = Field(1, description='Number of rooms. Default to 1.')
    hotel_class: Optional[str] = Field(
        None, description='Parameter defines to include only certain hotel class in the results. for example- 2,3,4')


class HotelsInputSchema(BaseModel):
    params: HotelsInput


@tool(args_schema=HotelsInputSchema)
def hotels_finder(params: HotelsInput):
    '''
    Find hotels using the Google Hotels engine.

    Returns:
        dict: Hotel search results.
    '''

    search_params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'google_hotels',
        'hl': os.environ.get('SERPAPI_HL', 'en'),
        'gl': os.environ.get('SERPAPI_GL', 'us'),
        'q': params.q,
        'check_in_date': params.check_in_date,
        'check_out_date': params.check_out_date,
        'currency': os.environ.get('CURRENCY', 'USD'),
        'adults': params.adults,
        'children': params.children,
        'rooms': params.rooms,
        'sort_by': params.sort_by,
        'hotel_class': params.hotel_class
    }

    # Allow runtime override from sidebar settings
    override_sort = os.environ.get('HOTELS_SORT_BY_OVERRIDE')
    if override_sort:
        search_params['sort_by'] = override_sort

    try:
        safe_params = dict(search_params)
        if 'api_key' in safe_params:
            safe_params['api_key'] = '***'
        print(f"DEBUG: Hotel Search params (masked): {safe_params}")
        search = serpapi.search(search_params)
        data = getattr(search, 'data', {}) or {}
        properties = data.get('properties', [])
        return properties[:5]
    except serpapi.SerpApiError as e:
        print(f"DEBUG: SerpAPI error: {str(e)}")
        return []
