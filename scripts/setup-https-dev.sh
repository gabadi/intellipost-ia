#!/bin/bash
# Setup HTTPS for local development using mkcert

set -e

echo "=== HTTPS Development Setup ==="
echo ""

# Check if mkcert is installed
if ! command -v mkcert &> /dev/null; then
    echo "mkcert is not installed. Please install it first:"
    echo ""
    echo "macOS: brew install mkcert"
    echo "Linux: https://github.com/FiloSottile/mkcert#installation"
    echo ""
    exit 1
fi

# Create certificates directory
CERT_DIR="../certs"
mkdir -p $CERT_DIR

# Install local CA
echo "Installing local certificate authority..."
mkcert -install

# Generate certificates
echo "Generating certificates for localhost..."
cd $CERT_DIR
mkcert -cert-file localhost.pem -key-file localhost-key.pem localhost 127.0.0.1 ::1

echo ""
echo "✅ HTTPS certificates generated successfully!"
echo ""
echo "Certificate location:"
echo "  - Certificate: $(pwd)/localhost.pem"
echo "  - Private Key: $(pwd)/localhost-key.pem"
echo ""
echo "To use HTTPS in development:"
echo ""
echo "1. With uvicorn directly:"
echo "   uvicorn main:app --ssl-keyfile=../certs/localhost-key.pem --ssl-certfile=../certs/localhost.pem"
echo ""
echo "2. With a reverse proxy (recommended for production-like setup):"
echo "   See ../nginx/nginx.dev.conf for nginx configuration"
echo ""

# Create sample nginx configuration
mkdir -p ../nginx
cat > ../nginx/nginx.dev.conf << 'EOF'
# Nginx configuration for HTTPS development
server {
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate /app/certs/localhost.pem;
    ssl_certificate_key /app/certs/localhost-key.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API proxy
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend proxy
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support for hot reload
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name localhost;
    return 301 https://$server_name$request_uri;
}
EOF

echo "✅ Sample nginx configuration created at ../nginx/nginx.dev.conf"
