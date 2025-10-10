# Multi-stage build for React Frontend
# Stage 1: Build the React app
FROM node:20-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies needed for build)
RUN npm ci

# Copy source code (including .env file)
COPY . .

# Build the app (Vite will pick up environment variables from .env file)
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy built app from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration (with backend proxy)
COPY nginx.conf /etc/nginx/nginx.conf

# Install openssl so we can generate a self-signed certificate at container start
RUN apk add --no-cache openssl

# Copy startup script(s) that run before nginx to ensure certs exist
COPY docker-entrypoint.d/ /docker-entrypoint.d/
RUN chmod +x /docker-entrypoint.d/*.sh || true

# Expose ports 80 and 443
EXPOSE 80 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"]