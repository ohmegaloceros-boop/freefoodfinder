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
    
    # Load food boxes
    food_boxes = load_json(r'c:\Users\ohmeg\code\FoodFinder\server\data\food-boxes.json')
    print(f"Food boxes: {len(food_boxes)}")
    
    # Merge
    all_locations.extend(food_boxes)
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
