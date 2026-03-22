// PlaceIQ — Frontend API Configuration
// For local development, use http://localhost:8080
// For production, change this to your Render backend URL (e.g., https://placeiq-backend.onrender.com)
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

window.PLACE_IQ_API_URL = isLocal 
    ? 'http://localhost:8080' 
    : 'https://placeiq-backend.onrender.com';

window.PLACE_IQ_AI_API_URL = isLocal 
    ? 'http://localhost:8001' 
    : 'https://placeiq-ai-service.onrender.com';


