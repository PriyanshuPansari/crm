# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app

# Copy package.json & package-lock.json first for caching
COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

# Stage 2: Serve
FROM nginx:stable-alpine

COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx config (optional)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
