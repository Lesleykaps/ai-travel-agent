# pylint: disable = http-used,print-used,no-self-use

import datetime
import operator
import os
import json
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from agents.tools.flights_finder import flights_finder
from agents.tools.hotels_finder import hotels_finder
from agents.utils.env_utils import get_env_var

_ = load_dotenv()

CURRENT_YEAR = datetime.datetime.now().year


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


TOOLS_SYSTEM_PROMPT = f"""You are a smart travel agency with advanced city name standardization capabilities. You MUST ALWAYS use the tools to look up information.
    You are allowed to make multiple calls (either together or in sequence).
    The current year is {CURRENT_YEAR}.
    
    CRITICAL RULES - NEVER IGNORE THESE:
    1. ALWAYS use flights_finder tool when ANY flight, airline, or travel between cities is mentioned
    2. ALWAYS use hotels_finder tool when ANY accommodation, hotel, or lodging is mentioned
    3. NEVER provide responses without using tools first
    4. If a user mentions both flights and hotels, use BOTH tools
    5. If unsure what the user wants, use BOTH tools to be comprehensive
    
    For flight searches (MANDATORY for any flight-related query):
    - The flights_finder tool automatically converts city names to airport codes
    - Use city names directly (e.g., "Durban", "Harare", "New York", "Ethiopia", "Cape Town")
    - The system handles variations, abbreviations, and alternative names automatically
    - For one-way flights, only provide departure date and leave return date empty
    - Always provide detailed flight information including airlines, times, prices, and duration
    
    For hotel searches (MANDATORY for any accommodation query):
    - The hotels_finder tool automatically standardizes city names for consistent results
    - Use any city name format, the system will normalize it
    - Always search when users mention hotels, accommodation, stay, lodging, etc.
    
    City Name Standardization Features:
    - Automatic conversion of city names to proper airport codes for flights
    - Normalization of city names for hotel searches
    - Support for common abbreviations and alternative names
    - Case-insensitive processing
    - Handles typos and variations in city names
    
    RESPONSE REQUIREMENTS:
    - Always include detailed flight options with prices, times, airlines, and flight numbers
    - Always include hotel details with prices, ratings, and locations
    - Include links to websites when possible
    - Use appropriate currency formatting
    - Provide comprehensive, detailed responses based on tool results
    
    ABSOLUTELY FORBIDDEN:
    - Generic responses like "I've processed your travel request"
    - Responses without using tools for travel queries
    - Short, unhelpful answers
    - Ignoring user requests for flights or hotels
    
    Remember: Your job is to provide actual, detailed travel information using the tools. Never give generic responses!
    """

TOOLS = [flights_finder, hotels_finder]




class Agent:

    def __init__(self):
        self._tools = {t.name: t for t in TOOLS}
        self._tools_llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-lite', google_api_key=get_env_var('GOOGLE_API_KEY')).bind_tools(TOOLS)

        builder = StateGraph(AgentState)
        builder.add_node('call_tools_llm', self.call_tools_llm)
        builder.add_node('invoke_tools', self.invoke_tools)
        builder.set_entry_point('call_tools_llm')

        builder.add_conditional_edges('call_tools_llm', Agent.exists_action, {'more_tools': 'invoke_tools', END: END})
        builder.add_edge('invoke_tools', 'call_tools_llm')
        memory = MemorySaver()
        self.graph = builder.compile(checkpointer=memory)

        print(self.graph.get_graph().draw_mermaid())

    @staticmethod
    def exists_action(state: AgentState):
        result = state['messages'][-1]
        if len(result.tool_calls) == 0:
            return END
        return 'more_tools'

    def call_tools_llm(self, state: AgentState):
        messages = state['messages']
        messages = [SystemMessage(content=TOOLS_SYSTEM_PROMPT)] + messages
        message = self._tools_llm.invoke(messages)
        return {'messages': [message]}

    def invoke_tools(self, state: AgentState):
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f'Calling: {t}')
            if not t['name'] in self._tools:  # check for bad tool name from LLM
                print('\n ....bad tool name....')
                result = 'bad tool name, retry'  # instruct LLM to retry if bad
                content = result
            else:
                result = self._tools[t['name']].invoke(t['args'])
                try:
                    content = json.dumps(result)
                except Exception:
                    content = str(result)
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=content))
        print('Back to the model!')
        return {'messages': results}
