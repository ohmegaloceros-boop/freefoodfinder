# 🍎 FreeFoodFinder

A nationwide web application to help users find free food resources including food banks, community fridges, and food boxes.

## ✨ Features

- **📍 Automatic Geolocation**: Map centers on your location with optimal 10-mile radius view
- **🗺️ Interactive Map**: Browse 899+ food resources across 47 states using Leaflet/OpenStreetMap
- **🔍 Smart Filtering**: Toggle visibility by type (food banks, community fridges, food boxes)
- **📱 Responsive Design**: Slide-out sidebar on mobile, full layout on desktop
- **➕ Crowdsourced Data**: Users can suggest new locations via map clicks
- **🎯 Viewport Filtering**: Only shows locations in current map view for better performance
- **🌐 Reverse Geocoding**: Auto-fills addresses when users click map to suggest locations

## 🏗️ Architecture

### Frontend (`/client`)
- **Framework**: React 18.2.0
- **Map Library**: React-Leaflet 4.2.1 + Leaflet 1.9.4
- **Routing**: React Router (SPA)
- **Styling**: Custom CSS with mobile-first approach

### Backend (`/server`)
- **Runtime**: Node.js + Express.js
- **Data Storage**: JSON files (899+ locations in `all-locations.json`)
- **API**: RESTful endpoints for locations and user submissions
- **Deployment**: Render.com (auto-deploys from `viewport-filtering` branch)

### Key Components

```
client/src/
├── App.js                    # Main app component, state management
├── components/
│   ├── Map.js               # Leaflet map with geolocation & zoom control
│   ├── FilterPanel.js       # Type filters (food banks, fridges, boxes)
│   ├── LocationList.js      # Scrollable list of visible locations
│   └── SubmissionForm.js    # Modal form for user suggestions
└── App.css                  # Global styles

server/
├── index.js                 # Express API server
└── data/
    ├── all-locations.json   # 899+ approved locations
    └── submissions.json     # Pending user submissions
```

## 🚀 Technology Stack

- **Frontend**: React 18, React-Leaflet for maps
- **Backend**: Node.js with Express
- **Maps**: Leaflet with OpenStreetMap (free, no API key required)
- **Geocoding**: Nominatim API (OpenStreetMap's reverse geocoding)
- **Data Storage**: JSON files (easily upgradeable to database)
- **Deployment**: Render.com (production), GitHub (version control)

## 💻 Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm (comes with Node.js)

### Installation

1. Clone the repository and install all dependencies:
```bash
npm run install-all
```

Or install manually:
```bash
# Install root dependencies
npm install

# Install client dependencies
cd client
npm install

# Install server dependencies
cd ../server
npm install
```

### Running the Application

#### Development Mode (runs both frontend and backend):
```bash
npm run dev
```

This will start:
- Backend API server on http://localhost:5000
- React development server on http://localhost:3000

#### Run Backend Only:
```bash
npm run server
```

#### Run Frontend Only:
```bash
npm run client
```

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `client/build` folder.

## Project Structure

```
FoodFinder/
├── client/                 # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── Map.js             # Map display
│   │   │   ├── FilterPanel.js     # Filter controls
│   │   │   └── LocationList.js    # Location sidebar
│   │   ├── data/          # Sample data
│   │   ├── App.js         # Main app component
│   │   └── index.js       # Entry point
│   └── package.json
├── server/                # Node.js backend
│   ├── data/
│   │   └── locations.json # Location data
│   ├── index.js           # Express server
│   └── package.json
├── .github/
│   └── copilot-instructions.md
└── package.json           # Root package file
```

## Data Structure

Each location in the system has the following structure:

```json
{
  "id": 1,
  "name": "Downtown Community Food Bank",
  "type": "foodbank",
  "address": "123 Main Street",
  "city": "Sample City",
  "state": "SC",
  "zipCode": "12345",
  "coordinates": {
    "lat": 40.7128,
    "lng": -74.0060
  },
  "hours": "Mon-Fri: 9am-5pm",
  "phone": "(555) 123-4567",
  "description": "Description of the location"
}
```

### Location Types

- `foodbank`: Traditional food banks and pantries
- `community_fridge`: Public refrigerators with free food
- `food_box`: Community food boxes with non-perishable items

## Customization

### Adding Your Own Data

1. Edit `server/data/locations.json` with real location data
2. Ensure each location has valid coordinates (latitude/longitude)
3. Restart the server

### Changing Map Center

In [client/src/components/Map.js](client/src/components/Map.js), update the `defaultCenter` to your area:

```javascript
const defaultCenter = [YOUR_LATITUDE, YOUR_LONGITUDE];
```

### Adding More Filter Types

1. Add new type to the data structure
2. Update `filterOptions` in [client/src/components/FilterPanel.js](client/src/components/FilterPanel.js)
3. Add corresponding icon and color

## Future Enhancements

Here are some ideas to expand the app:

### Short-term
- [ ] User location detection (geolocation API)
- [ ] Search by address or zip code
- [ ] Directions to locations
- [ ] Hours highlighting (open now/closed)
- [ ] Mobile-friendly improvements

### Medium-term
- [ ] Database integration (MongoDB, PostgreSQL)
- [ ] User submissions for new locations
- [ ] Admin panel for managing locations
- [ ] Location verification system
- [ ] Reviews and ratings

### Long-term
- [ ] Real-time data from APIs (Yelp, Google Places, 211 services)
- [ ] Mobile app (React Native)
- [ ] Push notifications for new locations
- [ ] Multi-language support
- [ ] Food donation scheduling
- [ ] Integration with food rescue organizations

## Data Sources

To populate your app with real data, consider these resources:

- **211.org**: Information on local food assistance programs
- **Feeding America**: Food bank locator API
- **Google Places API**: Search for food banks and pantries
- **Local government open data portals**
- **Community organizations and social services directories**
- **freedge.org**: Community fridge directory

## Contributing

This is a starter project! Feel free to:
- Add new features
- Improve the UI/UX
- Add real data sources
- Submit bug reports or feature requests

## License

MIT License - Feel free to use this project for learning or as a foundation for your own app!

## Support

If you're new to React or web development:
- React Documentation: https://react.dev
- Leaflet Documentation: https://leafletjs.com
- Express Documentation: https://expressjs.com

## Acknowledgments

- Built with React and Leaflet
- Map data from OpenStreetMap contributors
- Icons and design inspired by modern web applications

---

**Note**: This project currently uses sample data. You'll need to add real location data to make it useful for your community!
