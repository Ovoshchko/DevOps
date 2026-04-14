FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY public ./public
COPY src ./src
COPY tsconfig.json ./

RUN npm run build


FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
