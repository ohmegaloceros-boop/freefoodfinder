"""
Address-Only Scraper Template

This scraper collects food bank information WITHOUT geocoding.
Just scrapes names, addresses, and other details.
Then use batch_geocode.py to add coordinates later.
"""

import json
from typing import List, Dict

def scrape_addresses() -> List[Dict]:
    """
    Scrape food bank addresses without geocoding.
    
    This is much faster since we're not making API calls.
    Replace this function with your actual scraping logic.
    """
    
    # Example: Manual data entry (replace with actual web scraping)
    locations = [
        {
            "name": "Example Food Bank 1",
            "address": "123 Main St",
            "city": "Denver",
            "state": "CO",
            "zipCode": "80202",
            "phone": "(555) 123-4567",
            "website": "https://example.com",
            "hours": "Mon-Fri 9-5",
            "type": "foodbank",
            "description": "Example food bank serving the community"
        },
        {
            "name": "Example Food Pantry 2",
            "address": "456 Oak Ave",
            "city": "Boulder",
            "state": "CO",
            "zipCode": "80301",
            "phone": "(555) 987-6543",
            "type": "foodbank",
            "description": "Local food pantry"
        }
        # Add more locations...
    ]
    
    return locations

def scrape_from_website(url: str) -> List[Dict]:
    """
    Example function to scrape from a website.
    
    This would use BeautifulSoup or similar to extract:
    - Name
    - Address
    - City, State, ZIP
    - Phone
    - Website
    - Hours
    
    NO geocoding here - just collecting the data!
    """
    import requests
    from bs4 import BeautifulSoup
    
    locations = []
    
    try:
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Example: Find all food bank listings
        # (This would be customized for each website)
        listings = soup.find_all('div', class_='food-bank-listing')
        
        for listing in listings:
            location = {
                'name': listing.find('h2').text.strip(),
                'address': listing.find(class_='address').text.strip(),
                'city': listing.find(class_='city').text.strip(),
                'state': listing.find(class_='state').text.strip(),
                'zipCode': listing.find(class_='zip').text.strip(),
                'phone': listing.find(class_='phone').text.strip() if listing.find(class_='phone') else '',
                'type': 'foodbank'
            }
            locations.append(location)
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    
    return locations

def scrape_from_csv(filename: str) -> List[Dict]:
    """
    Load addresses from a CSV file.
    
    Expected columns: name, address, city, state, zipCode, phone, website
    """
    import csv
    
    locations = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            location = {
                'name': row.get('name', ''),
                'address': row.get('address', ''),
                'city': row.get('city', ''),
                'state': row.get('state', ''),
                'zipCode': row.get('zipCode', ''),
                'phone': row.get('phone', ''),
                'website': row.get('website', ''),
                'hours': row.get('hours', 'Call for hours'),
                'type': row.get('type', 'foodbank'),
                'description': row.get('description', '')
            }
            locations.append(location)
    
    return locations

def save_addresses(locations: List[Dict], output_file: str):
    """Save addresses to JSON (no coordinates yet)."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(locations)} locations to {output_file}")
    print("\nNext steps:")
    print(f"1. Review the addresses in {output_file}")
    print(f"2. Run: python scripts/batch_geocode.py {output_file} geocoded-{output_file}")
    print(f"3. Check the geocoded results")
    print(f"4. Merge into all-locations.json")

def main():
    """
    Example usage - customize this for your data source!
    """
    print("Address-Only Scraper")
    print("=" * 60)
    print("Choose your data source:")
    print("1. Manual data entry")
    print("2. Scrape from website")
    print("3. Load from CSV")
    print("=" * 60)
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    locations = []
    output_file = "raw-addresses.json"
    
    if choice == "1":
        print("\nUsing example manual data...")
        locations = scrape_addresses()
        
    elif choice == "2":
        url = input("Enter website URL: ").strip()
        print(f"\nScraping {url}...")
        locations = scrape_from_website(url)
        
    elif choice == "3":
        filename = input("Enter CSV filename: ").strip()
        print(f"\nLoading {filename}...")
        locations = scrape_from_csv(filename)
    
    else:
        print("Invalid choice!")
        return
    
    if locations:
        save_addresses(locations, output_file)
    else:
        print("No locations found!")

if __name__ == "__main__":
    main()
