# Stage 1: build Astro frontend
FROM node:22-alpine AS builder

ARG PUBLIC_API_URL=/api
ARG PUBLIC_STRIPE_KEY

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./

ENV PUBLIC_API_URL=$PUBLIC_API_URL
ENV PUBLIC_STRIPE_KEY=$PUBLIC_STRIPE_KEY

RUN npm run build

# Stage 2: serve with nginx
FROM nginx:alpine

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
