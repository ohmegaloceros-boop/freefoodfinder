"""
Colorado Food Bank Data Scraper

This script collects food bank data for Colorado from various sources.
Data is formatted to match the FreeFoodFinder location schema.
"""

import json
from typing import List, Dict

# Manual data entry of major Colorado food banks from public sources
# Data compiled from Feeding America, Food Bank of the Rockies, and local organizations

COLORADO_FOODBANKS = [
    {
        "name": "Food Bank of the Rockies - Main Distribution Center",
        "type": "foodbank",
        "address": "10700 E 45th Ave",
        "city": "Denver",
        "state": "CO",
        "zipCode": "80239",
        "coordinates": {"lat": 39.7800, "lng": -104.8697},
        "hours": "Monday-Friday 8:00 AM - 4:00 PM",
        "phone": "(303) 371-9250",
        "description": "Food Bank of the Rockies is the largest hunger-relief organization in the Rocky Mountain region, serving communities throughout Colorado and Wyoming."
    },
    {
        "name": "Metro Caring",
        "type": "foodbank",
        "address": "1100 E 18th Ave",
        "city": "Denver",
        "state": "CO",
        "zipCode": "80218",
        "coordinates": {"lat": 39.7445, "lng": -104.9759},
        "hours": "Monday, Wednesday, Friday 9:00 AM - 3:00 PM",
        "phone": "(303) 860-7200",
        "description": "Metro Caring provides emergency food, clothing, and supportive services to low-income individuals and families in Denver."
    },
    {
        "name": "Community Food Share",
        "type": "foodbank",
        "address": "650 S Taylor Ave",
        "city": "Louisville",
        "state": "CO",
        "zipCode": "80027",
        "coordinates": {"lat": 39.9625, "lng": -105.1319},
        "hours": "Monday-Friday 9:00 AM - 5:00 PM",
        "phone": "(303) 652-3663",
        "description": "Community Food Share serves Boulder and Broomfield counties, providing food to partner agencies and direct distribution."
    },
    {
        "name": "Volunteers of America Food Bank",
        "type": "foodbank",
        "address": "2877 Lawrence St",
        "city": "Denver",
        "state": "CO",
        "zipCode": "80205",
        "coordinates": {"lat": 39.7600, "lng": -104.9766},
        "hours": "Monday-Friday 9:00 AM - 4:00 PM",
        "phone": "(303) 297-0408",
        "description": "VOA provides food assistance, clothing, and supportive services to individuals and families in need throughout metro Denver."
    },
    {
        "name": "SAME Cafe",
        "type": "foodbank",
        "address": "2023 E Colfax Ave",
        "city": "Denver",
        "state": "CO",
        "zipCode": "80206",
        "coordinates": {"lat": 39.7403, "lng": -104.9709},
        "hours": "Tuesday-Saturday 11:00 AM - 2:00 PM",
        "phone": "(303) 388-7263",
        "description": "So All May Eat (SAME) Cafe is a donation-based, fair-exchange restaurant providing healthy meals to everyone."
    },
    {
        "name": "Hunger Free Colorado",
        "type": "foodbank",
        "address": "9900 E Iliff Ave",
        "city": "Denver",
        "state": "CO",
        "zipCode": "80231",
        "coordinates": {"lat": 39.6707, "lng": -104.8708},
        "hours": "Monday-Friday 8:30 AM - 5:00 PM",
        "phone": "(303) 595-0207",
        "description": "Hunger Free Colorado connects people to food resources and advocates for policies to end hunger statewide."
    },
    {
        "name": "Brother Jeff's Cultural Center Food Pantry",
        "type": "foodbank",
        "address": "2851 Welton St",
        "city": "Denver",
        "state": "CO",
        "zipCode": "80205",
        "coordinates": {"lat": 39.7577, "lng": -104.9761},
        "hours": "Thursday 12:00 PM - 3:00 PM",
        "phone": "(720) 295-2384",
        "description": "Community food pantry providing fresh and shelf-stable foods to families in Northeast Denver."
    },
    {
        "name": "St. Francis Center",
        "type": "foodbank",
        "address": "2323 Curtis St",
        "city": "Denver",
        "state": "CO",
        "zipCode": "80205",
        "coordinates": {"lat": 39.7544, "lng": -104.9822},
        "hours": "Monday-Friday 7:30 AM - 3:00 PM",
        "phone": "(303) 297-8855",
        "description": "St. Francis Center provides daily meals, food assistance, clothing, healthcare, and supportive services to people experiencing poverty and homelessness."
    },
    {
        "name": "Servicios de La Raza",
        "type": "foodbank",
        "address": "3131 W 7th Ave",
        "city": "Denver",
        "state": "CO",
        "zipCode": "80204",
        "coordinates": {"lat": 39.7283, "lng": -105.0214},
        "hours": "Monday-Friday 8:00 AM - 5:00 PM",
        "phone": "(303) 458-5851",
        "description": "Provides food assistance, case management, and social services to Latino families and other communities in need."
    },
    {
        "name": "Growhaus Food Pantry",
        "type": "foodbank",
        "address": "4751 York St",
        "city": "Denver",
        "state": "CO",
        "zipCode": "80216",
        "coordinates": {"lat": 39.7899, "lng": -104.9619},
        "hours": "Tuesday, Thursday 12:00 PM - 5:00 PM; Saturday 10:00 AM - 1:00 PM",
        "phone": "(303) 296-9968",
        "description": "Indoor farm and food hub providing fresh produce and food assistance to the Elyria-Swansea neighborhood."
    },
    {
        "name": "Colorado Springs Food Bank",
        "type": "foodbank",
        "address": "5039 Edison Ave",
        "city": "Colorado Springs",
        "state": "CO",
        "zipCode": "80915",
        "coordinates": {"lat": 38.8610, "lng": -104.7522},
        "hours": "Monday-Friday 9:00 AM - 4:00 PM",
        "phone": "(719) 296-6995",
        "description": "Care and Share Food Bank serves Southern Colorado, distributing millions of pounds of food annually."
    },
    {
        "name": "Weld Food Bank",
        "type": "foodbank",
        "address": "315 S 11th Ave",
        "city": "Greeley",
        "state": "CO",
        "zipCode": "80631",
        "coordinates": {"lat": 40.4180, "lng": -104.7042},
        "hours": "Monday-Friday 8:00 AM - 4:30 PM",
        "phone": "(970) 352-6522",
        "description": "Serves Weld County with food distribution, nutrition education, and hunger relief programs."
    },
    {
        "name": "Food Bank for Larimer County",
        "type": "foodbank",
        "address": "1301 Blue Spruce Dr",
        "city": "Fort Collins",
        "state": "CO",
        "zipCode": "80524",
        "coordinates": {"lat": 40.5482, "lng": -105.0415},
        "hours": "Monday-Friday 10:00 AM - 4:00 PM",
        "phone": "(970) 493-4477",
        "description": "Provides food assistance to individuals and families throughout Larimer County."
    },
    {
        "name": "Pueblo Community Soup Kitchen",
        "type": "foodbank",
        "address": "107 S Union Ave",
        "city": "Pueblo",
        "state": "CO",
        "zipCode": "81003",
        "coordinates": {"lat": 38.2644, "lng": -104.6091},
        "hours": "Monday-Friday 11:30 AM - 1:00 PM",
        "phone": "(719) 545-8407",
        "description": "Provides hot meals and food pantry services to those in need in Pueblo."
    },
    {
        "name": "Summit County Community & Senior Center Food Pantry",
        "type": "foodbank",
        "address": "83 Nancy's Pl",
        "city": "Frisco",
        "state": "CO",
        "zipCode": "80443",
        "coordinates": {"lat": 39.5744, "lng": -106.1047},
        "hours": "Monday-Friday 8:00 AM - 5:00 PM",
        "phone": "(970) 668-2940",
        "description": "Provides food assistance to residents of Summit County mountain communities."
    }
]

def generate_location_ids(locations: List[Dict]) -> List[Dict]:
    """Add unique IDs to location entries."""
    for i, location in enumerate(locations, start=1):
        location['id'] = f"co-foodbank-{i}"
    return locations

def save_to_json(locations: List[Dict], filename: str):
    """Save locations to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(locations)} locations to {filename}")

def main():
    # Add IDs to locations
    locations = generate_location_ids(COLORADO_FOODBANKS)
    
    # Save to file
    output_file = r'c:\Users\ohmeg\code\FoodFinder\server\data\colorado-foodbanks.json'
    save_to_json(locations, output_file)
    
    print(f"\nSuccessfully compiled {len(locations)} Colorado food banks!")
    print(f"Cities covered: {', '.join(set(loc['city'] for loc in locations))}")

if __name__ == "__main__":
    main()
