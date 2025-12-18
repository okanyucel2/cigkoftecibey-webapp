# Build stage
FROM node:20-alpine AS builder

# Build args for version info (passed by Render or CI)
ARG RENDER_GIT_COMMIT=unknown
ARG RENDER_GIT_BRANCH=main

# Install git for local builds
RUN apk add --no-cache git

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Set git info as env vars for vite build
# Render provides these automatically via RENDER_GIT_COMMIT
ENV VITE_GIT_COMMIT=${RENDER_GIT_COMMIT}
ENV VITE_GIT_BRANCH=${RENDER_GIT_BRANCH}

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
