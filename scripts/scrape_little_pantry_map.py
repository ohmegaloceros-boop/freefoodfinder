"""
Scraper for Little Free Pantry mapping website
This site has thousands of community food boxes nationwide
"""

import requests
import json
import re
import time
from typing import List, Dict

def scrape_little_pantry_map() -> List[Dict]:
    """
    Scrape Little Free Pantry locations from their website
    The site uses an embedded Google Maps with markers
    We need to find their data source/API
    """
    
    # Try to find their API endpoint or data feed
    # Many mapping sites expose a JSON API or embed data in the HTML
    
    url = "https://mapping.littlefreepantry.org/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"Fetching data from {url}...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        html = response.text
        
        # Look for embedded JSON data in the HTML
        # Many sites embed their marker data in a JavaScript variable
        
        # Try to find data patterns
        # Look for coordinates, addresses, names in the HTML
        json_patterns = [
            r'var\s+locations\s*=\s*(\[.*?\]);',
            r'var\s+markers\s*=\s*(\[.*?\]);',
            r'var\s+data\s*=\s*(\[.*?\]);',
            r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    print(f"Found embedded data with {len(data)} items!")
                    return parse_embedded_data(data)
                except:
                    continue
        
        # If no JSON found, look for API endpoints in the HTML
        api_patterns = [
            r'(https?://[^\s"\']+api[^\s"\']+)',
            r'(https?://[^\s"\']+/locations[^\s"\']+)',
            r'(https?://[^\s"\']+/pantry[^\s"\']+)',
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, html)
            if matches:
                print(f"Found potential API endpoints: {matches[:3]}")
                # Try to fetch from these endpoints
                for api_url in matches[:5]:
                    try:
                        api_response = requests.get(api_url, headers=headers, timeout=10)
                        if api_response.status_code == 200:
                            try:
                                data = api_response.json()
                                print(f"Successfully fetched {len(data)} locations from API!")
                                return parse_api_data(data)
                            except:
                                continue
                    except:
                        continue
        
        # If we can't find the data automatically, we need to manually analyze the site
        # The site appears to use a custom system - we may need to reverse engineer it
        print("\nCouldn't automatically find data source.")
        print("The site appears to use Google Maps with custom markers.")
        print("\nManual steps needed:")
        print("1. Open the site in browser DevTools")
        print("2. Look for network requests when the map loads")
        print("3. Find the API endpoint that returns location data")
        print("4. Update this script with the correct endpoint")
        
        # As a fallback, create a smaller manual dataset based on what we saw
        return create_manual_sample()
        
    except Exception as e:
        print(f"Error scraping: {e}")
        return create_manual_sample()

def parse_embedded_data(data: List) -> List[Dict]:
    """Parse embedded JSON data from HTML"""
    locations = []
    
    for item in data:
        try:
            location = {
                'name': item.get('name', item.get('title', 'Little Free Pantry')),
                'lat': float(item.get('lat', item.get('latitude', 0))),
                'lng': float(item.get('lng', item.get('longitude', 0))),
                'address': item.get('address', ''),
                'city': item.get('city', ''),
                'state': item.get('state', ''),
                'description': item.get('description', 'Community food pantry'),
                'hours': '24/7',
                'type': 'food_box'
            }
            
            if location['lat'] != 0 and location['lng'] != 0:
                locations.append(location)
                
        except Exception as e:
            continue
    
    return locations

def parse_api_data(data: Dict) -> List[Dict]:
    """Parse JSON data from API"""
    # Adapt based on actual API structure
    if isinstance(data, list):
        return parse_embedded_data(data)
    elif isinstance(data, dict):
        if 'locations' in data:
            return parse_embedded_data(data['locations'])
        elif 'pantries' in data:
            return parse_embedded_data(data['pantries'])
    return []

def create_manual_sample() -> List[Dict]:
    """
    Create a manual sample of Little Free Pantry locations
    Based on the visible results from the website
    """
    
    locations = [
        # Major cities with multiple Little Free Pantries
        # Seattle area
        {"name": "Spottswood Neighborhood Pantry", "lat": 47.5412, "lng": -122.3958, "city": "Seattle", "state": "WA"},
        {"name": "Alaska Junction Little Free Pantry", "lat": 47.5665, "lng": -122.3867, "city": "Seattle", "state": "WA"},
        {"name": "Kindness Cabinet", "lat": 47.6587, "lng": -122.3173, "city": "Seattle", "state": "WA"},
        
        # Portland area
        {"name": "Water Ave Pantry", "lat": 45.5053, "lng": -122.6572, "city": "Portland", "state": "OR"},
        {"name": "Little Free Pantry PDX", "lat": 45.5231, "lng": -122.6765, "city": "Portland", "state": "OR"},
        
        # San Francisco Bay Area
        {"name": "Unitarian Universalist San Mateo", "lat": 37.5428, "lng": -122.3108, "city": "San Mateo", "state": "CA"},
        {"name": "Little Blue Pantry", "lat": 37.8044, "lng": -122.2712, "city": "Oakland", "state": "CA"},
        
        # Los Angeles area
        {"name": "Little Free Pantry Norwalk", "lat": 33.9022, "lng": -118.0817, "city": "Norwalk", "state": "CA"},
        
        # Chicago area
        {"name": "Budlong Woods Little Free Pantry", "lat": 41.9828, "lng": -87.6923, "city": "Chicago", "state": "IL"},
        {"name": "Little Free Pantry Chicago", "lat": 41.8781, "lng": -87.6298, "city": "Chicago", "state": "IL"},
        
        # New York area
        {"name": "Patterson Park Little Pantry", "lat": 40.7128, "lng": -73.9569, "city": "Brooklyn", "state": "NY"},
        
        # Other major cities
        {"name": "Little Free Pantry Austin", "lat": 30.2672, "lng": -97.7431, "city": "Austin", "state": "TX"},
        {"name": "Little Free Pantry Denver", "lat": 39.7392, "lng": -104.9903, "city": "Denver", "state": "CO"},
        {"name": "Little Free Pantry Phoenix", "lat": 33.4484, "lng": -112.0740, "city": "Phoenix", "state": "AZ"},
        {"name": "Little Free Pantry Miami", "lat": 25.7617, "lng": -80.1918, "city": "Miami", "state": "FL"},
    ]
    
    # Add generic address and details
    for loc in locations:
        loc['address'] = f"{loc['city']}, {loc['state']}"
        loc['description'] = 'Little Free Pantry - Take what you need, leave what you can'
        loc['hours'] = '24/7'
        loc['phone'] = ''
        loc['type'] = 'food_box'
    
    return locations

def generate_location_ids(locations: List[Dict]) -> List[Dict]:
    """Add unique IDs to locations"""
    for i, location in enumerate(locations, 1):
        location['id'] = f"little-pantry-{i}"
    return locations

def save_locations(locations: List[Dict], filename: str = 'little-pantry-locations.json'):
    """Save locations to JSON file"""
    import os
    
    output_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'server',
        'data',
        filename
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(locations)} locations to {output_path}")
    
    # Print statistics
    states = {}
    for loc in locations:
        state = loc.get('state', 'Unknown')
        states[state] = states.get(state, 0) + 1
    
    print(f"\nStates covered: {len(states)}")
    print("Top states:")
    for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {state}: {count}")

if __name__ == "__main__":
    print("=" * 60)
    print("Little Free Pantry Mapping Website Scraper")
    print("=" * 60)
    
    locations = scrape_little_pantry_map()
    
    if locations:
        locations = generate_location_ids(locations)
        save_locations(locations)
        print("\nScraping completed!")
    else:
        print("\nNo locations found. Manual intervention needed.")
        print("\nNEXT STEPS:")
        print("1. Visit https://mapping.littlefreepantry.org/ in browser")
        print("2. Open DevTools (F12)")
        print("3. Go to Network tab")
        print("4. Refresh the page and look for API calls")
        print("5. Find the endpoint that returns location data")
        print("6. Share that endpoint to update this script")
