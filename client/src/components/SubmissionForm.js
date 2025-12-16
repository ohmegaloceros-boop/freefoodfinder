import React, { useState } from 'react';
import './SubmissionForm.css';

function SubmissionForm({ isOpen, onClose, clickedCoordinates, selectedCity, locationData }) {
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
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  // Update form data when location data is provided
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

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

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

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Suggest a New Location</h2>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>

        {formData.coordinates && (
          <div className="coordinates-info">
            📍 Location selected on map: {formData.coordinates.lat.toFixed(4)}, {formData.coordinates.lng.toFixed(4)}
          </div>
        )}

        <form onSubmit={handleSubmit} className="submission-form">
          <div className="form-group">
            <label>Type *</label>
            <select name="type" value={formData.type} onChange={handleChange} required>
              <option value="foodbank">Food Bank</option>
              <option value="community_fridge">Community Fridge</option>
              <option value="food_box">Food Box</option>
            </select>
          </div>

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

          {submitStatus === 'success' && (
            <div className="alert alert-success">
              ✓ Thank you! Your submission has been received and will be reviewed by an admin before being added to the map.
            </div>
          )}

          {submitStatus === 'error' && (
            <div className="alert alert-error">
              ✗ Sorry, there was an error submitting. Please try again.
            </div>
          )}

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
