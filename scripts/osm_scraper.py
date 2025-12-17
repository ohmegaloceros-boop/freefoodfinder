"""
OpenStreetMap Food Bank Scraper

Uses Overpass API (OSM) to find food banks, pantries, and soup kitchens nationwide.
100% FREE - No API key required!

Coverage: OpenStreetMap has community-contributed data, typically better in urban areas.
Expected results: 5,000-15,000 locations across the US.
"""

import json
import requests
import time
from typing import List, Dict, Optional

# Overpass API endpoint (free, no auth required)
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# OpenStreetMap tags for food assistance locations
OSM_QUERIES = {
    'foodbank': '[amenity=social_facility][social_facility=food_bank]',
    'soup_kitchen': '[amenity=social_facility][social_facility=soup_kitchen]',
    'food_pantry': '[amenity=social_facility][social_facility=food_pantry]',
    'community_fridge': '[amenity=community_fridge]',
    # Additional tags to catch more locations
    'social_facility_general': '[amenity=social_facility][~"social_facility:for"~"food|meal"]',
    'foodbank_by_name': '[name~"food bank|food pantry|food shelf",i]',
    'feeding_program': '[amenity~"community_centre|social_centre"][~"description|note"~"food|meal|pantry",i]',
}

# US bounding box
US_BBOX = "(24.5,-125.0,49.4,-66.9)"  # South, West, North, East

class OSMScraper:
    def __init__(self):
        self.locations = []
        self.seen_osm_ids = set()
        
    def query_overpass(self, query: str) -> List[Dict]:
        """Query the Overpass API."""
        overpass_query = f"""
        [out:json][timeout:90];
        (
          node{query}{US_BBOX};
          way{query}{US_BBOX};
          relation{query}{US_BBOX};
        );
        out center;
        """
        
        try:
            print(f"Querying OSM for: {query}")
            response = requests.post(OVERPASS_URL, data={'data': overpass_query})
            
            if response.status_code == 200:
                data = response.json()
                elements = data.get('elements', [])
                print(f"  Found {len(elements)} results")
                return elements
            else:
                print(f"  Error {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"  Request failed: {e}")
            return []
    
    def parse_address(self, tags: Dict) -> Dict:
        """Parse OSM address tags into components."""
        return {
            'address': tags.get('addr:street', ''),
            'city': tags.get('addr:city', ''),
            'state': tags.get('addr:state', ''),
            'zipCode': tags.get('addr:postcode', '')
        }
    
    def get_location_type(self, tags: Dict) -> str:
        """Determine location type from OSM tags."""
        social_facility = tags.get('social_facility', '')
        amenity = tags.get('amenity', '')
        
        if social_facility == 'soup_kitchen' or 'soup' in tags.get('name', '').lower():
            return 'foodbank'
        elif social_facility == 'food_pantry' or 'pantry' in tags.get('name', '').lower():
            return 'foodbank'
        elif amenity == 'community_fridge' or 'fridge' in tags.get('name', '').lower():
            return 'community_fridge'
        else:
            return 'foodbank'
    
    def get_coordinates(self, element: Dict) -> Optional[Dict]:
        """Extract coordinates from OSM element."""
        if element['type'] == 'node':
            return {
                'lat': element.get('lat'),
                'lng': element.get('lon')
            }
        elif 'center' in element:
            return {
                'lat': element['center'].get('lat'),
                'lng': element['center'].get('lon')
            }
        return None
    
    def parse_hours(self, tags: Dict) -> str:
        """Parse opening hours from OSM tags."""
        hours = tags.get('opening_hours', '')
        if hours:
            return hours
        return "Call for hours"
    
    def convert_to_app_format(self, element: Dict) -> Optional[Dict]:
        """Convert OSM element to app format."""
        try:
            # Skip if already processed
            osm_id = f"{element['type']}/{element['id']}"
            if osm_id in self.seen_osm_ids:
                return None
            self.seen_osm_ids.add(osm_id)
            
            tags = element.get('tags', {})
            
            # Get name
            name = tags.get('name') or tags.get('official_name') or 'Food Assistance Location'
            
            # Get coordinates
            coords = self.get_coordinates(element)
            if not coords or not coords['lat'] or not coords['lng']:
                return None
            
            # Parse address
            address_parts = self.parse_address(tags)
            
            # Skip if missing critical info
            if not address_parts['city'] or not address_parts['state']:
                return None
            
            # Get other details
            location_type = self.get_location_type(tags)
            hours = self.parse_hours(tags)
            phone = tags.get('phone') or tags.get('contact:phone')
            website = tags.get('website') or tags.get('contact:website')
            
            description = f"Food assistance location from OpenStreetMap community data."
            if website:
                description += f" Website: {website}"
            
            return {
                'name': name,
                'type': location_type,
                'address': address_parts['address'],
                'city': address_parts['city'],
                'state': address_parts['state'],
                'zipCode': address_parts['zipCode'],
                'coordinates': coords,
                'hours': hours,
                'phone': phone,
                'description': description,
                'osm_id': osm_id
            }
        except Exception as e:
            print(f"Error converting element: {e}")
            return None
    
    def scrape_all(self):
        """Scrape all OSM queries."""
        print("Starting OpenStreetMap scrape...")
        print(f"Searching US bounding box: {US_BBOX}\n")
        
        for name, query in OSM_QUERIES.items():
            print(f"\n=== Searching for {name} ===")
            elements = self.query_overpass(query)
            
            for element in elements:
                location = self.convert_to_app_format(element)
                if location:
                    self.locations.append(location)
            
            print(f"Total unique locations so far: {len(self.locations)}")
            
            # Rate limiting - be nice to free API
            time.sleep(2)
        
        print(f"\n=== Scrape Complete ===")
        print(f"Total locations found: {len(self.locations)}")
    
    def save_results(self, filename: str):
        """Save results to JSON file."""
        # Add IDs
        for i, location in enumerate(self.locations, start=1):
            location['id'] = f"osm-{i}"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.locations, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(self.locations)} locations to {filename}")
        
        # Print stats
        states = {}
        cities = {}
        types = {}
        
        for loc in self.locations:
            state = loc['state']
            city = loc['city']
            loc_type = loc['type']
            
            states[state] = states.get(state, 0) + 1
            cities[city] = cities.get(city, 0) + 1
            types[loc_type] = types.get(loc_type, 0) + 1
        
        print(f"\n=== Statistics ===")
        print(f"States covered: {len(states)}")
        print(f"Cities covered: {len(cities)}")
        print(f"\nTop 10 states:")
        for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {state}: {count}")
        
        print(f"\nBy type:")
        for loc_type, count in types.items():
            print(f"  {loc_type}: {count}")

def main():
    print("OpenStreetMap Food Bank Scraper")
    print("=" * 50)
    print("100% FREE - No API key required!")
    print("This will take 2-3 minutes to complete.\n")
    
    # Initialize scraper
    scraper = OSMScraper()
    
    # Run scraper
    scraper.scrape_all()
    
    # Save results
    output_file = r'c:\Users\ohmeg\code\FoodFinder\server\data\osm-locations.json'
    scraper.save_results(output_file)
    
    print("\n=== Next Steps ===")
    print("1. Review the results in osm-locations.json")
    print("2. Update merge_locations.py to merge OSM data")
    print("3. Run: python scripts/merge_locations.py")
    print("4. Restart your dev server!")

if __name__ == "__main__":
    main()
