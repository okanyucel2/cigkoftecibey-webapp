# Build stage
FROM node:20-alpine AS builder

# Build args for version info (passed by Render or CI)
ARG RENDER_GIT_COMMIT=unknown
ARG RENDER_GIT_BRANCH=main
ARG VITE_API_URL=https://genesis-cigkoftecibey-webapp-backend-59jx.onrender.com/api

# Install git for local builds
RUN apk add --no-cache git

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Set env vars for vite build
ENV VITE_GIT_COMMIT=${RENDER_GIT_COMMIT}
ENV VITE_GIT_BRANCH=${RENDER_GIT_BRANCH}
ENV VITE_API_URL=${VITE_API_URL}

# Build the Vue app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
