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
  // State: Is search input expanded?
  const [isExpanded, setIsExpanded] = useState(false);
  
  // State: User's search query text
  const [searchQuery, setSearchQuery] = useState('');
  
  // State: Is search API request in progress?
  const [isSearching, setIsSearching] = useState(false);
  
  // State: Error message to display (empty string = no error)
  const [error, setError] = useState('');

  /**
   * Toggle search bar expansion
   * - Expands to show input field when collapsed
   * - Collapses to just magnifying glass icon when expanded
   * - Clears any error messages
   */
  const handleToggle = () => {
    setIsExpanded(!isExpanded);
    setError('');
  };

  /**
   * Handle search submission
   * 
   * Flow:
   * 1. Validates query is not empty
   * 2. Calls Nominatim geocoding API (OpenStreetMap's free geocoding service)
   * 3. If location found: calls onSearch callback to fly map to location
   * 4. If not found: displays error message
   * 5. Closes search bar on success
   * 
   * @param {Event} e - Form submit event
   */
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setError('');

    try {
      // Search using Nominatim geocoding API
      // Free geocoding service provided by OpenStreetMap
      // Limit=1 returns only the best match
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}&limit=1`
      );
      const data = await response.json();

      if (data && data.length > 0) {
        const result = data[0];
        // Call parent component's onSearch callback with location data
        onSearch({
          lat: parseFloat(result.lat),
          lng: parseFloat(result.lon),
          displayName: result.display_name
        });
        // Clear search and collapse bar on success
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
      {/* Magnifying glass button - always visible */}
      <button 
        className="search-icon-button"
        onClick={handleToggle}
        aria-label="Search for location"
      >
        🔍
      </button>
      
      {/* Search form - only visible when expanded */}
      {isExpanded && (
        <>
          <form onSubmit={handleSearch} className="search-form">
            {/* Search text input */}
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search city or address..."
              className="search-input"
              autoFocus
            />
            
            {/* Conditional button: green "Go" when text entered, red "X" when empty */}
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
          </form>
          
          {/* Error message display - outside form for proper positioning */}
          {error && <div className="search-error">{error}</div>}
        </>
      )}
    </div>
  );
}

export default SearchBar;
