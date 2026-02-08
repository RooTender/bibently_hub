# -------- builder --------
FROM node:22-trixie-slim as builder

WORKDIR /app

ARG PUBLIC_URL
ARG CDN_BASE_URL

ENV PUBLIC_URL=${PUBLIC_URL}
ENV CDN_BASE_URL=${CDN_BASE_URL}

COPY pnpm-lock.yaml package.json pnpm-workspace.yaml ./

RUN corepack enable && \
    --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

COPY . .

RUN pnpm build

# -------- runtime --------
FROM node:22-trixie-slim

WORKDIR /home/node/parabol

COPY --from=builder /app/build ./build
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY .env.example ./.env.example

USER node
EXPOSE 3000

CMD ["node", "./dist/web.js"]
