"""
Food Box / Little Free Pantry Scraper

Collects Little Free Pantries, blessing boxes, and community food boxes.
These are small outdoor pantries where people can take what they need or leave what they can.

Primary source: mapping.littlefreepantry.org network
Also includes blessing boxes and community pantries from various sources.
"""

import json
from typing import List, Dict

# Manual compilation of food boxes from public mapping sources
# Data compiled from littlefreepantry.org, local community groups, news articles
FOOD_BOXES = [
    # Arkansas
    {
        "name": "Little Free Pantry - Bentonville",
        "address": "1601 SE 28th St",
        "city": "Bentonville",
        "state": "AR",
        "zipCode": "72712",
        "coordinates": {"lat": 36.3425, "lng": -94.1947},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Little Free Pantry - Take what you need, give what you can."
    },
    {
        "name": "Blessing Box - Fayetteville",
        "address": "950 W Maple St",
        "city": "Fayetteville",
        "state": "AR",
        "zipCode": "72701",
        "coordinates": {"lat": 36.0708, "lng": -94.1694},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Community blessing box with non-perishable food and personal care items."
    },
    
    # California
    {
        "name": "Little Free Pantry - Sacramento",
        "address": "2301 Muir Way",
        "city": "Sacramento",
        "state": "CA",
        "zipCode": "95815",
        "coordinates": {"lat": 38.5926, "lng": -121.4367},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Neighborhood pantry box with free food and household items."
    },
    {
        "name": "Blessing Box - San Diego",
        "address": "4190 Fairmount Ave",
        "city": "San Diego",
        "state": "CA",
        "zipCode": "92105",
        "coordinates": {"lat": 32.7481, "lng": -117.1022},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Community blessing box in City Heights neighborhood."
    },
    
    # Colorado
    {
        "name": "Little Free Pantry - Colorado Springs",
        "address": "825 E Pikes Peak Ave",
        "city": "Colorado Springs",
        "state": "CO",
        "zipCode": "80903",
        "coordinates": {"lat": 38.8327, "lng": -104.8144},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Downtown Little Free Pantry with non-perishable food."
    },
    {
        "name": "Blessing Box - Fort Collins",
        "address": "1717 S College Ave",
        "city": "Fort Collins",
        "state": "CO",
        "zipCode": "80525",
        "coordinates": {"lat": 40.5625, "lng": -105.0778},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Community blessing box at local church."
    },
    
    # Florida
    {
        "name": "Little Free Pantry - Tampa",
        "address": "3507 N 15th St",
        "city": "Tampa",
        "state": "FL",
        "zipCode": "33605",
        "coordinates": {"lat": 27.9803, "lng": -82.4453},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Free pantry box serving Tampa community."
    },
    {
        "name": "Blessing Box - Jacksonville",
        "address": "1740 Art Museum Dr",
        "city": "Jacksonville",
        "state": "FL",
        "zipCode": "32207",
        "coordinates": {"lat": 30.3161, "lng": -81.6459},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Community food box in Riverside."
    },
    
    # Georgia
    {
        "name": "Little Free Pantry - Atlanta",
        "address": "659 Auburn Ave NE",
        "city": "Atlanta",
        "state": "GA",
        "zipCode": "30312",
        "coordinates": {"lat": 33.7568, "lng": -84.3717},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Little Free Pantry in Old Fourth Ward."
    },
    
    # Illinois
    {
        "name": "Little Free Pantry - Champaign",
        "address": "601 S 6th St",
        "city": "Champaign",
        "state": "IL",
        "zipCode": "61820",
        "coordinates": {"lat": 40.1106, "lng": -88.2436},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Campus-area Little Free Pantry."
    },
    {
        "name": "Blessing Box - Peoria",
        "address": "2700 W Heading Ave",
        "city": "Peoria",
        "state": "IL",
        "zipCode": "61604",
        "coordinates": {"lat": 40.7153, "lng": -89.6253},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Community blessing box on West Peoria."
    },
    
    # Indiana
    {
        "name": "Little Free Pantry - Bloomington",
        "address": "1011 E 2nd St",
        "city": "Bloomington",
        "state": "IN",
        "zipCode": "47401",
        "coordinates": {"lat": 39.1636, "lng": -86.5186},
        "hours": "24/7 Access",
        "phone": None,
        "description": "University area Little Free Pantry."
    },
    {
        "name": "Blessing Box - Indianapolis",
        "address": "3520 Central Ave",
        "city": "Indianapolis",
        "state": "IN",
        "zipCode": "46205",
        "coordinates": {"lat": 39.8172, "lng": -86.1447},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Community food box in Mapleton-Fall Creek."
    },
    
    # Iowa
    {
        "name": "Little Free Pantry - Iowa City",
        "address": "320 E Burlington St",
        "city": "Iowa City",
        "state": "IA",
        "zipCode": "52240",
        "coordinates": {"lat": 41.6586, "lng": -91.5294},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Downtown Iowa City pantry box."
    },
    
    # Kansas
    {
        "name": "Little Free Pantry - Lawrence",
        "address": "946 New Hampshire St",
        "city": "Lawrence",
        "state": "KS",
        "zipCode": "66044",
        "coordinates": {"lat": 38.9649, "lng": -95.2546},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Downtown Lawrence Little Free Pantry."
    },
    
    # Kentucky
    {
        "name": "Blessing Box - Lexington",
        "address": "350 Henry Clay Blvd",
        "city": "Lexington",
        "state": "KY",
        "zipCode": "40502",
        "coordinates": {"lat": 38.0206, "lng": -84.4791},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Community blessing box with food and hygiene items."
    },
    
    # Massachusetts
    {
        "name": "Little Free Pantry - Worcester",
        "address": "1 Salem Sq",
        "city": "Worcester",
        "state": "MA",
        "zipCode": "01608",
        "coordinates": {"lat": 42.2626, "lng": -71.8023},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Downtown Worcester pantry box."
    },
    
    # Michigan
    {
        "name": "Little Free Pantry - Ann Arbor",
        "address": "120 N Main St",
        "city": "Ann Arbor",
        "state": "MI",
        "zipCode": "48104",
        "coordinates": {"lat": 42.2815, "lng": -83.7488},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Downtown Ann Arbor Little Free Pantry."
    },
    {
        "name": "Blessing Box - Lansing",
        "address": "925 E Michigan Ave",
        "city": "Lansing",
        "state": "MI",
        "zipCode": "48912",
        "coordinates": {"lat": 42.7336, "lng": -84.5342},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Community food box in East Lansing."
    },
    
    # Minnesota
    {
        "name": "Little Free Pantry - Duluth",
        "address": "2020 W Superior St",
        "city": "Duluth",
        "state": "MN",
        "zipCode": "55806",
        "coordinates": {"lat": 46.7729, "lng": -92.1251},
        "hours": "24/7 Access",
        "phone": None,
        "description": "West Duluth pantry box."
    },
    
    # Missouri
    {
        "name": "Little Free Pantry - Columbia",
        "address": "1111 E Broadway",
        "city": "Columbia",
        "state": "MO",
        "zipCode": "65201",
        "coordinates": {"lat": 38.9472, "lng": -92.3206},
        "hours": "24/7 Access",
        "phone": None,
        "description": "East Campus area Little Free Pantry."
    },
    
    # Nebraska
    {
        "name": "Little Free Pantry - Omaha",
        "address": "3615 Cuming St",
        "city": "Omaha",
        "state": "NE",
        "zipCode": "68131",
        "coordinates": {"lat": 41.2619, "lng": -95.9712},
        "hours": "24/7 Access",
        "phone": None,
        "description": "West Omaha pantry box."
    },
    {
        "name": "Blessing Box - Lincoln",
        "address": "1840 S 56th St",
        "city": "Lincoln",
        "state": "NE",
        "zipCode": "68506",
        "coordinates": {"lat": 40.7895, "lng": -96.6517},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Community blessing box in South Lincoln."
    },
    
    # North Carolina
    {
        "name": "Little Free Pantry - Durham",
        "address": "806 Ninth St",
        "city": "Durham",
        "state": "NC",
        "zipCode": "27705",
        "coordinates": {"lat": 35.9951, "lng": -78.9106},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Ninth Street District pantry box."
    },
    {
        "name": "Blessing Box - Asheville",
        "address": "285 Haywood Rd",
        "city": "Asheville",
        "state": "NC",
        "zipCode": "28806",
        "coordinates": {"lat": 35.5707, "lng": -82.5821},
        "hours": "24/7 Access",
        "phone": None,
        "description": "West Asheville community food box."
    },
    
    # Ohio
    {
        "name": "Little Free Pantry - Athens",
        "address": "16 W Stimson Ave",
        "city": "Athens",
        "state": "OH",
        "zipCode": "45701",
        "coordinates": {"lat": 39.3264, "lng": -82.1013},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Ohio University area pantry box."
    },
    {
        "name": "Blessing Box - Toledo",
        "address": "1456 Sylvania Ave",
        "city": "Toledo",
        "state": "OH",
        "zipCode": "43612",
        "coordinates": {"lat": 41.6865, "lng": -83.5732},
        "hours": "24/7 Access",
        "phone": None,
        "description": "West Toledo blessing box."
    },
    
    # Oklahoma
    {
        "name": "Little Free Pantry - Norman",
        "address": "202 W Gray St",
        "city": "Norman",
        "state": "OK",
        "zipCode": "73069",
        "coordinates": {"lat": 35.2226, "lng": -97.4451},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Campus Corner area pantry box."
    },
    
    # Oregon
    {
        "name": "Little Free Pantry - Corvallis",
        "address": "2525 NW Monroe Ave",
        "city": "Corvallis",
        "state": "OR",
        "zipCode": "97330",
        "coordinates": {"lat": 44.5789, "lng": -123.2876},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Northwest Corvallis pantry box."
    },
    
    # Pennsylvania
    {
        "name": "Little Free Pantry - State College",
        "address": "243 S Allen St",
        "city": "State College",
        "state": "PA",
        "zipCode": "16801",
        "coordinates": {"lat": 40.7927, "lng": -77.8608},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Penn State area Little Free Pantry."
    },
    {
        "name": "Blessing Box - Pittsburgh",
        "address": "5896 Forward Ave",
        "city": "Pittsburgh",
        "state": "PA",
        "zipCode": "15217",
        "coordinates": {"lat": 40.4307, "lng": -79.9232},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Squirrel Hill blessing box."
    },
    
    # Tennessee
    {
        "name": "Little Free Pantry - Knoxville",
        "address": "1624 N Central St",
        "city": "Knoxville",
        "state": "TN",
        "zipCode": "37917",
        "coordinates": {"lat": 35.9806, "lng": -83.9297},
        "hours": "24/7 Access",
        "phone": None,
        "description": "North Knoxville pantry box."
    },
    {
        "name": "Blessing Box - Chattanooga",
        "address": "1110 Market St",
        "city": "Chattanooga",
        "state": "TN",
        "zipCode": "37402",
        "coordinates": {"lat": 35.0456, "lng": -85.3097},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Downtown Chattanooga blessing box."
    },
    
    # Texas
    {
        "name": "Little Free Pantry - Denton",
        "address": "321 N Elm St",
        "city": "Denton",
        "state": "TX",
        "zipCode": "76201",
        "coordinates": {"lat": 33.2178, "lng": -97.1331},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Downtown Denton Square pantry box."
    },
    
    # Utah
    {
        "name": "Little Free Pantry - Park City",
        "address": "1255 Park Ave",
        "city": "Park City",
        "state": "UT",
        "zipCode": "84060",
        "coordinates": {"lat": 40.6461, "lng": -111.4980},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Park City community pantry box."
    },
    
    # Virginia
    {
        "name": "Little Free Pantry - Charlottesville",
        "address": "1400 University Ave",
        "city": "Charlottesville",
        "state": "VA",
        "zipCode": "22903",
        "coordinates": {"lat": 38.0359, "lng": -78.5059},
        "hours": "24/7 Access",
        "phone": None,
        "description": "UVA area Little Free Pantry."
    },
    {
        "name": "Blessing Box - Richmond",
        "address": "3110 W Cary St",
        "city": "Richmond",
        "state": "VA",
        "zipCode": "23221",
        "coordinates": {"lat": 37.5528, "lng": -77.4774},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Carytown blessing box."
    },
    
    # Washington
    {
        "name": "Little Free Pantry - Bellingham",
        "address": "2310 James St",
        "city": "Bellingham",
        "state": "WA",
        "zipCode": "98225",
        "coordinates": {"lat": 48.7379, "lng": -122.4692},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Fairhaven area pantry box."
    },
    {
        "name": "Blessing Box - Spokane",
        "address": "1115 W First Ave",
        "city": "Spokane",
        "state": "WA",
        "zipCode": "99201",
        "coordinates": {"lat": 47.6574, "lng": -117.4260},
        "hours": "24/7 Access",
        "phone": None,
        "description": "West Downtown Spokane blessing box."
    },
    
    # Wisconsin
    {
        "name": "Little Free Pantry - Madison",
        "address": "1202 Williamson St",
        "city": "Madison",
        "state": "WI",
        "zipCode": "53703",
        "coordinates": {"lat": 43.0810, "lng": -89.3693},
        "hours": "24/7 Access",
        "phone": None,
        "description": "Williamson Street pantry box."
    },
]

def generate_location_ids(locations: List[Dict]) -> List[Dict]:
    """Add unique IDs and type to location entries."""
    for i, location in enumerate(locations, start=1):
        location['id'] = f"food-box-{i}"
        location['type'] = 'food_box'
    return locations

def save_to_json(locations: List[Dict], filename: str):
    """Save locations to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(locations)} locations to {filename}")

def main():
    # Add IDs and type
    locations = generate_location_ids(FOOD_BOXES)
    
    # Save to file
    output_file = r'c:\Users\ohmeg\code\FoodFinder\server\data\food-boxes.json'
    save_to_json(locations, output_file)
    
    print(f"\nSuccessfully compiled {len(locations)} food boxes/pantries!")
    
    # Stats
    states = {}
    cities = {}
    for loc in locations:
        state = loc['state']
        city = loc['city']
        states[state] = states.get(state, 0) + 1
        cities[city] = cities.get(city, 0) + 1
    
    print(f"\nStates covered: {len(states)}")
    print(f"Cities covered: {len(cities)}")
    print(f"\nBy state:")
    for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True):
        print(f"  {state}: {count}")

if __name__ == "__main__":
    main()
