# Use official Node.js runtime as base image with Node 20
FROM node:20-alpine

# Set working directory inside container
WORKDIR /app

# Install Python and build tools for native dependencies
RUN apk add --no-cache python3 make g++ python3-dev py3-setuptools

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install --production --legacy-peer-deps

# Copy application code
COPY . .

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership of the app directory to the nodejs user
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port 5002
EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5002/health || exit 1

# Start the application
CMD ["node", "server.js"]