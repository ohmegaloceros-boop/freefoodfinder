/**
 * FreeFoodFinder - Backend API Server
 * 
 * Provides REST API endpoints for:
 * - Fetching location data (national dataset)
 * - Filtering locations by type and viewport bounds
 * - Accepting user-submitted location suggestions
 * 
 * Data Storage:
 * - all-locations.json: Approved locations (899+ nationwide)
 * - submissions.json: Pending user submissions awaiting admin review
 * 
 * Tech Stack:
 * - Express.js for REST API
 * - CORS enabled for React frontend
 * - JSON file-based data storage
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

// Serve static files from React build (production)
app.use(express.static(path.join(__dirname, '../client/build')));

// ========== API ROUTES ==========

/**
 * GET /api/locations
 * Fetch all locations, optionally filtered by type or bounding box
 * 
 * Query Parameters:
 *   - type: 'foodbank' | 'community_fridge' | 'food_box' (optional)
 *     Example: /api/locations?type=foodbank
 * 
 *   - bounds: 'north,south,east,west' (optional) - filter by viewport
 *     Example: /api/locations?bounds=40.0,-105.0,39.5,-104.5
 * 
 * Returns: Array of location objects with coordinates, name, address, etc.
 */
app.get('/api/locations', (req, res) => {
  const { type, bounds } = req.query;
  
  let locations = [...allLocations];
  
  // Filter by type if provided
  if (type) {
    locations = locations.filter(location => location.type === type);
  }
  
  // Filter by viewport bounds if provided (performance optimization)
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
 * Fetch a single location by ID
 * 
 * Path Parameters:
 *   - id: Location ID (e.g., 'denver-1', 'seattle-5', 'natl-042')
 * 
 * Returns: Location object or 404 if not found
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
 * Request Body (JSON):
 *   Required:
 *     - name: string - Location name
 *     - type: 'foodbank' | 'community_fridge' | 'food_box'
 *     - city: string
 *     - state: string (2-letter code)
 *     - zipCode: string (5 digits)
 *     - coordinates: {lat: number, lng: number}
 *   
 *   Optional:
 *     - address: string
 *     - hours: string
 *     - phone: string
 *     - description: string
 *     - submitterEmail: string
 * 
 * Submissions are saved with 'pending' status for admin review
 * Returns: Success message with submission ID
 */
app.post('/api/submissions', (req, res) => {
  // Add metadata to submission
  const submission = {
    ...req.body,
    submittedAt: new Date().toISOString(),
    status: 'pending' // Admin will review and approve/reject
  };

  const submissionsPath = path.join(__dirname, 'data', 'submissions.json');
  
  // Read existing submissions or initialize empty array
  let submissions = [];
  if (fs.existsSync(submissionsPath)) {
    try {
      const data = fs.readFileSync(submissionsPath, 'utf8');
      submissions = JSON.parse(data);
    } catch (error) {
      console.error('Error reading submissions file:', error);
      submissions = []; // Start fresh if file is corrupted
    }
  }

  // Add new submission to array
  submissions.push(submission);

  // Save updated submissions to file
  try {
    fs.writeFileSync(submissionsPath, JSON.stringify(submissions, null, 2));
    console.log('✓ New submission received:', submission.name, '-', submission.city, submission.state);
    res.status(201).json({ 
      message: 'Submission received successfully', 
      id: submissions.length 
    });
  } catch (error) {
    console.error('Error saving submission:', error);
    res.status(500).json({ message: 'Error saving submission' });
  }
});

// ========== FALLBACK ROUTE ==========

/**
 * Serve React app for all other routes (SPA routing)
 * Must be last route definition
 */
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/build', 'index.html'));
});

// ========== SERVER STARTUP ==========

/**
 * Start Express server (skip if running in serverless environment like Vercel)
 */
if (process.env.VERCEL !== '1') {
  app.listen(PORT, () => {
    console.log(`🚀 FreeFoodFinder API server running on port ${PORT}`);
    console.log(`📍 Serving ${allLocations.length} locations across the nation`);
  });
}

// Export app for serverless deployment (Vercel, AWS Lambda, etc.)
module.exports = app;
