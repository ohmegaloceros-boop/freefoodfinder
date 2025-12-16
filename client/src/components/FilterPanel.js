/**
 * FilterPanel Component
 * 
 * Displays filter buttons for each location type
 * On mobile: Compact checkbox-style buttons
 * On desktop: Larger button-style filters
 * 
 * Active filters show with highlighted background
 */

import React from 'react';
import './FilterPanel.css';

// Filter configuration with colors matching map markers
const filterOptions = [
  { key: 'foodbank', label: 'Food Banks', color: '#2e7d32', icon: '🏦' },
  { key: 'community_fridge', label: 'Community Fridges', color: '#66bb6a', icon: '🧊' },
  { key: 'food_box', label: 'Food Boxes', color: '#fdd835', icon: '📦' }
];

/**
 * @param {Object} selectedTypes - Object with boolean values for each type
 * @param {Function} onFilterChange - Callback to toggle filter on/off
 */
function FilterPanel({ selectedTypes, onFilterChange }) {
  return (
    <div className="filter-panel">
      <h2>Filter Locations</h2>
      <div className="filter-options">
        {filterOptions.map(option => (
          <div
            key={option.key} 
            className={`filter-option ${selectedTypes[option.key] ? 'active' : ''}`}
            onClick={() => onFilterChange(option.key)}
          >
            <span 
              className="filter-color" 
              style={{ backgroundColor: option.color }}
            ></span>
            <span className="filter-icon">{option.icon}</span>
            <span className="filter-label">{option.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default FilterPanel;
