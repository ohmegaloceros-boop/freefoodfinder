"""
Feeding America Food Bank Scraper

Scrapes food bank locations from Feeding America's website.
This is the authoritative source for food banks affiliated with Feeding America.
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Optional
import re

class FeedingAmericaScraper:
    def __init__(self):
        self.locations = []
        self.base_url = "https://www.feedingamerica.org"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def geocode_address(self, address: str, city: str, state: str, zipcode: str = '') -> Optional[Dict]:
        """Geocode an address using Nominatim."""
        full_address = f"{address}, {city}, {state} {zipcode}".strip()
        
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': full_address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'us'
            }
            headers = {
                'User-Agent': 'FoodFinderApp/1.0 (contact@example.com)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    return {
                        'lat': float(results[0]['lat']),
                        'lng': float(results[0]['lon'])
                    }
            
            # Retry with just city, state
            params['q'] = f"{city}, {state}"
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                results = response.json()
                if results:
                    return {
                        'lat': float(results[0]['lat']),
                        'lng': float(results[0]['lon'])
                    }
            
            return None
        except Exception as e:
            print(f"  Geocoding error: {e}")
            return None
    
    def scrape_member_list(self) -> List[Dict]:
        """
        Scrape the Feeding America member food bank directory.
        
        Note: This scrapes their public directory page. If this doesn't work,
        we can use their search widget or API endpoint if available.
        """
        locations = []
        
        # Try the find food page
        search_url = f"{self.base_url}/find-your-local-foodbank"
        
        try:
            print(f"Fetching Feeding America directory...")
            response = requests.get(search_url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"Error: Status code {response.status_code}")
                return self.use_hardcoded_data()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find the data in script tags (many sites embed JSON)
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'foodbank' in script.string.lower():
                    # Try to extract JSON data
                    try:
                        # Look for JSON objects
                        json_matches = re.findall(r'\{[^{}]*"name"[^{}]*"address"[^{}]*\}', script.string)
                        for match in json_matches:
                            try:
                                data = json.loads(match)
                                locations.append(data)
                            except:
                                continue
                    except:
                        continue
            
            if locations:
                print(f"Found {len(locations)} locations from embedded data")
                return locations
            
            # If no embedded data, look for list items or divs
            foodbank_items = soup.find_all(['div', 'li'], class_=re.compile('food.*bank|member', re.I))
            
            if not foodbank_items:
                print("Could not find food bank listings in HTML structure")
                return self.use_hardcoded_data()
            
            print(f"Found {len(foodbank_items)} potential entries")
            
        except Exception as e:
            print(f"Error scraping: {e}")
            return self.use_hardcoded_data()
        
        return locations
    
    def use_hardcoded_data(self) -> List[Dict]:
        """
        Fallback: Use known Feeding America member food banks.
        Data compiled from public sources.
        """
        print("\nUsing curated Feeding America member food bank data...")
        
        # Major Feeding America members by state (with pre-geocoded coordinates)
        hardcoded_banks = [
            {
                "name": "Food Bank For New York City",
                "address": "39 Broadway, 10th Floor",
                "city": "New York",
                "state": "NY",
                "zipCode": "10006",
                "phone": "(212) 566-7855",
                "website": "https://www.foodbanknyc.org",
                "coordinates": {"lat": 40.7074, "lng": -74.0113}
            },
            {
                "name": "Los Angeles Regional Food Bank",
                "address": "1734 E 41st St",
                "city": "Los Angeles",
                "state": "CA",
                "zipCode": "90058",
                "phone": "(323) 234-3030",
                "website": "https://www.lafoodbank.org",
                "coordinates": {"lat": 34.0073, "lng": -118.2267}
            },
            {
                "name": "Greater Chicago Food Depository",
                "address": "4100 W Ann Lurie Pl",
                "city": "Chicago",
                "state": "IL",
                "zipCode": "60632",
                "phone": "(773) 247-3663",
                "website": "https://www.chicagosfoodbank.org",
                "coordinates": {"lat": 41.8234, "lng": -87.7284}
            },
            {
                "name": "Houston Food Bank",
                "address": "535 Portwall St",
                "city": "Houston",
                "state": "TX",
                "zipCode": "77029",
                "phone": "(713) 547-3663",
                "website": "https://www.houstonfoodbank.org",
                "coordinates": {"lat": 29.7328, "lng": -95.2956}
            },
            {
                "name": "Greater Boston Food Bank",
                "address": "70 South Bay Ave",
                "city": "Boston",
                "state": "MA",
                "zipCode": "02118",
                "phone": "(617) 427-5200",
                "website": "https://www.gbfb.org",
                "coordinates": {"lat": 42.3357, "lng": -71.0615}
            },
            {
                "name": "Capital Area Food Bank (DC)",
                "address": "4900 Puerto Rico Ave NE",
                "city": "Washington",
                "state": "DC",
                "zipCode": "20017",
                "phone": "(202) 644-9800",
                "website": "https://www.capitalareafoodbank.org",
                "coordinates": {"lat": 38.9354, "lng": -76.9968}
            },
            {
                "name": "North Texas Food Bank",
                "address": "3677 Mapleshade Ln",
                "city": "Plano",
                "state": "TX",
                "zipCode": "75075",
                "phone": "(469) 399-1000",
                "website": "https://www.ntfb.org",
                "coordinates": {"lat": 33.0440, "lng": -96.7764}
            },
            {
                "name": "Food Bank of the Rockies",
                "address": "10700 E 45th Ave",
                "city": "Denver",
                "state": "CO",
                "zipCode": "80239",
                "phone": "(303) 371-9250",
                "website": "https://www.foodbankrockies.org",
                "coordinates": {"lat": 39.7800, "lng": -104.8697}
            },
            {
                "name": "San Francisco-Marin Food Bank",
                "address": "900 Pennsylvania Ave",
                "city": "San Francisco",
                "state": "CA",
                "zipCode": "94107",
                "phone": "(415) 282-1900",
                "website": "https://www.sfmfoodbank.org",
                "coordinates": {"lat": 37.7599, "lng": -122.3958}
            },
            {
                "name": "Atlanta Community Food Bank",
                "address": "732 Joseph E Lowery Blvd NW",
                "city": "Atlanta",
                "state": "GA",
                "zipCode": "30318",
                "phone": "(404) 892-9822",
                "website": "https://www.acfb.org",
                "coordinates": {"lat": 33.7672, "lng": -84.4180}
            },
            {
                "name": "Second Harvest Food Bank of Orange County",
                "address": "8014 Marine Way",
                "city": "Irvine",
                "state": "CA",
                "zipCode": "92618",
                "phone": "(949) 653-2900",
                "website": "https://www.feedoc.org",
                "coordinates": {"lat": 33.6748, "lng": -117.8603}
            },
            {
                "name": "Feeding America Tampa Bay",
                "address": "4702 Transport Dr",
                "city": "Tampa",
                "state": "FL",
                "zipCode": "33605",
                "phone": "(813) 254-1190",
                "website": "https://www.feedingtampabay.org",
                "coordinates": {"lat": 27.9728, "lng": -82.4254}
            },
            {
                "name": "Food Bank of the Southern Tier",
                "address": "388 Upper Oakwood Ave",
                "city": "Elmira Heights",
                "state": "NY",
                "zipCode": "14903",
                "phone": "(607) 796-6061",
                "website": "https://www.foodbankst.org",
                "coordinates": {"lat": 42.1306, "lng": -76.8211}
            },
            {
                "name": "Three Square Food Bank (Las Vegas)",
                "address": "4190 N Pecos Rd",
                "city": "Las Vegas",
                "state": "NV",
                "zipCode": "89115",
                "phone": "(702) 644-3663",
                "website": "https://www.threesquare.org",
                "coordinates": {"lat": 36.1985, "lng": -115.1186}
            },
            {
                "name": "Oregon Food Bank",
                "address": "7900 SE Mcloughlin Blvd",
                "city": "Portland",
                "state": "OR",
                "zipCode": "97202",
                "phone": "(503) 282-0555",
                "website": "https://www.oregonfoodbank.org",
                "coordinates": {"lat": 45.4694, "lng": -122.6437}
            },
            {
                "name": "Food Bank of Central & Eastern North Carolina",
                "address": "1924 Capital Blvd",
                "city": "Raleigh",
                "state": "NC",
                "zipCode": "27604",
                "phone": "(919) 875-0707",
                "website": "https://www.foodbankcenc.org",
                "coordinates": {"lat": 35.8051, "lng": -78.6168}
            },
            {
                "name": "Food Bank of the Heartland (Omaha)",
                "address": "10525 J St",
                "city": "Omaha",
                "state": "NE",
                "zipCode": "68127",
                "phone": "(402) 331-1213",
                "website": "https://www.foodbankheartland.org",
                "coordinates": {"lat": 41.2131, "lng": -96.0861}
            },
            {
                "name": "Community Food Bank of New Jersey",
                "address": "31 Evans Terminal",
                "city": "Hillside",
                "state": "NJ",
                "zipCode": "07205",
                "phone": "(908) 355-3663",
                "website": "https://www.cfbnj.org",
                "coordinates": {"lat": 40.6998, "lng": -74.2249}
            },
            {
                "name": "Gleaners Community Food Bank (Detroit)",
                "address": "2131 Beaufait St",
                "city": "Detroit",
                "state": "MI",
                "zipCode": "48207",
                "phone": "(313) 923-3535",
                "website": "https://www.gcfb.org",
                "coordinates": {"lat": 42.3566, "lng": -83.0089}
            },
            {
                "name": "Second Harvest Heartland (Minneapolis)",
                "address": "1140 Gervais Ave",
                "city": "Maplewood",
                "state": "MN",
                "zipCode": "55109",
                "phone": "(651) 484-5117",
                "website": "https://www.2harvest.org",
                "coordinates": {"lat": 45.0063, "lng": -93.0186}
            }
        ]
        
        return hardcoded_banks
    
    def process_locations(self, raw_data: List[Dict]) -> List[Dict]:
        """Process locations (now with pre-geocoded coordinates)."""
        processed = []
        
        print(f"\nProcessing {len(raw_data)} food banks...")
        
        for i, bank in enumerate(raw_data, 1):
            print(f"\n[{i}/{len(raw_data)}] {bank.get('name', 'Unknown')}")
            
            # Check if already has coordinates
            coords = bank.get('coordinates')
            
            if not coords:
                # Try to geocode
                coords = self.geocode_address(
                    bank.get('address', ''),
                    bank.get('city', ''),
                    bank.get('state', ''),
                    bank.get('zipCode', '')
                )
                
                if not coords:
                    print(f"  ⚠ Could not geocode, skipping")
                    continue
                    
                print(f"  ✓ Geocoded: {coords['lat']}, {coords['lng']}")
                time.sleep(1)  # Rate limiting
            else:
                print(f"  ✓ Using pre-geocoded coordinates: {coords['lat']}, {coords['lng']}")
            
            location = {
                'name': bank.get('name', 'Food Bank'),
                'type': 'foodbank',
                'address': bank.get('address', ''),
                'city': bank.get('city', ''),
                'state': bank.get('state', ''),
                'zipCode': bank.get('zipCode', ''),
                'coordinates': coords,
                'phone': bank.get('phone', ''),
                'website': bank.get('website', ''),
                'description': f"Feeding America member food bank serving {bank.get('city', 'the community')}.",
                'hours': bank.get('hours', 'Contact for hours'),
                'source': 'Feeding America'
            }
            
            processed.append(location)
        
        return processed
    
    def scrape(self):
        """Main scraping method."""
        print("Feeding America Food Bank Scraper")
        print("=" * 50)
        
        # Get raw data
        raw_data = self.scrape_member_list()
        
        if not raw_data:
            print("\nNo data found. Using fallback data.")
            raw_data = self.use_hardcoded_data()
        
        # Process and geocode
        self.locations = self.process_locations(raw_data)
        
        print(f"\n=== Scrape Complete ===")
        print(f"Successfully processed: {len(self.locations)} food banks")
    
    def save_results(self, filename: str):
        """Save results to JSON file."""
        # Add IDs
        for i, location in enumerate(self.locations, start=1):
            location['id'] = f"fa-{i}"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.locations, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(self.locations)} locations to {filename}")
        
        # Print stats
        states = {}
        for loc in self.locations:
            state = loc['state']
            states[state] = states.get(state, 0) + 1
        
        print(f"\n=== Statistics ===")
        print(f"States covered: {len(states)}")
        print(f"\nBreakdown by state:")
        for state, count in sorted(states.items()):
            print(f"  {state}: {count}")

def main():
    scraper = FeedingAmericaScraper()
    scraper.scrape()
    
    output_file = r'c:\Users\ohmeg\code\FoodFinder\server\data\feeding-america-locations.json'
    scraper.save_results(output_file)
    
    print("\n=== Next Steps ===")
    print("1. Review feeding-america-locations.json")
    print("2. Run OSM scraper: python scripts/osm_scraper.py")
    print("3. Merge all data: python scripts/merge_locations.py")

if __name__ == "__main__":
    main()
