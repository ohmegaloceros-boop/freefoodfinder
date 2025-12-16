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

import React, { useState, useEffect, useCallback } from 'react';
import Map from './components/Map';
import FilterPanel from './components/FilterPanel';
import LocationList from './components/LocationList';
import SubmissionForm from './components/SubmissionForm';
import './App.css';

function App() {
  // ========== STATE MANAGEMENT ==========
  
  // Location data state
  const [locations, setLocations] = useState([]); // All locations from API
  const [filteredLocations, setFilteredLocations] = useState([]); // Filtered by type and viewport
  const [selectedLocation, setSelectedLocation] = useState(null); // Location clicked on map/list
  const [mapBounds, setMapBounds] = useState(null); // Current map viewport bounds
  
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
  const [isProcessingClick, setIsProcessingClick] = useState(false); // Prevent multiple clicks
  
  // Mobile UI state
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Hamburger menu toggle

  // Map center state
  const [mapCenter, setMapCenter] = useState([39.8283, -98.5795]); // Default: Geographic center of USA
  const [mapZoom, setMapZoom] = useState(4); // Default zoom level
  const [userLocation, setUserLocation] = useState(null); // User's geolocation
  const [locationPermission, setLocationPermission] = useState('prompt'); // 'prompt', 'granted', 'denied'

  // ========== GEOLOCATION ==========
  
  /**
   * Get user's location on mount and center map
   * Falls back to default USA center if permission denied or unavailable
   */
  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          const userPos = [latitude, longitude];
          setUserLocation(userPos);
          setMapCenter(userPos);
          setMapZoom(11); // Zoom in closer when we have user location
          setLocationPermission('granted');
          console.log('User location detected:', userPos);
        },
        (error) => {
          console.log('Geolocation error:', error.message);
          setLocationPermission('denied');
          // Keep default center and zoom
        },
        {
          enableHighAccuracy: false,
          timeout: 5000,
          maximumAge: 0
        }
      );
    } else {
      console.log('Geolocation not supported');
      setLocationPermission('denied');
    }
  }, []);

  // ========== DATA FETCHING ==========
  
  /**
   * Fetch all locations on mount
   * Loads complete national dataset from API
   */
  useEffect(() => {
    fetch('/api/locations')
      .then(res => res.json())
      .then(data => {
        setLocations(data);
        setFilteredLocations(data);
      })
      .catch(err => {
        console.error('Error fetching locations:', err);
      });
  }, []);

  /**
   * Filter locations based on selected types and viewport bounds
   * Updates whenever user toggles filters or pans/zooms map
   */
  useEffect(() => {
    let filtered = locations.filter(location => selectedTypes[location.type]);
    
    // Filter by viewport if map bounds are available
    if (mapBounds) {
      filtered = filtered.filter(location => {
        const { lat, lng } = location.coordinates;
        return lat <= mapBounds.north && 
               lat >= mapBounds.south && 
               lng >= mapBounds.west && 
               lng <= mapBounds.east;
      });
    }
    
    setFilteredLocations(filtered);
  }, [selectedTypes, locations, mapBounds]);

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
    if (!isSelectingOnMap || isProcessingClick) return; // Prevent multiple clicks
    
    setIsProcessingClick(true); // Block additional clicks
    setClickedCoordinates(coordinates); // Show marker immediately
    
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
    setIsProcessingClick(false); // Allow new clicks
    setIsSubmissionFormOpen(true);
  };

  const handleCloseForm = () => {
    setIsSubmissionFormOpen(false);
    setClickedCoordinates(null);
    setLocationData(null);
    setIsSelectingOnMap(false);
    setIsProcessingClick(false);
  };

  /**
   * Skip geocoding and open form immediately
   * Allows user to manually enter address if geocoding is slow
   */
  const handleSkipGeocoding = () => {
    setIsSelectingOnMap(false);
    setIsProcessingClick(false);
    setIsSubmissionFormOpen(true);
  };

  /**
   * Handle map bounds change (when user pans/zooms)
   * Updates visible locations based on current viewport
   */
  const handleMapBoundsChange = useCallback((bounds) => {
    setMapBounds(bounds);
  }, []);

  // ========== RENDER ==========
  
  return (
    <div className="App">
      {/* Header with suggest button */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <h1>🍎 FreeFoodFinder</h1>
            <p>Find free food resources nationwide</p>
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
            onMapBoundsChange={handleMapBoundsChange}
            defaultCenter={mapCenter}
            defaultZoom={mapZoom}
            isSelectingOnMap={isSelectingOnMap}
            clickedCoordinates={clickedCoordinates}
            isProcessingClick={isProcessingClick}
            onSkipGeocoding={handleSkipGeocoding}
            userLocation={userLocation}
          />
        </main>
      </div>
      
      <SubmissionForm 
        isOpen={isSubmissionFormOpen}
        onClose={handleCloseForm}
        clickedCoordinates={clickedCoordinates}
        locationData={locationData}
      />
    </div>
  );
}

export default App;
