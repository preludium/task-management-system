FROM node:22-alpine AS builder

RUN corepack enable pnpm

WORKDIR /app

COPY package.json ./
COPY pnpm-lock.yaml ./

RUN pnpm install --frozen-lockfile

COPY . .

RUN pnpm build

FROM nginx:alpine as runner

COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=builder /app/favicon.svg /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
