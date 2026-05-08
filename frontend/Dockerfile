FROM node:22-slim AS deps

WORKDIR /app
RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .pnpmfile.cjs* ./
RUN pnpm install --frozen-lockfile

FROM deps AS build

ARG NEXT_PUBLIC_API_URL=http://localhost:8787
ARG NEXT_PUBLIC_WS_URL=ws://localhost:8787
ARG NEXT_PUBLIC_BATON_API_KEY=
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_WS_URL=$NEXT_PUBLIC_WS_URL \
    NEXT_PUBLIC_BATON_API_KEY=$NEXT_PUBLIC_BATON_API_KEY \
    NEXT_TELEMETRY_DISABLED=1

COPY . .
RUN pnpm build

FROM node:22-slim AS runtime

WORKDIR /app
RUN corepack enable

ENV NODE_ENV=production \
    PORT=3000 \
    NEXT_TELEMETRY_DISABLED=1

COPY --from=build /app/package.json /app/pnpm-lock.yaml /app/pnpm-workspace.yaml ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/.next ./.next
COPY --from=build /app/next.config.js ./next.config.js

EXPOSE 3000

CMD ["pnpm", "start"]
