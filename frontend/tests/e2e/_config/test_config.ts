// GENESIS Dynamic Port Allocation for cigkoftecibey-webapp:
// Backend:  9049  (5000 + CRC32("cigkoftecibey-webapp") % 10000)
// Frontend: 19049 (15000 + CRC32("cigkoftecibey-webapp") % 10000)
export const config = {
    frontendUrl: process.env.FRONTEND_URL || 'http://localhost:19049',
    frontendPort: parseInt(process.env.FRONTEND_PORT || '19049'),
    backendUrl: process.env.BACKEND_URL || 'http://localhost:9049',
    auth: {
        email: process.env.TEST_EMAIL || 'admin@cigkofte.com',
        password: process.env.TEST_PASSWORD || 'admin123'
    }
};
