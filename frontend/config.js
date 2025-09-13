// Configuration for different environments
const config = {
    development: {
        apiUrl: 'http://localhost:5001/api'
    },
    production: {
        apiUrl: 'https://studyspark-backend.herokuapp.com/api'  // We'll update this with actual URL later
    }
};

// Determine current environment
const environment = window.location.hostname === 'localhost' ? 'development' : 'production';

// Export the configuration
export const API_URL = config[environment].apiUrl;