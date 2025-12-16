/**
 * LocationList Component
 * 
 * Displays scrollable list of food resource locations
 * Features:
 * - Highlights selected location
 * - Shows count of visible locations
 * - Auto-closes sidebar on mobile when location clicked
 * - Displays empty state when no results match filters
 */

import React from 'react';
import './LocationList.css';

// Human-readable labels for location types
const typeLabels = {
  foodbank: 'Food Bank',
  community_fridge: 'Community Fridge',
  food_box: 'Food Box'
};

/**
 * @param {Array} locations - Filtered locations to display
 * @param {Function} onLocationClick - Callback when location is selected
 * @param {Object} selectedLocation - Currently selected location (highlighted)
 * @param {Function} onToggleSidebar - Callback to toggle mobile sidebar
 */
function LocationList({ locations, onLocationClick, selectedLocation, onToggleSidebar }) {
  // Show empty state when no locations match current filters
  if (locations.length === 0) {
    return (
      <div className="location-list">
        <div className="no-results">
          <p>No locations match your filters</p>
        </div>
      </div>
    );
  }

  return (
    <div className="location-list">
      {/* Header showing total count - clickable on mobile to close sidebar */}
      <div className="location-count" onClick={onToggleSidebar}>
        {locations.length} location{locations.length !== 1 ? 's' : ''} found
      </div>
      
      {/* Scrollable list of location cards */}
      <div className="location-items">
        {locations.map(location => (
          <div
            key={location.id}
            className={`location-item ${selectedLocation?.id === location.id ? 'selected' : ''}`}
            onClick={() => onLocationClick(location)}
          >
            {/* Location name and type badge */}
            <div className="location-header">
              <h3>{location.name}</h3>
              <span className={`location-type type-${location.type}`}>
                {typeLabels[location.type]}
              </span>
            </div>
            
            {/* Location details */}
            <p className="location-address">
              📍 {location.address}, {location.city}
            </p>
            <p className="location-hours">
              🕒 {location.hours}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default LocationList;
