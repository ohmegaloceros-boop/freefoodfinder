#!/usr/bin/env python3
"""
Normalize all-locations.json to ensure consistent coordinate format
All locations should have coordinates in format: {coordinates: {lat, lng}}
"""

import json
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent.parent / "server" / "data"
ALL_LOCATIONS = DATA_DIR / "all-locations.json"

def normalize_locations():
    """Normalize coordinate format for all locations"""
    
    print(f"Loading locations from {ALL_LOCATIONS}...")
    with open(ALL_LOCATIONS, 'r', encoding='utf-8') as f:
        locations = json.load(f)
    print(f"  Found {len(locations)} locations")
    
    normalized_count = 0
    
    for location in locations:
        # Check if coordinates are at root level (needs normalization)
        if 'lat' in location and 'lng' in location and 'coordinates' not in location:
            # Move lat/lng into coordinates object
            location['coordinates'] = {
                'lat': location['lat'],
                'lng': location['lng']
            }
            # Remove from root
            del location['lat']
            del location['lng']
            normalized_count += 1
    
    print(f"\n{'='*60}")
    print(f"Normalization Summary:")
    print(f"  - Locations normalized: {normalized_count}")
    print(f"  - Locations already correct: {len(locations) - normalized_count}")
    print(f"  - Total locations: {len(locations)}")
    print(f"{'='*60}")
    
    if normalized_count > 0:
        print(f"\nSaving to {ALL_LOCATIONS}...")
        with open(ALL_LOCATIONS, 'w', encoding='utf-8') as f:
            json.dump(locations, f, indent=2, ensure_ascii=False)
        print("✓ Normalization complete!")
    else:
        print("\n⚠ No locations needed normalization")

if __name__ == '__main__':
    normalize_locations()
