#!/usr/bin/env python3
"""
Merge little-pantry-locations.json into all-locations.json
"""

import json
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent.parent / "server" / "data"
ALL_LOCATIONS = DATA_DIR / "all-locations.json"
PANTRY_LOCATIONS = DATA_DIR / "little-pantry-geocoded_3941.json"

def merge_locations():
    """Merge pantry locations into main location set"""
    
    # Load existing locations
    print(f"Loading locations from {ALL_LOCATIONS}...")
    with open(ALL_LOCATIONS, 'r', encoding='utf-8') as f:
        all_locations = json.load(f)
    print(f"  Found {len(all_locations)} existing locations")
    
    # Load pantry locations
    print(f"\nLoading pantry locations from {PANTRY_LOCATIONS}...")
    with open(PANTRY_LOCATIONS, 'r', encoding='utf-8') as f:
        pantry_locations = json.load(f)
    print(f"  Found {len(pantry_locations)} pantry locations")
    
    if len(pantry_locations) == 0:
        print("\n⚠ No pantry locations to merge!")
        return
    
    # Get existing IDs to avoid duplicates
    existing_ids = {loc.get('id') for loc in all_locations if loc.get('id')}
    
    # Merge pantries (skip duplicates)
    new_count = 0
    duplicate_count = 0
    
    for pantry in pantry_locations:
        if pantry.get('id') in existing_ids:
            duplicate_count += 1
            print(f"  ⊘ Skipping duplicate: {pantry['name']}")
        else:
            all_locations.append(pantry)
            existing_ids.add(pantry.get('id'))
            new_count += 1
    
    # Save merged data
    print(f"\n{'='*60}")
    print(f"Merge Summary:")
    print(f"  - New pantries added: {new_count}")
    print(f"  - Duplicates skipped: {duplicate_count}")
    print(f"  - Total locations: {len(all_locations)} (was {len(all_locations) - new_count})")
    print(f"{'='*60}")
    
    if new_count > 0:
        print(f"\nSaving to {ALL_LOCATIONS}...")
        with open(ALL_LOCATIONS, 'w', encoding='utf-8') as f:
            json.dump(all_locations, f, indent=2, ensure_ascii=False)
        print("✓ Merge complete!")
    else:
        print("\n⚠ No new locations to save")

if __name__ == '__main__':
    merge_locations()
