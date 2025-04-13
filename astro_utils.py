import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import math
import os
import random # Added for random generation

# Import the Tavily coordinate function and LLM call function
from llm_utils import get_coordinates_from_tavily, call_llm_api

# Set up geocoding services with proper user agent
geolocator = Nominatim(user_agent="astrology-ai-consultation")
tf = TimezoneFinder()

# Planets and celestial bodies (simplified list for random generation)
CELESTIAL_BODIES_NAMES = [
    'Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
    'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto',
    'North Node', 'Chiron'
]

# Zodiac signs
ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 
    'Leo', 'Virgo', 'Libra', 'Scorpio', 
    'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

def get_location_coordinates(location_name):
    """Get latitude and longitude for a location name (Kept for context)"""
    try:
        # First try with Nominatim
        print(f"Attempting to geocode '{location_name}' with Nominatim...")
        location = geolocator.geocode(location_name)
        if location:
            # Debug info
            print(f"Nominatim found: {location.address}")
            print(f"Latitude: {location.latitude}, Longitude: {location.longitude}")

            return {
                'lat': location.latitude,
                'lng': location.longitude,
                'formatted_address': location.address
            }
        else:
            print(f"Nominatim could not geocode '{location_name}'. Trying Tavily...")
            # Fallback to Tavily
            tavily_coords = get_coordinates_from_tavily(location_name)
            if tavily_coords:
                # Ensure Tavily returns expected keys
                if 'lat' in tavily_coords and 'lng' in tavily_coords:
                    return {
                        'lat': tavily_coords['lat'],
                        'lng': tavily_coords['lng'],
                        'formatted_address': location_name # Use original name as address
                    }
                else:
                    print("Tavily response missing lat/lng.")
                    return None
            else:
                print(f"Tavily could not find coordinates for '{location_name}'.")
                # Last resort: Fallback coordinates for Ahmedabad, India if relevant
                if "ahmedabad" in location_name.lower() and "india" in location_name.lower():
                    print("Using hardcoded fallback coordinates for Ahmedabad, India")
                    return {
                        'lat': 23.0225,
                        'lng': 72.5714,
                        'formatted_address': "Ahmedabad, Gujarat, India (Fallback)"
                    }
                return None

    except Exception as e:
        print(f"Error during geocoding process for '{location_name}': {e}")
        # Attempt Tavily even if Nominatim raised an exception
        print("Attempting Tavily due to Nominatim error...")
        tavily_coords = get_coordinates_from_tavily(location_name)
        if tavily_coords and 'lat' in tavily_coords and 'lng' in tavily_coords:
             return {
                 'lat': tavily_coords['lat'],
                 'lng': tavily_coords['lng'],
                 'formatted_address': location_name # Use original name as address
             }
        print("Tavily fallback failed after Nominatim error.")
        return None

def get_timezone_for_location(lat, lng):
    """Get timezone string for coordinates (Kept for context)"""
    try:
        if lat is None or lng is None:
            print("Warning: Latitude or longitude is None for timezone lookup")
            return 'UTC' # Default to UTC if coords are missing
            
        # Basic coordinate validation
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            print(f"Warning: Invalid coordinates for timezone lookup: lat={lat}, lng={lng}. Defaulting to UTC.")
            return 'UTC'
            
        tz_name = tf.timezone_at(lat=lat, lng=lng)
        if not tz_name:
            print(f"No timezone found for coordinates: lat={lat}, lng={lng}. Defaulting to UTC.")
             # Simple fallback based on longitude (very rough)
            if lng > -30 and lng < 30: return 'Europe/London' # Rough Europe/Africa
            if lng >= 30 and lng < 120: return 'Asia/Kolkata' # Rough Asia
            if lng <= -30 and lng > -150: return 'America/New_York' # Rough Americas
            return 'UTC' # Default
            
        return tz_name
    except Exception as e:
        print(f"Error getting timezone: {e}. Defaulting to UTC.")
        return 'UTC'

def generate_random_chart_structure():
    """Generates a dictionary with random astrological placements."""
    print("Generating random chart structure (No astronomical calculation)")
    planets = {}
    for body_name in CELESTIAL_BODIES_NAMES:
        sign_index = random.randint(0, 11)
        position_in_sign = random.uniform(0, 29.99)
        sign = ZODIAC_SIGNS[sign_index]
        # Approx 15% chance of being retrograde (excluding Sun/Moon/Nodes)
        is_retro = False
        if body_name not in ['Sun', 'Moon', 'North Node']:
            is_retro = random.random() < 0.15

        planets[body_name] = {
            'longitude': (sign_index * 30) + position_in_sign,
            'latitude': random.uniform(-5, 5),
            'distance': random.uniform(0.5, 30),
            'speed': random.uniform(-1, 2) * (1 if not is_retro else -1),
            'sign': sign,
            'position_in_sign': position_in_sign,
            'is_retrograde': is_retro,
            'heliocentric_longitude': None
        }

    # Generate random house cusps (degrees 0-359.99)
    # Start with a random Ascendant degree
    asc_position = random.uniform(0, 359.99)
    asc_sign_index = int(asc_position / 30)
    asc_sign = ZODIAC_SIGNS[asc_sign_index]
    
    # Generate other cusps somewhat realistically spaced, but still random
    house_cusps = [0.0] * 12 # Initialize list for 12 cusps (use index 0-11)
    house_cusps[0] = asc_position
    current_cusp = asc_position
    for i in range(1, 12):
        # Add a random spacing (e.g., 20-40 degrees) for semi-plausible look
        spacing = random.uniform(20, 40) 
        next_cusp = (current_cusp + spacing) % 360
        house_cusps[i] = next_cusp
        current_cusp = next_cusp
        
    # Ensure cusps are sorted for certain drawing logic if needed (optional)
    # Note: Real house calculations don't always result in sorted cusps depending on system/latitude
    
    # Determine MC based on 10th house cusp (index 9)
    mc_position = house_cusps[9]
    mc_sign_index = int(mc_position / 30)
    mc_sign = ZODIAC_SIGNS[mc_sign_index]

    return {
        'planets': planets,
        'aspects': [],
        'houses': {
             'cusps': house_cusps, # List of 12 cusp degrees
             # Storing sign names might be redundant now but keep for compatibility if needed elsewhere
             'ascendant_sign': asc_sign, 
             'mc_sign': mc_sign 
        },
        'ascendant': {
            'position': asc_position,
            'sign': asc_sign
        },
        'midheaven': {
            'position': mc_position,
            'sign': mc_sign
        }
    }

def calculate_natal_chart(birth_date, birth_time, birth_location):
    """Generates a natal chart using random data and LLM interpretation."""
    try:
        # 1. Get location data (still useful for context)
        location_data = get_location_coordinates(birth_location)
        lat, lng, formatted_address = None, None, birth_location # Defaults
        if location_data:
            lat = location_data.get('lat')
            lng = location_data.get('lng')
            formatted_address = location_data.get('formatted_address', birth_location)
        else:
             print(f"Warning: Could not find coordinates for {birth_location}. Proceeding without precise location.")

        # 2. Get timezone (still useful for context)
        timezone_str = get_timezone_for_location(lat, lng)

        # 3. Generate Random Astrological Data
        random_chart = generate_random_chart_structure()

        # 4. Compile the chart data dictionary
        chart_data = {
            'date': birth_date,
            'time': birth_time if birth_time else '12:00 (Assumed)',
            'location': formatted_address,
            'latitude': lat,
            'longitude': lng,
            'timezone': timezone_str,
            'julian_day': None, # Not calculated
            'houses': random_chart['houses'], # Use random houses
            'planets': random_chart['planets'], # Use random planets
            'aspects': random_chart['aspects'], # Use empty aspects
            'ascendant': random_chart['ascendant'], # Use random ascendant
            'midheaven': random_chart['midheaven'] # Use random midheaven
        }

        # 5. Generate LLM Interpretation based on the random data
        # Ensure the interpretation function is robust to the new structure
        chart_data['interpretation'] = generate_llm_interpretation(chart_data)
        
        return chart_data
    
    except Exception as e:
        print(f"Error generating random natal chart: {e}")
        # Return a minimal error structure
        return {
             'error': f"Failed to generate chart: {e}",
             'date': birth_date,
             'time': birth_time,
             'location': birth_location,
             'interpretation': "Could not generate interpretation due to an error."
        }

def generate_llm_interpretation(chart_data):
    """Generates an astrological interpretation using an LLM based on provided chart data."""
    try:
        # Prepare a summary of the chart for the LLM prompt
        prompt = f"Provide a plausible-sounding astrological interpretation for a generated natal chart with the following details (Note: Placements are randomly generated, not calculated astronomically):\n\n"
        prompt += f"Birth Date: {chart_data.get('date', 'Unknown')}\n"
        prompt += f"Birth Time: {chart_data.get('time', 'Unknown')}\n"
        prompt += f"Birth Location: {chart_data.get('location', 'Unknown')}\n\n"

        # Key placements (handle potential None values)
        planets = chart_data.get('planets', {})
        sun_info = planets.get('Sun', {})
        moon_info = planets.get('Moon', {})
        asc_info = chart_data.get('ascendant', {})

        if sun_info and 'sign' in sun_info:
            prompt += f"Sun: {sun_info['sign']}\n"
        if moon_info and 'sign' in moon_info:
            prompt += f"Moon: {moon_info['sign']}\n"
        if asc_info and 'sign' in asc_info:
            prompt += f"Ascendant (Rising Sign): {asc_info['sign']}\n\n"

        # Add planet positions (simplified)
        prompt += "Planetary Positions (Generated Signs):\n"
        for planet, data in planets.items():
             # Check if data is a dictionary and has the 'sign' key
            if isinstance(data, dict) and 'sign' in data:
                retro = " (Retrograde)" if data.get('is_retrograde') else ""
                prompt += f"- {planet}: {data['sign']}{retro}\n"
            else:
                 prompt += f"- {planet}: Sign Unavailable\n"
        prompt += "\n"

        # Aspects are no longer generated, so remove this section from the prompt
        # if chart_data.get('aspects'):
        #    prompt += "Major Aspects (Generated):\n"
        #    ...

        prompt += "Based *only* on these generated sign placements (ignore degrees and houses), offer a brief, general, and positive-toned personality sketch focusing on potential strengths and tendencies. Acknowledge that this is based on random data, not a real calculation."

        # Call the LLM API
        interpretation = call_llm_api(prompt)
        return interpretation

    except Exception as e:
        print(f"Error generating LLM interpretation: {e}")
        return "Error: Could not generate interpretation." 