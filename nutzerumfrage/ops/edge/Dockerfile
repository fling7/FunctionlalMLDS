FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 8080 8443
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/healthz >/dev/null || exit 1
