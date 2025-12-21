export const config = {
    frontendUrl: process.env.FRONTEND_URL || 'http://localhost:5174',
    frontendPort: parseInt(process.env.FRONTEND_PORT || '5174'),
    backendUrl: process.env.BACKEND_URL || 'http://localhost:8000',
    auth: {
        email: process.env.TEST_EMAIL || 'admin@cigkofte.com',
        password: process.env.TEST_PASSWORD || 'admin123'
    }
};
