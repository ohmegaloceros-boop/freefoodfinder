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
import SearchBar from './components/SearchBar';
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
          setMapZoom(10); // Zoom level 10 shows approximately 10-mile radius
          console.log('User location detected:', userPos);
        },
        (error) => {
          console.log('Geolocation error:', error.message);
          // Keep default center and zoom
        },
        {
          enableHighAccuracy: false,
          timeout: 10000, // Increased to 10 seconds
          maximumAge: 300000 // Allow cached position up to 5 minutes old
        }
      );
    } else {
      console.log('Geolocation not supported');
    }
  }, []);

  // ========== DATA FETCHING ==========
  
  /**
   * Fetch locations based on map viewport (lazy loading)
   * Only loads locations visible in current map view for better performance
   * Triggered when map bounds change or filters are toggled
   * 
   * Debounced to avoid excessive API calls during rapid panning/zooming
   */
  useEffect(() => {
    // Skip initial fetch until we have map bounds (after first render)
    if (!mapBounds) return;
    
    // Debounce: Wait 300ms after user stops moving map before fetching
    const timeoutId = setTimeout(() => {
      // Build query parameters for server-side filtering
      const params = new URLSearchParams();
      params.append('bounds', `${mapBounds.north},${mapBounds.south},${mapBounds.east},${mapBounds.west}`);
      
      // Fetch filtered locations from server
      fetch(`/api/locations?${params.toString()}`)
        .then(res => res.json())
        .then(data => {
          setLocations(data);
        })
        .catch(err => {
          console.error('Error fetching locations:', err);
        });
    }, 300); // 300ms debounce delay
    
    // Cleanup: Cancel pending fetch if bounds change again
    return () => clearTimeout(timeoutId);
  }, [mapBounds]); // Re-fetch when map viewport changes

  /**
   * Filter locations based on selected types
   * Note: Viewport filtering now happens server-side for performance
   * This only filters by type (foodbank, fridge, box)
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

  /**
   * Handle search - fly map to searched location
   * @param {Object} location - {lat, lng, displayName}
   */
  const handleSearch = (location) => {
    setMapCenter([location.lat, location.lng]);
    setMapZoom(13); // Zoom in to city level
    console.log('Flying to:', location.displayName);
  };

  // ========== RENDER ==========
  
  return (
    <div className="App">
      {/* Header with suggest button */}
      <header className="app-header">
        <div className="header-content">
          <h1 className="header-title">🍎 FreeFoodFinder</h1>
          <button 
            className="suggest-button"
            onClick={handleStartSelecting}
          >
            {isSelectingOnMap ? '📍 Click on Map...' : 'submit new location'}
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
      
      {/* Search bar for finding cities/locations */}
      <SearchBar onSearch={handleSearch} isSidebarOpen={isSidebarOpen} />
      
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
            center={mapCenter}
            zoom={mapZoom}
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
