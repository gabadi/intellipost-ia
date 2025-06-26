# Use Node.js 20 LTS
FROM node:20-alpine

# Set environment variables
ENV NODE_ENV=development

# Install system dependencies
RUN apk add --no-cache curl

# Set work directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Run the application
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
