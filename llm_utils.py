import os
from dotenv import load_dotenv
from langchain_cerebras import ChatCerebras
from langchain_tavily import TavilySearch
import json
import re

# Load environment variables
load_dotenv()

def create_cerebras_llm():
    """Create and configure ChatCerebras LLM instance"""
    try:
        # Get API key from environment variables
        api_key = os.getenv("CEREBRAS_API_KEY")
        
        if not api_key:
            raise ValueError("CEREBRAS_API_KEY not found in environment variables")
        
        # Initialize the ChatCerebras model as shown in documentation
        # https://python.langchain.com/docs/integrations/chat/cerebras/
        llm = ChatCerebras(
            cerebras_api_key=api_key,
            temperature=0.7,
            max_tokens=8000,
            model="llama-4-scout-17b-16e-instruct"  # Use an appropriate Cerebras model
        )
        
        return llm
    
    except Exception as e:
        print(f"Error creating Cerebras LLM: {e}")
        raise

# Create the LLM instance globally or pass it around
# Creating it once might be more efficient if called frequently
try:
    llm_instance = create_cerebras_llm()
except Exception as e:
    llm_instance = None
    print(f"Failed to initialize Cerebras LLM: {e}. Interpretation will fail.")

def get_tavily_search(query, profile, chart_data):
    """Perform web search for astrological information related to the query using Tavily"""
    try:
        # Get API key from environment variables
        api_key = os.getenv("TAVILY_API_KEY")
        
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        # Extract relevant information from the chart data for search context
        # Handle potential missing keys gracefully
        sun_sign = chart_data.get('planets', {}).get('Sun', {}).get('sign', 'Unknown')
        moon_sign = chart_data.get('planets', {}).get('Moon', {}).get('sign', 'Unknown')
        rising_sign = chart_data.get('ascendant', {}).get('sign', 'Unknown')
        
        # Create an enhanced query with astrological context
        enhanced_query = f"Astrology: {query} for person with Sun in {sun_sign}, Moon in {moon_sign}, and {rising_sign} rising"
        
        # Initialize Tavily search with proper configuration
        # https://python.langchain.com/docs/integrations/tools/tavily_search/
        search_tool = TavilySearch(
            tavily_api_key=api_key,
            max_results=3, # Reduced results for brevity
            topic="general",
            include_raw_content=False,
            include_images=False,
        )
        
        print(f"Executing Tavily Search: {enhanced_query}")
        # Execute the search using the invoke method
        search_results = search_tool.invoke({"query": enhanced_query})
        print(f"Tavily Response: {search_results}")
        
        # Format the results as a readable text
        formatted_results = "\n\n--- Web Search Insights ---\n"
        
        # Check the structure of search_results (it might be a list of dicts or just a string)
        results_to_process = []
        if isinstance(search_results, list):
            results_to_process = search_results
        elif isinstance(search_results, dict) and "results" in search_results:
             results_to_process = search_results["results"]
        elif isinstance(search_results, str): # Handle case where Tavily returns a string summary
             formatted_results += search_results
             return formatted_results
        else:
            formatted_results += "No parseable search results found."
            return formatted_results
            
        if not results_to_process:
             formatted_results += "No results found."
             return formatted_results

        for i, result in enumerate(results_to_process):
            # Ensure result is a dictionary before accessing keys
            if isinstance(result, dict):
                title = result.get("title", f"Result {i+1}")
                url = result.get("url", "No URL")
                content = result.get("content", "No content available")
                
                formatted_results += f"Source {i+1}: {title}\n"
                formatted_results += f"URL: {url}\n"
                formatted_results += f"Content Summary: {content[:250]}...\n\n"
            else:
                 formatted_results += f"Result {i+1}: {str(result)[:250]}...\n\n" # Display raw result if not dict
        
        return formatted_results
    
    except Exception as e:
        print(f"Error performing Tavily search: {e}")
        return f"\nError: Could not perform web search - {str(e)}"

def format_astrological_analysis(chart_data):
    """Format natal chart data into a human-readable astrological analysis"""
    try:
        # Use .get() with default values for safety
        planets = chart_data.get('planets', {})
        aspects = chart_data.get('aspects', [])
        houses = chart_data.get('houses', {})
        
        analysis = "Astrological Profile Summary (Generated):\n\n" # Note: Added '(Generated)'
        
        # Add basic chart information safely
        sun_info = planets.get('Sun', {})
        moon_info = planets.get('Moon', {})
        asc_info = chart_data.get('ascendant', {})
        mc_info = chart_data.get('midheaven', {})

        analysis += f"Sun Sign: {sun_info.get('sign', 'N/A')} {sun_info.get('position_in_sign', ''):.1f}°\n" if sun_info else "Sun Sign: N/A\n"
        analysis += f"Moon Sign: {moon_info.get('sign', 'N/A')} {moon_info.get('position_in_sign', ''):.1f}°\n" if moon_info else "Moon Sign: N/A\n"
        analysis += f"Rising Sign (Ascendant): {asc_info.get('sign', 'N/A')}\n" if asc_info else "Rising Sign: N/A\n"
        analysis += f"Midheaven: {mc_info.get('sign', 'N/A')}\n\n" if mc_info else "Midheaven: N/A\n\n"
        
        # Add planetary positions
        analysis += "Planetary Positions (Generated):\n"
        for planet, data in planets.items():
            if isinstance(data, dict): # Ensure data is a dictionary
                 retrograde = " (R)" if data.get('is_retrograde', False) else ""
                 sign = data.get('sign', 'N/A')
                 pos = data.get('position_in_sign', '')
                 pos_str = f"{pos:.1f}°" if isinstance(pos, (int, float)) else ""
                 analysis += f"{planet}: {sign} {pos_str}{retrograde}\n"
            else:
                 analysis += f"{planet}: Error in data format\n"
        
        # Add major aspects (if any were generated)
        if aspects:
            analysis += "\nMajor Aspects (Generated):\n"
            major_aspect_types = ['Conjunction', 'Opposition', 'Trine', 'Square']
            # Filter aspects ensuring they are dicts with required keys
            filtered_aspects = [
                a for a in aspects 
                if isinstance(a, dict) and 
                   a.get('aspect') in major_aspect_types and 
                   'planet1' in a and 'planet2' in a and 'orb' in a
            ]
            
            for aspect in filtered_aspects[:5]:  # Limit aspects
                planet1 = aspect['planet1']
                planet2 = aspect['planet2']
                aspect_type = aspect['aspect']
                orb = aspect['orb']
                orb_str = f"{orb:.1f}°" if isinstance(orb, (int, float)) else ""
                
                analysis += f"{planet1} {aspect_type} {planet2} (Orb: {orb_str})\n"
        else:
             analysis += "\nNo major aspects generated.\n"
        
        return analysis
    
    except Exception as e:
        print(f"Error formatting astrological analysis: {e}")
        return "Error: Could not generate astrological analysis summary."

# Replace the placeholder LLM call with the actual Cerebras implementation
def call_llm_api(prompt: str) -> str:
    """
    Sends a prompt to the configured Cerebras LLM API and returns the response.
    """
    global llm_instance
    if llm_instance is None:
        print("Error: Cerebras LLM instance is not available.")
        return "Error: LLM not initialized. Cannot generate interpretation."
        
    print(f"--- Sending Prompt to Cerebras LLM ---")
    # print(prompt) # Optionally print the full prompt for debugging
    print(f"Prompt length: {len(prompt)} characters")
    print("--- End of LLM Prompt ---")
    
    try:
        # Use the invoke method for LangChain components
        response = llm_instance.invoke(prompt)
        
        # The response object might be complex, extract the content
        # Adjust based on the actual structure of ChatCerebras response
        if hasattr(response, 'content'):
            interpretation = response.content
        elif isinstance(response, str):
            interpretation = response
        else:
            print(f"Warning: Unexpected LLM response format: {type(response)}")
            interpretation = str(response) # Fallback to string representation
            
        print("--- Received LLM Response ---")
        return interpretation
        
    except Exception as e:
        print(f"Cerebras LLM API Error: {e}")
        # Provide more context if available from the exception
        return f"Error retrieving interpretation from LLM: {e}"

# We assume get_coordinates_from_tavily exists here as imported in astro_utils.py
# Add any necessary imports for Tavily if not already present
# from tavily import TavilyClient # Example if using Tavily Python SDK
# tavily_client = TavilyClient(api_key="YOUR_TAVILY_API_KEY")

def get_coordinates_from_tavily(location_name: str) -> dict | None:
    """
    Gets coordinates using the Tavily API.
    (Keep your existing implementation or adapt as needed)
    """
    print(f"Querying Tavily for coordinates of: {location_name}")
    # Replace with your actual Tavily API call logic
    # Example using a hypothetical search:
    # try:
    #     response = tavily_client.search(query=f"coordinates of {location_name}", search_depth="basic")
    #     # Parse response to find coordinates - This depends heavily on Tavily's output format
    #     # Placeholder logic:
    #     if response and 'results' in response and len(response['results']) > 0:
    #         # Hypothetical: Assume first result might have coordinates
    #         # You'll need to adapt this based on actual Tavily output
    #         # This part is highly speculative without knowing Tavily's exact response structure for coordinates
    #         # Maybe look for structured data or parse text?
    #         coords = parse_coordinates_from_tavily_result(response['results'][0]) # Implement this parsing function
    #         if coords:
    #              return {'lat': coords['lat'], 'lng': coords['lng']}
    # except Exception as e:
    #     print(f"Tavily API error: {e}")

    print(f"Tavily fallback for {location_name} did not yield coordinates.")
    return None # Placeholder

# Example helper function (needs implementation based on Tavily response)
# def parse_coordinates_from_tavily_result(result: dict) -> dict | None:
#     # Implement logic to extract lat/lng from a Tavily search result item
#     # This might involve regex, searching for keywords, etc.
#     return None 