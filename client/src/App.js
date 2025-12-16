/**
 * FreeFoodFinder - Main Application Component
 * 
 * This app helps users find free food resources including:
 * - Food Banks
 * - Community Fridges  
 * - Food Boxes
 * 
 * Features:
 * - Multi-city support (Denver, Seattle)
 * - Interactive map with custom markers
 * - Filter locations by type
 * - User-submitted location suggestions
 * - Mobile-responsive design with slide-out sidebar
 */

import React, { useState, useEffect } from 'react';
import Map from './components/Map';
import FilterPanel from './components/FilterPanel';
import LocationList from './components/LocationList';
import SubmissionForm from './components/SubmissionForm';
import './App.css';

function App() {
  // ========== STATE MANAGEMENT ==========
  
  // Location data state
  const [locations, setLocations] = useState([]); // All locations from API
  const [filteredLocations, setFilteredLocations] = useState([]); // Filtered by type
  const [selectedCity, setSelectedCity] = useState('denver'); // Current city
  const [selectedLocation, setSelectedLocation] = useState(null); // Location clicked on map/list
  
  // Filter state - controls which types of locations are shown
  const [selectedTypes, setSelectedTypes] = useState({
    foodbank: true,
    community_fridge: true,
    food_box: true
  });
  
  // User submission workflow state
  const [isSubmissionFormOpen, setIsSubmissionFormOpen] = useState(false);
  const [clickedCoordinates, setClickedCoordinates] = useState(null);
  const [isSelectingOnMap, setIsSelectingOnMap] = useState(false);
  const [locationData, setLocationData] = useState(null); // Reverse geocoded address
  
  // Mobile UI state
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Hamburger menu toggle

  // City configuration - coordinates for map centering
  const cityConfig = {
    denver: {
      name: 'Denver',
      state: 'Colorado',
      center: [39.7392, -104.9903]
    },
    seattle: {
      name: 'Seattle',
      state: 'Washington',
      center: [47.6062, -122.3321]
    }
  };

  // ========== DATA FETCHING ==========
  
  /**
   * Fetch locations when city changes
   * Queries the backend API for location data specific to the selected city
   */
  useEffect(() => {
    fetch(`http://localhost:5000/api/locations?city=${selectedCity}`)
      .then(res => res.json())
      .then(data => {
        setLocations(data);
        setFilteredLocations(data);
      })
      .catch(err => {
        console.error('Error fetching locations:', err);
        // Fallback to sample data if API is not available
        const sampleData = require('./data/sampleLocations.json');
        setLocations(sampleData);
        setFilteredLocations(sampleData);
      });
  }, [selectedCity]);

  /**
   * Filter locations based on selected types
   * Updates whenever user toggles food bank, fridge, or food box filters
   */
  useEffect(() => {
    const filtered = locations.filter(location => selectedTypes[location.type]);
    setFilteredLocations(filtered);
  }, [selectedTypes, locations]);

  // ========== EVENT HANDLERS ==========
  
  /**
   * Toggle filter for a specific location type
   * @param {string} type - One of: 'foodbank', 'community_fridge', 'food_box'
   */
  const handleFilterChange = (type) => {
    setSelectedTypes(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  /**
   * Handle when user clicks a location marker or list item
   * Centers map on the selected location
   */
  const handleLocationClick = (location) => {
    setSelectedLocation(location);
  };

  /**
   * Start the "Select on Map" workflow
   * User can click map to suggest a new location
   */
  const handleStartSelecting = () => {
    setIsSelectingOnMap(true);
  };

  /**
   * Handle map clicks during location suggestion workflow
   * Performs reverse geocoding to get address from coordinates
   * @param {Object} coordinates - {lat, lng} from map click
   */
  const handleMapClick = async (coordinates) => {
    if (!isSelectingOnMap) return;
    
    setClickedCoordinates(coordinates);
    
    /**
     * Reverse Geocoding: Convert coordinates to address
     * Uses OpenStreetMap Nominatim API (free, no API key required)
     */
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${coordinates.lat}&lon=${coordinates.lng}&zoom=18&addressdetails=1`
      );
      const data = await response.json();
      
      // Extract relevant address components
      const locationInfo = {
        coordinates,
        address: data.address?.road || data.address?.building || '',
        city: data.address?.city || data.address?.town || data.address?.village || '',
        state: data.address?.state || '',
        zipCode: data.address?.postcode || '',
        fullAddress: data.display_name || ''
      };
      
      setLocationData(locationInfo);
    } catch (error) {
      console.error('Error fetching address:', error);
      setLocationData({ coordinates });
    }
    
    setIsSelectingOnMap(false);
    setIsSubmissionFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsSubmissionFormOpen(false);
    setClickedCoordinates(null);
    setLocationData(null);
    setIsSelectingOnMap(false);
  };

  // ========== RENDER ==========
  
  return (
    <div className="App">
      {/* Header with city selector and suggest button */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <h1>🍎 FreeFoodFinder</h1>
            <div className="city-selector">
              <select 
                value={selectedCity} 
                onChange={(e) => setSelectedCity(e.target.value)}
                className="city-dropdown"
              >
                <option value="denver">Denver, CO</option>
                <option value="seattle">Seattle, WA</option>
              </select>
            </div>
          </div>
          <button 
            className="suggest-button"
            onClick={handleStartSelecting}
          >
            {isSelectingOnMap ? '📍 Click on Map...' : '+ Suggest Location'}
          </button>
        </div>
      </header>
      
      <button 
        className={`hamburger-button ${isSidebarOpen ? 'hamburger-open' : ''}`}
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        aria-label="Toggle menu"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>
      
      <div className="app-container">
        <aside className={`sidebar ${isSidebarOpen ? 'sidebar-open' : ''}`}>
          <FilterPanel 
            selectedTypes={selectedTypes}
            onFilterChange={handleFilterChange}
          />
          <LocationList 
            locations={filteredLocations}
            onLocationClick={handleLocationClick}
            selectedLocation={selectedLocation}
            onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          />
        </aside>
        
        {isSidebarOpen && (
          <div 
            className="sidebar-overlay"
            onClick={() => setIsSidebarOpen(false)}
          ></div>
        )}
        
        <main className="map-container">
          <Map 
            locations={filteredLocations}
            selectedLocation={selectedLocation}
            onLocationClick={handleLocationClick}
            onMapClick={handleMapClick}
            cityCenter={cityConfig[selectedCity].center}
            isSelectingOnMap={isSelectingOnMap}
          />
        </main>
      </div>
      
      <SubmissionForm 
        isOpen={isSubmissionFormOpen}
        onClose={handleCloseForm}
        clickedCoordinates={clickedCoordinates}
        selectedCity={selectedCity}
        locationData={locationData}
      />
    </div>
  );
}

export default App;
