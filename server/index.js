/**
 * FreeFoodFinder - Backend API Server
 * 
 * Provides REST API endpoints for:
 * - Fetching location data by city
 * - Filtering locations by type
 * - Accepting user-submitted location suggestions
 * 
 * Data stored in JSON files:
 * - locations.json: Approved locations organized by city
 * - submissions.json: Pending user submissions awaiting review
 */

const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const allLocations = require('./data/all-locations.json');

const app = express();
const PORT = process.env.PORT || 5000;

// ========== MIDDLEWARE ==========

app.use(cors()); // Enable Cross-Origin requests from React frontend
app.use(express.json()); // Parse JSON request bodies

// Serve static files from React build
app.use(express.static(path.join(__dirname, '../client/build')));

// ========== API ROUTES ==========

/**
 * GET /api/locations
 * Fetch all locations, optionally filtered by type or bounding box
 * Query params:
 *   - type: 'foodbank' | 'community_fridge' | 'food_box' (optional)
 *   - bounds: 'north,south,east,west' (optional) - filter by viewport
 */
app.get('/api/locations', (req, res) => {
  const { type, bounds } = req.query;
  
  let locations = [...allLocations];
  
  // Filter by type if provided
  if (type) {
    locations = locations.filter(location => location.type === type);
  }
  
  // Filter by viewport bounds if provided
  if (bounds) {
    const [north, south, east, west] = bounds.split(',').map(Number);
    locations = locations.filter(location => {
      const { lat, lng } = location.coordinates;
      return lat <= north && lat >= south && lng <= east && lng >= west;
    });
  }

  res.json(locations);
});

/**
 * GET /api/locations/:id
 * Fetch a single location by ID (uses string IDs like 'denver-1', 'seattle-5')
 */
app.get('/api/locations/:id', (req, res) => {
  const location = allLocations.find(loc => loc.id === req.params.id);
  
  if (!location) {
    return res.status(404).json({ message: 'Location not found' });
  }
  
  res.json(location);
});

/**
 * POST /api/submissions
 * Accept new location suggestions from users
 * 
 * Request body should include:
 *   - name, type, address, city, state, zipCode
 *   - coordinates: {lat, lng}
 *   - hours, phone, description (optional)
 *   - submitterEmail (optional)
 * 
 * Submissions are saved with 'pending' status for admin review
 */
app.post('/api/submissions', (req, res) => {
  const submission = {
    ...req.body,
    submittedAt: new Date().toISOString(),
    status: 'pending'
  };

  const submissionsPath = path.join(__dirname, 'data', 'submissions.json');
  
  // Read existing submissions or create empty array
  let submissions = [];
  if (fs.existsSync(submissionsPath)) {
    const data = fs.readFileSync(submissionsPath, 'utf8');
    submissions = JSON.parse(data);
  }

  // Add new submission
  submissions.push(submission);

  // Save to file
  fs.writeFileSync(submissionsPath, JSON.stringify(submissions, null, 2));

  console.log('New submission received:', submission.name);
  res.status(201).json({ message: 'Submission received successfully', id: submissions.length });
});

// Serve React app for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/build', 'index.html'));
});

// Only start server if not in Vercel serverless environment
if (process.env.VERCEL !== '1') {
  app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
  });
}

// Export for Vercel
module.exports = app;
