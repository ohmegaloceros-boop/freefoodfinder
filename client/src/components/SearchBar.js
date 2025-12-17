/**
 * SearchBar Component
 * 
 * Expandable search bar with magnifying glass icon
 * Features:
 * - Click magnifying glass to expand search input
 * - Search for cities or addresses
 * - Uses Nominatim geocoding API to find locations
 * - Flies map to searched location
 */

import React, { useState } from 'react';
import './SearchBar.css';

/**
 * @param {Function} onSearch - Callback when location is found
 *   Receives: { lat, lng, displayName }
 * @param {boolean} isSidebarOpen - True when sidebar is visible (hides search on mobile)
 */
function SearchBar({ onSearch, isSidebarOpen }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState('');

  /**
   * Toggle search bar expansion
   */
  const handleToggle = () => {
    setIsExpanded(!isExpanded);
    setError('');
  };

  /**
   * Handle search submission
   * Uses Nominatim geocoding API to find location
   */
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setError('');

    try {
      // Search using Nominatim geocoding API
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=1`
      );
      const data = await response.json();

      if (data && data.length > 0) {
        const result = data[0];
        onSearch({
          lat: parseFloat(result.lat),
          lng: parseFloat(result.lon),
          displayName: result.display_name
        });
        setSearchQuery('');
        setIsExpanded(false);
      } else {
        setError('Location not found. Try a city name or address.');
      }
    } catch (err) {
      console.error('Search error:', err);
      setError('Search failed. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className={`search-bar ${isExpanded ? 'expanded' : ''} ${isSidebarOpen ? 'behind-sidebar' : ''}`}>
      <button 
        className="search-icon-button"
        onClick={handleToggle}
        aria-label="Search for location"
      >
        🔍
      </button>
      
      {isExpanded && (
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search city or address..."
            className="search-input"
            autoFocus
          />
          {searchQuery.trim() ? (
            <button 
              type="submit" 
              className="search-submit-button"
              disabled={isSearching}
            >
              {isSearching ? '...' : 'Go'}
            </button>
          ) : (
            <button 
              type="button"
              className="search-close-button"
              onClick={handleToggle}
            >
              ✕
            </button>
          )}
          {error && <div className="search-error">{error}</div>}
        </form>
      )}
    </div>
  );
}

export default SearchBar;
