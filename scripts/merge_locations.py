"""
Merge Colorado food banks into all-locations.json
"""

import json

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    # Load existing locations
    all_locations = load_json(r'c:\Users\ohmeg\code\FoodFinder\server\data\all-locations.json')
    print(f"Current locations: {len(all_locations)}")
    
    # Load OSM locations
    osm_locations = load_json(r'c:\Users\ohmeg\code\FoodFinder\server\data\osm-locations.json')
    print(f"OSM locations: {len(osm_locations)}")
    
    # Merge
    all_locations.extend(osm_locations)
    print(f"Total after merge: {len(all_locations)}")
    
    # Save back to all-locations.json
    save_json(all_locations, r'c:\Users\ohmeg\code\FoodFinder\server\data\all-locations.json')
    print("Successfully updated all-locations.json!")
    
    # Print stats
    cities = {}
    for loc in all_locations:
        city = loc['city']
        cities[city] = cities.get(city, 0) + 1
    
    print(f"\nLocations by city:")
    for city, count in sorted(cities.items()):
        print(f"  {city}: {count}")

if __name__ == "__main__":
    main()
