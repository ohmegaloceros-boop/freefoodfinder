"""
Master Data Collection Script

Runs all food bank data scrapers and merges results:
1. Feeding America scraper (authoritative food banks)
2. OpenStreetMap scraper (community-contributed data)
3. Merges with existing data

Expected total: 2,000-10,000 new locations
"""

import json
import subprocess
import sys
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'server' / 'data'
SCRIPTS_DIR = BASE_DIR / 'scripts'

def run_script(script_name, description):
    """Run a Python script and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}\n")
    
    script_path = SCRIPTS_DIR / script_name
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            text=True,
            check=True
        )
        print(f"\n✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} failed with error")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error running {description}")
        print(f"Error: {e}")
        return False

def merge_all_data():
    """Merge all collected data sources."""
    print(f"\n{'='*60}")
    print("Merging all data sources...")
    print(f"{'='*60}\n")
    
    # Load existing data
    all_locations_file = DATA_DIR / 'all-locations.json'
    existing = []
    
    if all_locations_file.exists():
        with open(all_locations_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        print(f"Existing locations: {len(existing)}")
    
    # Load new data sources
    sources = [
        ('feeding-america-locations.json', 'Feeding America'),
        ('osm-locations.json', 'OpenStreetMap')
    ]
    
    new_locations = []
    seen_coords = set()
    
    # Add existing locations to seen set
    for loc in existing:
        coords = loc.get('coordinates', {})
        lat = coords.get('lat')
        lng = coords.get('lng')
        if lat and lng:
            # Round to 4 decimals (~11m precision)
            coord_key = (round(lat, 4), round(lng, 4))
            seen_coords.add(coord_key)
    
    # Load and deduplicate new sources
    for filename, source_name in sources:
        filepath = DATA_DIR / filename
        
        if not filepath.exists():
            print(f"⚠ {source_name} data not found, skipping...")
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        
        print(f"\n{source_name}: {len(source_data)} locations")
        
        added = 0
        duplicates = 0
        
        for loc in source_data:
            coords = loc.get('coordinates', {})
            lat = coords.get('lat')
            lng = coords.get('lng')
            
            if not lat or not lng:
                continue
            
            # Check for duplicates
            coord_key = (round(lat, 4), round(lng, 4))
            
            if coord_key in seen_coords:
                duplicates += 1
                continue
            
            seen_coords.add(coord_key)
            new_locations.append(loc)
            added += 1
        
        print(f"  Added: {added}")
        print(f"  Duplicates skipped: {duplicates}")
    
    # Combine all data
    all_locations = existing + new_locations
    
    # Regenerate IDs
    for i, loc in enumerate(all_locations, start=1):
        loc['id'] = i
    
    # Save merged data
    with open(all_locations_file, 'w', encoding='utf-8') as f:
        json.dump(all_locations, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✓ Merge complete!")
    print(f"{'='*60}")
    print(f"Previous total: {len(existing)}")
    print(f"New locations added: {len(new_locations)}")
    print(f"Final total: {len(all_locations)}")
    
    # Stats
    states = {}
    types = {}
    
    for loc in all_locations:
        state = loc.get('state', 'Unknown')
        loc_type = loc.get('type', 'Unknown')
        states[state] = states.get(state, 0) + 1
        types[loc_type] = types.get(loc_type, 0) + 1
    
    print(f"\nCoverage:")
    print(f"  States: {len(states)}")
    print(f"  Cities: {len(set(loc.get('city') for loc in all_locations if loc.get('city')))}")
    
    print(f"\nBy type:")
    for loc_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {loc_type}: {count}")

def main():
    print("=" * 60)
    print("FOOD FINDER - MASTER DATA COLLECTION")
    print("=" * 60)
    print("\nThis will:")
    print("1. Scrape Feeding America member food banks (~20)")
    print("2. Scrape OpenStreetMap food assistance locations (~5,000-15,000)")
    print("3. Merge with existing data and remove duplicates")
    print("\nEstimated time: 5-10 minutes")
    print("=" * 60)
    
    input("\nPress Enter to start...")
    
    # Track success
    results = []
    
    # Run Feeding America scraper
    success = run_script('scrape_feeding_america.py', 'Feeding America Scraper')
    results.append(('Feeding America', success))
    
    # Run OSM scraper
    success = run_script('osm_scraper.py', 'OpenStreetMap Scraper')
    results.append(('OpenStreetMap', success))
    
    # Merge everything
    merge_all_data()
    
    # Final summary
    print(f"\n\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {name}")
    
    print(f"\n{'='*60}")
    print("✓ DATA COLLECTION COMPLETE!")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("1. Review server/data/all-locations.json")
    print("2. Commit changes: git add -A && git commit -m 'Add Feeding America and OSM data'")
    print("3. Push to GitHub: git push origin MoarData")
    print("4. Restart dev server to see new locations!")

if __name__ == "__main__":
    main()
