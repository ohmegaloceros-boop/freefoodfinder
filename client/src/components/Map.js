/**
 * Map Component
 * 
 * Interactive Leaflet map displaying food resource locations
 * Features:
 * - Custom colored markers by location type
 * - Click-to-select mode for user submissions
 * - Smooth flying transitions between locations
 * - OpenStreetMap tiles (free, no API key)
 */

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './Map.css';
import './MapFix.css';

// ========== LEAFLET SETUP ==========

/**
 * Fix for default marker icons not loading in react-leaflet
 * See: https://github.com/Leaflet/Leaflet/issues/4968
 */
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

/**
 * Create custom map marker with specified color
 * @param {string} color - Hex color code for marker pin
 * @returns {L.DivIcon} Leaflet icon object
 */
const createCustomIcon = (color) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color};" class="marker-pin"></div>`,
    iconSize: [30, 42],
    iconAnchor: [15, 42],
    popupAnchor: [0, -42]
  });
};

// ========== MARKER ICONS ==========

/**
 * Icon definitions for each location type
 * Colors:
 * - Food Banks: Dark green (#2e7d32)
 * - Community Fridges: Light green (#66bb6a)  
 * - Food Boxes: Yellow (#fdd835)
 * - User Location: Blue (#2196f3)
 */
const icons = {
  foodbank: createCustomIcon('#2e7d32'),
  community_fridge: createCustomIcon('#66bb6a'),
  food_box: createCustomIcon('#fdd835'),
  user: createCustomIcon('#2196f3')
};

// ========== MAP CONTROL COMPONENTS ==========

/**
 * MapController - Handles map zoom to selected location and tracks viewport bounds
 * 
 * Responsibilities:
 * - Flies to selected location when user clicks marker/list item
 * - Tracks map bounds and reports changes to parent component
 * - Updates map view when center/zoom props change (e.g., user location detected)
 */
function MapController({ selectedLocation, onMapBoundsChange, center, zoom }) {
  const map = useMap();
  
  // Update map view when center or zoom changes (e.g., geolocation)
  useEffect(() => {
    if (center && zoom) {
      map.setView(center, zoom);
    }
  }, [center, zoom, map]);
  
  // Fly to selected location
  useEffect(() => {
    if (selectedLocation) {
      map.flyTo(
        [selectedLocation.coordinates.lat, selectedLocation.coordinates.lng],
        15,
        { duration: 1 }
      );
    }
  }, [selectedLocation, map]);

  // Track viewport bounds changes
  useEffect(() => {
    const updateBounds = () => {
      const bounds = map.getBounds();
      if (onMapBoundsChange) {
        onMapBoundsChange({
          north: bounds.getNorth(),
          south: bounds.getSouth(),
          east: bounds.getEast(),
          west: bounds.getWest()
        });
      }
    };

    // Update bounds when map moves
    map.on('moveend', updateBounds);
    updateBounds(); // Initial bounds

    return () => {
      map.off('moveend', updateBounds);
    };
  }, [map, onMapBoundsChange]);
  
  return null;
}

/**
 * MapClickHandler - Captures user clicks on the map
 * 
 * Used during "Suggest Location" workflow to get coordinates
 * Utilizes react-leaflet's useMapEvents hook
 */
function MapClickHandler({ onMapClick }) {
  useMapEvents({
    click: (e) => {
      if (onMapClick) {
        onMapClick({
          lat: e.latlng.lat,
          lng: e.latlng.lng
        });
      }
    }
  });
  return null;
}

// ========== MAIN MAP COMPONENT ==========

/**
 * Map - Main map display component
 * 
 * @param {Array} locations - Filtered array of location objects to display
 * @param {Object} selectedLocation - Currently selected location (if any)
 * @param {Function} onLocationClick - Callback when marker is clicked
 * @param {Function} onMapClick - Callback when map surface is clicked
 * @param {Function} onMapBoundsChange - Callback when viewport changes
 * @param {Array} defaultCenter - [lat, lng] initial map center
 * @param {number} defaultZoom - Initial zoom level
 * @param {Array} center - [lat, lng] current map center (can change dynamically)
 * @param {number} zoom - Current zoom level (can change dynamically)
 * @param {boolean} isSelectingOnMap - True when in "click to select" mode
 * @param {Array} userLocation - [lat, lng] of user's geolocation if available
 */
function Map({ locations, selectedLocation, onLocationClick, onMapClick, onMapBoundsChange, defaultCenter, defaultZoom, center, zoom, isSelectingOnMap, clickedCoordinates, isProcessingClick, onSkipGeocoding, userLocation }) {

  return (
    <>
      {isSelectingOnMap && (
        <div className="selecting-overlay">
          <div className="selecting-message">
            {isProcessingClick ? (
              <>
                <div className="loading-spinner"></div>
                <span>Finding address...</span>
                <button className="skip-button" onClick={onSkipGeocoding}>
                  Skip & Enter Manually
                </button>
              </>
            ) : (
              '📍 Click anywhere on the map to select a location'
            )}
          </div>
        </div>
      )}
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        className={`leaflet-map ${isSelectingOnMap ? 'selecting-mode' : ''}`}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapController selectedLocation={selectedLocation} onMapBoundsChange={onMapBoundsChange} center={center} zoom={zoom} />
        <MapClickHandler onMapClick={onMapClick} />
        
        {/* User's current location marker */}
        {userLocation && (
          <Marker
            position={userLocation}
            icon={icons.user}
          >
            <Popup>
              <div className="popup-content">
                <h3>📍 Your Location</h3>
                <p>You are here</p>
              </div>
            </Popup>
          </Marker>
        )}
        
        {/* Temporary marker for clicked location during processing */}
        {clickedCoordinates && isProcessingClick && (
          <Marker
            position={[clickedCoordinates.lat, clickedCoordinates.lng]}
            icon={L.divIcon({
              className: 'temp-marker',
              html: '<div class="temp-marker-pin">📍</div>',
              iconSize: [30, 30],
              iconAnchor: [15, 30]
            })}
          />
        )}
        
        {locations.map(location => (
          <Marker
            key={location.id}
            position={[location.coordinates.lat, location.coordinates.lng]}
            icon={icons[location.type]}
            eventHandlers={{
              click: () => onLocationClick(location)
            }}
          >
            <Popup>
              <div className="popup-content">
                <h3>{location.name}</h3>
                <p className="popup-type">{location.type.replace('_', ' ').toUpperCase()}</p>
                <p><strong>Address:</strong> {location.address}</p>
                <p><strong>Hours:</strong> {location.hours}</p>
                {location.phone && <p><strong>Phone:</strong> {location.phone}</p>}
                <p className="popup-description">{location.description}</p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </>
  );
}

export default Map;
