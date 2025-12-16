"""
Geocode Little Free Pantry locations using free geocoding service

We have 3,941 pantry names but no coordinates.
This script will attempt to geocode them using Nominatim (OpenStreetMap's free geocoder)

Note: Nominatim has rate limits (1 request/second), so this will take ~66 minutes
"""

import json
import time
import os
import requests
from typing import Dict, List

def load_pantry_names(filename='little-pantry-full.json'):
    """Load the scraped pantry names"""
    filepath = os.path.join(
        os.path.dirname(__file__),
        '..',
        'server',
        'data',
        filename
    )
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def geocode_location(name: str, retry_count: int = 3) -> Dict:
    """
    Geocode a location name using Nominatim with retry logic
    Returns dict with lat, lng, and formatted address
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    
    # Extract city/state from common patterns
    query = name
    
    # Try to be smart about the query
    # Many pantries have format: "Name - City" or "Name, City, State"
    if ' - ' in name:
        query = name.split(' - ')[-1]  # Take the part after the dash
    elif ',' in name:
        parts = name.split(',')
        if len(parts) >= 2:
            query = ', '.join(parts[-2:])  # Take last two parts (likely city, state)
    
    # Add "USA" to help narrow search
    query += ", USA"
    
    params = {
        'q': query,
        'format': 'json',
        'limit': 1,
        'addressdetails': 1
    }
    
    headers = {
        'User-Agent': 'FreeFoodFinder/1.0 (nonprofit food assistance locator)'
    }
    
    for attempt in range(retry_count):
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            results = response.json()
            
            if results and len(results) > 0:
                result = results[0]
                address_parts = result.get('address', {})
                
                return {
                    'success': True,
                    'lat': float(result['lat']),
                    'lng': float(result['lon']),
                    'city': address_parts.get('city') or address_parts.get('town') or address_parts.get('village', ''),
                    'state': address_parts.get('state', ''),
                    'country': address_parts.get('country', ''),
                    'formatted_address': result.get('display_name', '')
                }
            else:
                return {'success': False, 'error': 'No results found'}
                
        except requests.exceptions.Timeout:
            if attempt < retry_count - 1:
                time.sleep(2)  # Wait before retry
                continue
            return {'success': False, 'error': 'Timeout after retries'}
        except Exception as e:
            if attempt < retry_count - 1:
                time.sleep(2)
                continue
            return {'success': False, 'error': str(e)}

def geocode_batch(locations: List[Dict], batch_size: int = 100, delay: float = 1.1):
    """
    Geocode a batch of locations with rate limiting
    
    Args:
        locations: List of location dicts
        batch_size: Number to geocode before saving progress
        delay: Seconds between requests (Nominatim requires 1 second minimum)
    """
    geocoded = []
    failed = []
    
    total = len(locations)
    print(f"\nGeocoding {total} locations...")
    print(f"Estimated time: {(total * delay) / 60:.1f} minutes")
    print(f"Rate limit: 1 request per {delay} seconds")
    print(f"Progress will be saved every {batch_size} locations\n")
    
    for i, location in enumerate(locations, 1):
        name = location['name']
        
        print(f"[{i}/{total}] Geocoding: {name[:60]}...")
        
        result = geocode_location(name)
        
        if result['success']:
            location['coordinates'] = {
                'lat': result['lat'],
                'lng': result['lng']
            }
            location['city'] = result['city']
            location['state'] = result['state']
            location['address'] = result['formatted_address']
            geocoded.append(location)
            print(f"  ✓ Found: {result['city']}, {result['state']}")
        else:
            failed.append({
                'name': name,
                'error': result.get('error', 'Unknown')
            })
            print(f"  ✗ Failed: {result.get('error', 'Unknown')}")
        
        # Save progress periodically
        if i % batch_size == 0:
            save_progress(geocoded, failed, i)
            print(f"\n[Progress saved at {i}/{total}]")
            print(f"Success rate: {len(geocoded)}/{i} ({len(geocoded)/i*100:.1f}%)\n")
        
        # Rate limiting
        time.sleep(delay)
    
    return geocoded, failed

def save_progress(geocoded: List[Dict], failed: List[Dict], count: int):
    """Save geocoding progress"""
    output_dir = os.path.join(
        os.path.dirname(__file__),
        '..',
        'server',
        'data'
    )
    
    # Save successful geocodes
    geocoded_file = os.path.join(output_dir, f'little-pantry-geocoded_{count}.json')
    with open(geocoded_file, 'w', encoding='utf-8') as f:
        json.dump(geocoded, f, indent=2, ensure_ascii=False)
    
    # Save failures
    failed_file = os.path.join(output_dir, f'little-pantry-failed_{count}.json')
    with open(failed_file, 'w', encoding='utf-8') as f:
        json.dump(failed, f, indent=2, ensure_ascii=False)
    
    print(f"  → Saved {len(geocoded)} successes and {len(failed)} failures")

def main():
    print("=" * 70)
    print("Little Free Pantry Geocoding Script")
    print("=" * 70)
    
    # Check for command line argument for sample size
    import sys
    sample_size = None
    if len(sys.argv) > 1:
        try:
            sample_size = int(sys.argv[1])
            print(f"\nSample mode: Geocoding first {sample_size} pantries")
        except ValueError:
            print(f"\nInvalid sample size: {sys.argv[1]}")
            return
    else:
        print("\nThis will geocode all 3,941 pantry names to get coordinates")
        print("\nWARNING: This will take ~66 minutes due to rate limits!")
    
    print("You can stop at any time - progress is saved every 100 locations")
    print("=" * 70)
    
    # Ask for confirmation (skip if sample mode for automation)
    if sample_size and sample_size <= 100:
        print(f"\n[Auto-starting sample geocoding of {sample_size} locations...]")
        response = 'yes'
    elif sample_size:
        response = input(f"\nGeocode first {sample_size} pantries? (yes/no): ").strip().lower()
    else:
        response = input("\nStart geocoding ALL pantries? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Cancelled.")
        return
    
    # Load locations
    print("\nLoading pantry names...")
    locations = load_pantry_names()
    print(f"Loaded {len(locations)} locations")
    
    # Limit to sample if specified
    if sample_size:
        locations = locations[:sample_size]
        print(f"Processing sample of {len(locations)} locations")
    
    # Start geocoding
    start_time = time.time()
    geocoded, failed = geocode_batch(locations)
    elapsed = time.time() - start_time
    
    # Final save
    save_progress(geocoded, failed, len(locations))
    
    # Summary
    print("\n" + "=" * 70)
    print("GEOCODING COMPLETE!")
    print("=" * 70)
    print(f"Time elapsed: {elapsed/60:.1f} minutes")
    print(f"Successfully geocoded: {len(geocoded)} ({len(geocoded)/len(locations)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(locations)*100:.1f}%)")
    
    if geocoded:
        # Count by state
        states = {}
        for loc in geocoded:
            state = loc.get('state', 'Unknown')
            states[state] = states.get(state, 0) + 1
        
        print(f"\nStates covered: {len(states)}")
        print("\nTop 10 states:")
        for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {state}: {count}")
    
    print("\nNext step: Merge these into all-locations.json")

if __name__ == "__main__":
    main()
