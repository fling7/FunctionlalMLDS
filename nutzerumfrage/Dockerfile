FROM node:22-bookworm-slim AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY index.html admin.html vite.config.js ./
COPY public ./public
COPY src ./src
COPY BuildOutput ./BuildOutput
RUN npm run build

FROM nginx:1.27-alpine AS web

COPY ops/study-nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/healthz >/dev/null || exit 1

FROM node:22-bookworm-slim AS api

ENV NODE_ENV=production \
    SURVEY_API_HOST=0.0.0.0 \
    SURVEY_API_PORT=3001 \
    SURVEY_DB_PATH=/data/survey.sqlite \
    SURVEY_SECURE_COOKIE=true
WORKDIR /app
COPY server ./server
RUN mkdir -p /data && chown -R node:node /app /data
USER node
EXPOSE 3001
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:3001/api/health').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"
CMD ["node", "server/index.mjs"]
