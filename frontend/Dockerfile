# Build stage
FROM node:20-alpine as build

WORKDIR /app

# Accept API URL as build arg (set in Railway)
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

# Use Railway-compatible nginx config template
COPY nginx.railway.conf /etc/nginx/templates/default.conf.template

EXPOSE 80

# Use envsubst to replace ${PORT} at runtime, then start nginx
CMD ["/bin/sh", "-c", "envsubst '${PORT}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
