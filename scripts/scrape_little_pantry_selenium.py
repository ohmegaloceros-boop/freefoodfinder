"""
Browser automation script to extract ALL Little Free Pantry locations
from https://mapping.littlefreepantry.org/

This script uses Selenium to:
1. Load the Google Maps interface
2. Extract all marker data
3. Save to JSON format

Requirements:
    pip install selenium webdriver-manager
"""

import json
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Set up Chrome driver with options"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    print("Setting up Chrome driver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extract_pantry_locations(driver):
    """
    Extract all Little Free Pantry locations from the map
    """
    url = "https://mapping.littlefreepantry.org/"
    print(f"\nLoading {url}...")
    driver.get(url)
    
    # Wait for map to load
    print("Waiting for map to load...")
    time.sleep(10)  # Give plenty of time for Google Maps to initialize
    
    locations = []
    
    try:
        # Try to find the map container and markers
        # Google Maps markers are typically in divs with specific classes
        
        # Method 1: Try to find result list items
        print("\nLooking for location data in results list...")
        try:
            # Wait for results to appear
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "results"))
            )
            
            # Find all result items
            result_items = driver.find_elements(By.CSS_SELECTOR, ".results table tbody tr")
            print(f"Found {len(result_items)} items in results list")
            
            for item in result_items:
                try:
                    name_elem = item.find_element(By.CSS_SELECTOR, "td a")
                    name = name_elem.text.strip()
                    
                    if name:
                        locations.append({
                            'name': name,
                            'type': 'food_box'
                        })
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Couldn't find results list: {e}")
        
        # Method 2: Execute JavaScript to access Google Maps API
        print("\nTrying to extract data via JavaScript...")
        try:
            # Try to access markers through Google Maps API
            js_script = """
            var markers = [];
            // Try to find markers in the Google Maps instance
            if (typeof google !== 'undefined' && google.maps) {
                // Look for map instance
                var mapElements = document.getElementsByClassName('gm-style');
                if (mapElements.length > 0) {
                    return 'Map found but markers not accessible via JS';
                }
            }
            return 'No Google Maps instance found';
            """
            result = driver.execute_script(js_script)
            print(f"JavaScript result: {result}")
            
        except Exception as e:
            print(f"JavaScript extraction failed: {e}")
        
        # Method 3: Try to click and extract from popups
        print("\nLooking for clickable markers on map...")
        try:
            # Find map markers (they might be in an iframe)
            map_frame = driver.find_element(By.TAG_NAME, "iframe")
            driver.switch_to.frame(map_frame)
            print("Switched to map iframe")
            
            # Look for marker elements
            markers = driver.find_elements(By.CSS_SELECTOR, "[role='button'][aria-label]")
            print(f"Found {len(markers)} potential markers")
            
            driver.switch_to.default_content()
            
        except Exception as e:
            print(f"Marker click method failed: {e}")
            driver.switch_to.default_content()
        
        # Method 4: Parse the HTML for embedded data
        print("\nParsing HTML for embedded location data...")
        page_source = driver.page_source
        
        # Look for patterns that might contain location data
        # Many sites embed data in JavaScript variables or JSON
        patterns = [
            r'"name"\s*:\s*"([^"]+)"',
            r'"title"\s*:\s*"([^"]+)"',
            r'<a[^>]*>([^<]+Little.*?Pantry[^<]*)</a>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            if matches:
                print(f"Found {len(matches)} matches with pattern: {pattern[:50]}...")
                for match in matches[:5]:  # Show first 5
                    print(f"  - {match}")
        
        # Try to scrape visible results
        print("\nAttempting to scrape visible pantry list...")
        try:
            # Scroll to load more results
            for _ in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Try different selectors for the results list
            selectors = [
                ".results table tbody tr td a",
                "table.results tbody tr td a",
                ".content-inner table tbody tr td a",
                "a[href*='pantry']"
            ]
            
            for selector in selectors:
                try:
                    links = driver.find_elements(By.CSS_SELECTOR, selector)
                    if links:
                        print(f"Found {len(links)} links with selector: {selector}")
                        for link in links:
                            text = link.text.strip()
                            if text and len(text) > 3:
                                locations.append({
                                    'name': text,
                                    'type': 'food_box'
                                })
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"Visible scraping failed: {e}")
        
        print(f"\nTotal unique locations found: {len(set([loc['name'] for loc in locations]))}")
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()
    
    return locations

def deduplicate_locations(locations):
    """Remove duplicate locations based on name"""
    seen = set()
    unique = []
    
    for loc in locations:
        name = loc['name']
        if name not in seen:
            seen.add(name)
            unique.append(loc)
    
    return unique

def generate_location_ids(locations):
    """Add unique IDs to locations"""
    for i, location in enumerate(locations, 1):
        location['id'] = f"little-pantry-{i}"
        # Add default fields
        location.setdefault('address', '')
        location.setdefault('city', '')
        location.setdefault('state', '')
        location.setdefault('coordinates', {'lat': 0, 'lng': 0})
        location.setdefault('hours', '24/7')
        location.setdefault('phone', '')
        location.setdefault('description', 'Little Free Pantry - Take what you need, leave what you can')
    
    return locations

def save_locations(locations, filename='little-pantry-full.json'):
    """Save locations to JSON file"""
    output_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'server',
        'data',
        filename
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(locations)} locations to {output_path}")
    
    # Also save just names to a text file for manual processing
    names_file = output_path.replace('.json', '_names.txt')
    with open(names_file, 'w', encoding='utf-8') as f:
        for loc in locations:
            f.write(f"{loc['name']}\n")
    print(f"Also saved names list to {names_file}")

def main():
    print("=" * 70)
    print("Little Free Pantry Browser Automation Scraper")
    print("=" * 70)
    print("\nThis script will:")
    print("1. Open the mapping website in a headless browser")
    print("2. Extract all visible Little Free Pantry locations")
    print("3. Save the data to JSON format")
    print("\nNOTE: Without coordinates, these will need manual geocoding")
    print("=" * 70)
    
    driver = None
    try:
        driver = setup_driver()
        locations = extract_pantry_locations(driver)
        
        if locations:
            locations = deduplicate_locations(locations)
            print(f"\nAfter deduplication: {len(locations)} unique locations")
            
            locations = generate_location_ids(locations)
            save_locations(locations)
            
            print("\n" + "=" * 70)
            print("NEXT STEPS:")
            print("=" * 70)
            print("1. The scraped names are saved but lack coordinates")
            print("2. You'll need to:")
            print("   a) Use a geocoding service to add lat/lng")
            print("   b) Or manually browse the site and click each location")
            print("   c) Or contact Little Free Pantry for their data export")
            print("\n3. Alternative: Focus on expanding existing high-quality data")
            print("   (Your 899 locations already cover 47 states!)")
            
        else:
            print("\n❌ No locations extracted!")
            print("\nThe site likely uses dynamic loading that requires:")
            print("1. Manual clicking through the map")
            print("2. API access from Little Free Pantry")
            print("3. Or advanced scraping with marker interaction")
            
            print("\nRECOMMENDATION:")
            print("Contact Little Free Pantry directly:")
            print("Email: info@littlefreepantry.org")
            print("Request: Data export or API access for nonprofit use")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            driver.quit()
            print("\nBrowser closed.")

if __name__ == "__main__":
    main()
