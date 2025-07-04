# HTTPS Configuration for Production

This document outlines the HTTPS configuration for the IntelliPost AI Backend in production environments.

## Configuration Overview

The application automatically enforces HTTPS security in production environments through:

1. **Automatic HTTPS Enforcement**: When `INTELLIPOST_ENVIRONMENT=production`, HTTPS-only mode is automatically enabled
2. **Security Headers**: Comprehensive security headers are added to all responses
3. **Secure Cookies**: Cookies are automatically configured with secure flags
4. **HSTS**: HTTP Strict Transport Security headers are added

## Environment Variables

### Required for Production

```bash
# Core environment
INTELLIPOST_ENVIRONMENT=production

# Security (automatically enforced in production)
INTELLIPOST_HTTPS_ONLY=true
INTELLIPOST_SECURE_COOKIES=true

# HSTS configuration (optional, defaults shown)
INTELLIPOST_HSTS_MAX_AGE=31536000  # 1 year in seconds

# API configuration
INTELLIPOST_API_HOST=0.0.0.0  # Allow external connections
INTELLIPOST_API_PORT=8080     # Or your preferred port

# Required secrets (must be changed from defaults)
INTELLIPOST_SECRET_KEY=your-production-secret-key-here
INTELLIPOST_USER_JWT_SECRET_KEY=your-jwt-secret-key-here
```

### Optional Security Configuration

```bash
# HTTPS redirect (useful for load balancers)
INTELLIPOST_HTTPS_REDIRECT=true
```

## Security Headers Added

The following security headers are automatically added in production:

- **Strict-Transport-Security**: Enforces HTTPS for 1 year
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-XSS-Protection**: Enables XSS filtering
- **Referrer-Policy**: Controls referrer information
- **Content-Security-Policy**: Restricts resource loading
- **Permissions-Policy**: Controls browser features

## Deployment Scenarios

### 1. Direct HTTPS (with TLS termination at the application)

When running the application with TLS termination directly:

```bash
# Use uvicorn with SSL
uvicorn main:app --host 0.0.0.0 --port 443 \
  --ssl-keyfile=/path/to/private.key \
  --ssl-certfile=/path/to/certificate.crt
```

### 2. Behind Load Balancer/Reverse Proxy

When running behind a load balancer or reverse proxy (recommended):

```bash
# Load balancer handles TLS termination
# Application runs on HTTP internally
uvicorn main:app --host 0.0.0.0 --port 8080
```

**Load Balancer Configuration** (nginx example):
```nginx
server {
    listen 443 ssl http2;
    server_name api.intellipost.ai;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Container Deployment (Docker)

```dockerfile
# Production Dockerfile
FROM python:3.11-slim

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Run in production mode
ENV INTELLIPOST_ENVIRONMENT=production
ENV INTELLIPOST_API_HOST=0.0.0.0
ENV INTELLIPOST_API_PORT=8080

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 4. Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: intellipost-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: intellipost-backend
  template:
    metadata:
      labels:
        app: intellipost-backend
    spec:
      containers:
      - name: backend
        image: intellipost/backend:latest
        ports:
        - containerPort: 8080
        env:
        - name: INTELLIPOST_ENVIRONMENT
          value: "production"
        - name: INTELLIPOST_API_HOST
          value: "0.0.0.0"
        - name: INTELLIPOST_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: intellipost-secrets
              key: secret-key
---
apiVersion: v1
kind: Service
metadata:
  name: intellipost-backend-service
spec:
  selector:
    app: intellipost-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: intellipost-backend-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.intellipost.ai
    secretName: intellipost-tls
  rules:
  - host: api.intellipost.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: intellipost-backend-service
            port:
              number: 80
```

## Testing HTTPS Configuration

### 1. Check Security Status

```bash
curl https://api.intellipost.ai/security-status
```

Expected response:
```json
{
  "environment": "production",
  "https_only": true,
  "secure_cookies": true,
  "hsts_enabled": true,
  "security_headers_enabled": true
}
```

### 2. Verify Security Headers

```bash
curl -I https://api.intellipost.ai/
```

Should include headers like:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
```

### 3. Test HTTPS Redirect

```bash
curl -I http://api.intellipost.ai/
```

Should return:
```
HTTP/1.1 301 Moved Permanently
Location: https://api.intellipost.ai/
```

## Security Considerations

1. **Certificate Management**: Use automated certificate management (Let's Encrypt, AWS ACM)
2. **HSTS Preloading**: Consider adding your domain to the HSTS preload list
3. **Perfect Forward Secrecy**: Ensure your TLS configuration supports PFS
4. **TLS Version**: Use TLS 1.2+ only, disable older versions
5. **Cipher Suites**: Use strong cipher suites only

## Troubleshooting

### Common Issues

1. **"Secret key must be changed from default value in production"**
   - Ensure `INTELLIPOST_SECRET_KEY` is set to a unique value

2. **HTTPS redirect loops**
   - Check `X-Forwarded-Proto` headers from load balancer
   - Verify proxy configuration

3. **Mixed content warnings**
   - Ensure all resources (frontend, API calls) use HTTPS
   - Check CORS configuration includes HTTPS origins

### Debug Mode

To debug HTTPS issues without full enforcement:

```bash
INTELLIPOST_ENVIRONMENT=staging
INTELLIPOST_HTTPS_ONLY=false
INTELLIPOST_LOG_LEVEL=DEBUG
```

This enables security headers but disables HTTPS enforcement and redirects.
