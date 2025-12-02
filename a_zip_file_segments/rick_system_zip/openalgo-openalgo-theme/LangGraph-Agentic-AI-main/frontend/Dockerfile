# ================================
# FRONTEND DOCKERFILE
# ================================
# File: frontend/Dockerfile

# Step 1: Build React app
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files first (for better caching)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code and .env file
COPY . .

# Set environment variable from build arg (passed from docker-compose)
ARG REACT_APP_WS_URL
ENV REACT_APP_WS_URL=$REACT_APP_WS_URL

# Build the app
RUN npm run build

# Step 2: Serve with Nginx
FROM nginx:stable-alpine

# Copy built app from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html


# Copy custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 3001

# Start nginx
CMD ["nginx", "-g", "daemon off;"]