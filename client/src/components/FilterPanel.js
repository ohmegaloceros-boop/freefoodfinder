/**
 * FilterPanel Component
 * 
 * Displays filter buttons for each location type
 * Features:
 * - Toggle visibility of Food Banks, Community Fridges, and Food Boxes
 * - Color-coded to match map markers
 * - Responsive design: compact on mobile, larger on desktop
 * - Active filters show with highlighted background
 */

import React from 'react';
import './FilterPanel.css';

/**
 * Filter configuration with colors matching map markers
 * Each filter includes:
 * - key: Matches location.type in data
 * - label: Display name for users
 * - color: Hex code matching map marker color
 * - icon: Emoji for visual identification
 */
const filterOptions = [
  { key: 'foodbank', label: 'Food Banks', color: '#2e7d32', icon: '🏦' },
  { key: 'community_fridge', label: 'Community Fridges', color: '#66bb6a', icon: '🧊' },
  { key: 'food_box', label: 'Food Boxes', color: '#fdd835', icon: '📦' }
];

/**
 * @param {Object} selectedTypes - Object with boolean values for each type
 *   Example: { foodbank: true, community_fridge: false, food_box: true }
 * @param {Function} onFilterChange - Callback to toggle filter on/off
 *   Called with filter key (e.g., 'foodbank')
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
            {/* Color indicator matching map marker */}
            <span 
              className="filter-color" 
              style={{ backgroundColor: option.color }}
            ></span>
            
            {/* Icon and label */}
            <span className="filter-icon">{option.icon}</span>
            <span className="filter-label">{option.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default FilterPanel;
