/**
 * SubmissionForm Component
 * 
 * Modal form for users to suggest new food resource locations
 * Features:
 * - Pre-fills location data from map clicks (via reverse geocoding)
 * - Validates required fields based on location type
 * - Shows success/error status after submission
 * - Auto-closes after successful submission
 * - Submissions saved to server for admin review
 */

import React, { useState } from 'react';
import './SubmissionForm.css';

/**
 * @param {boolean} isOpen - Controls modal visibility
 * @param {Function} onClose - Callback to close the modal
 * @param {Object} clickedCoordinates - {lat, lng} from map click
 * @param {string} selectedCity - City context (legacy, may be removed)
 * @param {Object} locationData - Pre-filled address data from reverse geocoding
 */
function SubmissionForm({ isOpen, onClose, clickedCoordinates, selectedCity, locationData }) {
  // Form data state - holds all input field values
  const [formData, setFormData] = useState({
    name: '',
    type: 'community_fridge',
    address: '',
    city: selectedCity === 'denver' ? 'Denver' : selectedCity === 'seattle' ? 'Seattle' : '',
    state: selectedCity === 'denver' ? 'CO' : selectedCity === 'seattle' ? 'WA' : '',
    zipCode: '',
    hours: '',
    phone: '',
    description: '',
    submitterEmail: '',
    coordinates: clickedCoordinates || null
  });
  
  // Submission status tracking
  const [isSubmitting, setIsSubmitting] = useState(false); // Disable submit button while processing
  const [submitStatus, setSubmitStatus] = useState(null); // 'success' | 'error' | null

  /**
   * Pre-fill form with reverse-geocoded location data
   * Runs when user clicks map and address is fetched
   */
  React.useEffect(() => {
    if (locationData) {
      setFormData(prev => ({
        ...prev,
        address: locationData.address || prev.address,
        city: locationData.city || prev.city,
        state: locationData.state || prev.state,
        zipCode: locationData.zipCode || prev.zipCode,
        coordinates: locationData.coordinates
      }));
    }
  }, [locationData]);

  /**
   * Handle input field changes
   * Updates form data state as user types
   */
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  /**
   * Submit form data to backend API
   * POST /api/submissions - Saves to submissions.json for admin review
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus(null);

    try {
      const response = await fetch('/api/submissions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setSubmitStatus('success');
        
        // Reset form to initial state
        setFormData({
          name: '',
          type: 'foodbank',
          address: '',
          city: 'Denver',
          state: 'CO',
          zipCode: '',
          hours: '',
          phone: '',
          description: '',
          submitterEmail: ''
        });
        
        // Auto-close modal after 2 seconds
        setTimeout(() => {
          onClose();
          setSubmitStatus(null);
        }, 2000);
      } else {
        setSubmitStatus('error');
      }
    } catch (error) {
      console.error('Error submitting:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Don't render if modal is closed
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      {/* Stop propagation to prevent closing when clicking inside modal */}
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Suggest a New Location</h2>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>

        {/* Show coordinates if location was selected on map */}
        {formData.coordinates && (
          <div className="coordinates-info">
            📍 Location selected on map: {formData.coordinates.lat.toFixed(4)}, {formData.coordinates.lng.toFixed(4)}
          </div>
        )}

        <form onSubmit={handleSubmit} className="submission-form">
          {/* Location Type Selector */}
          <div className="form-group">
            <label>Type *</label>
            <select name="type" value={formData.type} onChange={handleChange} required>
              <option value="foodbank">Food Bank</option>
              <option value="community_fridge">Community Fridge</option>
              <option value="food_box">Food Box</option>
            </select>
          </div>

          {/* Location Name */}
          <div className="form-group">
            <label>Location Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="e.g., Downtown Community Fridge"
            />
          </div>

          {/* Street Address - Required for food banks, optional for fridges/boxes */}
          <div className="form-group">
            <label>Address {formData.type === 'foodbank' && '*'}</label>
            <input
              type="text"
              name="address"
              value={formData.address}
              onChange={handleChange}
              required={formData.type === 'foodbank'}
              placeholder="Street address or general location"
            />
          </div>

          {/* City, State, Zip Row */}
          <div className="form-row">
            <div className="form-group">
              <label>City *</label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>State *</label>
              <input
                type="text"
                name="state"
                value={formData.state}
                onChange={handleChange}
                required
                maxLength="2"
              />
            </div>

            <div className="form-group">
              <label>Zip Code *</label>
              <input
                type="text"
                name="zipCode"
                value={formData.zipCode}
                onChange={handleChange}
                required
                pattern="[0-9]{5}"
                placeholder="80202"
              />
            </div>
          </div>

          {/* Operating Hours */}
          <div className="form-group">
            <label>Hours</label>
            <input
              type="text"
              name="hours"
              value={formData.hours}
              onChange={handleChange}
              placeholder="e.g., Mon-Fri: 9am-5pm or 24/7 Access"
            />
          </div>

          {/* Contact Phone */}
          <div className="form-group">
            <label>Phone</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="(303) 555-1234"
            />
          </div>

          {/* Description */}
          <div className="form-group">
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="3"
              placeholder="Brief description of the location and services offered"
            />
          </div>

          {/* Submitter Email - Optional for follow-up verification */}
          <div className="form-group">
            <label>Your Email (optional)</label>
            <input
              type="email"
              name="submitterEmail"
              value={formData.submitterEmail}
              onChange={handleChange}
              placeholder="In case we need to verify details"
            />
          </div>

          {/* Success message */}
          {submitStatus === 'success' && (
            <div className="alert alert-success">
              ✓ Thank you! Your submission has been received and will be reviewed by an admin before being added to the map.
            </div>
          )}

          {/* Error message */}
          {submitStatus === 'error' && (
            <div className="alert alert-error">
              ✗ Sorry, there was an error submitting. Please try again.
            </div>
          )}

          {/* Form Action Buttons */}
          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={isSubmitting} className="btn-primary">
              {isSubmitting ? 'Submitting...' : 'Submit Suggestion'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SubmissionForm;
