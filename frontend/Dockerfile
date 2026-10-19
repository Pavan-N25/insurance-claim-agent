# Multi-stage Dockerfile for React frontend
FROM node:20-alpine AS build

WORKDIR /app

# Copy lockfile first for layer caching
COPY frontend/package.json frontend/package-lock.json ./
# npm ci installs exact locked versions — never install ranges
RUN npm ci

COPY frontend ./
RUN npm run build

# Production serve with Nginx
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

# Custom nginx config for SPA routing and API reverse proxy
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    location /api/ { \
        proxy_pass http://backend:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
    location /uploads/ { \
        proxy_pass http://backend:8000; \
    } \
    location /api/v1/ws/ { \
        proxy_pass http://backend:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "Upgrade"; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
