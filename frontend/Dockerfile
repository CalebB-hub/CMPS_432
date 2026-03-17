# ── Build stage ───────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .
RUN npm run build

# ── Serve stage ───────────────────────────────────────────────────────────────
# The compiled dist/ folder is picked up by the nginx service via a shared volume
# or baked directly into the nginx image. Here we keep it as a separate stage
# so the nginx Dockerfile can COPY --from=frontend /app/dist /usr/share/nginx/html
FROM scratch AS export
COPY --from=builder /app/dist /dist
