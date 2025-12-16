import React from 'react';
import './LocationList.css';

const typeLabels = {
  foodbank: 'Food Bank',
  community_fridge: 'Community Fridge',
  food_box: 'Food Box'
};

function LocationList({ locations, onLocationClick, selectedLocation, onToggleSidebar }) {
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
      <div className="location-count" onClick={onToggleSidebar}>
        {locations.length} location{locations.length !== 1 ? 's' : ''} found
      </div>
      <div className="location-items">
        {locations.map(location => (
          <div
            key={location.id}
            className={`location-item ${selectedLocation?.id === location.id ? 'selected' : ''}`}
            onClick={() => onLocationClick(location)}
          >
            <div className="location-header">
              <h3>{location.name}</h3>
              <span className={`location-type type-${location.type}`}>
                {typeLabels[location.type]}
              </span>
            </div>
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
