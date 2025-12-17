"""
Batch Geocoder

Takes a JSON file with addresses and geocodes them in batches with proper rate limiting.
Saves progress so you can resume if interrupted.
"""

import json
import requests
import time
from pathlib import Path
from typing import Dict, Optional

class BatchGeocoder:
    def __init__(self, input_file: str, output_file: str):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.geocoded = []
        self.failed = []
        self.progress_file = self.output_file.with_suffix('.progress.json')
        
    def load_progress(self):
        """Load previous progress if exists."""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.geocoded = data.get('geocoded', [])
                self.failed = data.get('failed', [])
                print(f"Resuming from previous progress: {len(self.geocoded)} geocoded, {len(self.failed)} failed")
        
    def save_progress(self):
        """Save current progress."""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump({
                'geocoded': self.geocoded,
                'failed': self.failed
            }, f, indent=2)
    
    def geocode_address(self, address: str, city: str, state: str, zipcode: str = '') -> Optional[Dict]:
        """Geocode a single address using Nominatim."""
        # Try full address first
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
                'User-Agent': 'FoodFinderApp/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    return {
                        'lat': float(results[0]['lat']),
                        'lng': float(results[0]['lon'])
                    }
            
            # If full address fails, try just city, state
            if address:  # Only retry if we had a street address
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
            print(f"    Error: {e}")
            return None
    
    def geocode_batch(self, batch_size: int = 50, delay: float = 1.5):
        """Geocode all locations in batches."""
        # Load input data
        with open(self.input_file, 'r', encoding='utf-8') as f:
            locations = json.load(f)
        
        print(f"\nLoaded {len(locations)} locations to geocode")
        
        # Load progress
        self.load_progress()
        
        # Track which IDs we've already processed
        processed_ids = set()
        for loc in self.geocoded:
            if 'original_id' in loc:
                processed_ids.add(loc['original_id'])
        for loc in self.failed:
            if 'original_id' in loc:
                processed_ids.add(loc['original_id'])
        
        # Process remaining locations
        to_process = []
        for i, loc in enumerate(locations):
            loc_id = loc.get('id', i)
            if loc_id not in processed_ids:
                loc['original_id'] = loc_id
                to_process.append(loc)
        
        print(f"Remaining to geocode: {len(to_process)}")
        
        if not to_process:
            print("All locations already processed!")
            return
        
        # Geocode in batches
        for i, location in enumerate(to_process, 1):
            print(f"\n[{i}/{len(to_process)}] {location.get('name', 'Unknown')}")
            
            # Check if already has coordinates
            if location.get('coordinates'):
                print("  ✓ Already has coordinates, skipping")
                self.geocoded.append(location)
                continue
            
            # Geocode
            coords = self.geocode_address(
                location.get('address', ''),
                location.get('city', ''),
                location.get('state', ''),
                location.get('zipCode', '')
            )
            
            if coords:
                location['coordinates'] = coords
                self.geocoded.append(location)
                print(f"  ✓ {coords['lat']}, {coords['lng']}")
            else:
                self.failed.append(location)
                print(f"  ✗ Failed to geocode")
            
            # Save progress every 10 locations
            if i % 10 == 0:
                self.save_progress()
                print(f"\n  [Progress saved: {len(self.geocoded)} succeeded, {len(self.failed)} failed]")
            
            # Rate limiting - be nice to Nominatim
            time.sleep(delay)
        
        # Final save
        self.save_progress()
        
        print(f"\n{'='*60}")
        print(f"Geocoding complete!")
        print(f"{'='*60}")
        print(f"Successfully geocoded: {len(self.geocoded)}")
        print(f"Failed: {len(self.failed)}")
        print(f"Success rate: {len(self.geocoded)/(len(self.geocoded)+len(self.failed))*100:.1f}%")
    
    def save_results(self):
        """Save final geocoded results."""
        # Add sequential IDs
        for i, loc in enumerate(self.geocoded, 1):
            loc['id'] = i
            # Remove the original_id helper field
            if 'original_id' in loc:
                del loc['original_id']
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.geocoded, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(self.geocoded)} locations to {self.output_file}")
        
        # Save failed locations for review
        if self.failed:
            failed_file = self.output_file.with_name(f"{self.output_file.stem}-failed.json")
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump(self.failed, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(self.failed)} failed locations to {failed_file}")

def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python batch_geocode.py <input_file> <output_file> [batch_size] [delay_seconds]")
        print("\nExample:")
        print("  python batch_geocode.py raw-addresses.json geocoded-locations.json")
        print("  python batch_geocode.py raw-addresses.json geocoded-locations.json 50 1.5")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    batch_size = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    delay = float(sys.argv[4]) if len(sys.argv) > 4 else 1.5
    
    print("=" * 60)
    print("BATCH GEOCODER")
    print("=" * 60)
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    print(f"Batch size: {batch_size}")
    print(f"Delay: {delay}s between requests")
    print("=" * 60)
    
    geocoder = BatchGeocoder(input_file, output_file)
    
    try:
        geocoder.geocode_batch(batch_size, delay)
        geocoder.save_results()
        
        print("\n✓ Complete! You can now merge these results into all-locations.json")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted! Progress has been saved.")
        print(f"Run the same command again to resume from where you left off.")
        geocoder.save_progress()
    except Exception as e:
        print(f"\n\nError: {e}")
        print("Progress has been saved.")
        geocoder.save_progress()

if __name__ == "__main__":
    main()
