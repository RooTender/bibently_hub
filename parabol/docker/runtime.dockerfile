# syntax=docker/dockerfile:1

FROM parabol:base
WORKDIR /home/node/parabol

COPY . .

COPY --from=parabol:builder /app/dist ./dist
COPY --from=parabol:builder /app/build ./build

RUN corepack enable pnpm \
 && pnpm install --prod --no-frozen-lockfile

USER node
