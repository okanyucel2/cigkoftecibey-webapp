import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Resolve genesis.json path relative to this file
// This file is in projects/cigkoftecibey-webapp/frontend/tests/e2e/
const manualPath = path.resolve(__dirname, '../../../genesis.json');

let genesisConfig: any;

try {
    const rawData = fs.readFileSync(manualPath, 'utf-8');
    genesisConfig = JSON.parse(rawData);
} catch (error) {
    console.error(`Failed to load genesis.json from ${manualPath}`, error);
    // Fallback or throw
    throw new Error("Could not load genesis.json configuration. Ensure the file exists.");
}

export const config = {
    frontendUrl: `http://localhost:${genesisConfig.services.frontend.test_port}`,
    backendUrl: `http://localhost:${genesisConfig.services.backend.port}`,
    backendPort: genesisConfig.services.backend.port,
    frontendPort: genesisConfig.services.frontend.test_port,
    auth: {
        email: 'admin@cigkofte.com', // Default seeded admin
        password: 'admin123'         // Default seeded password
    }
};
