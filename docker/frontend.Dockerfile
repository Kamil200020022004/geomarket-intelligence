# Obraz frontendu Kamila — przygotowany przez Sebastiana do Docker Compose całości (lokalnie / VPS).
# Plik leży poza folderem frontend/, żeby nie zmieniać kodu autora. Produkcyjnie frontend działa też na Vercel.
# Kontekst budowania: frontend/.

# Etap 1: budowanie statycznych plików (Vite). Zmienne VITE_* są wpisywane do kodu w czasie budowania.
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL=http://localhost:8000
ARG VITE_MARKET_API_URL=http://localhost:8000
ARG VITE_FAVORITES_PROVIDER=api
ENV VITE_API_URL=$VITE_API_URL \
    VITE_MARKET_API_URL=$VITE_MARKET_API_URL \
    VITE_FAVORITES_PROVIDER=$VITE_FAVORITES_PROVIDER
RUN npm run build

# Etap 2: serwer nginx z samymi plikami statycznymi (bez Node.js w obrazie końcowym).
FROM nginx:1.29-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY --from=frontend-nginx nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
