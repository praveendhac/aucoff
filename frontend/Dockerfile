# AUCoFF frontend image (Next.js standalone output). Official minimal base pinned by digest
# (LIC-2 exception, LICENCES.md section 5a). Non-root, read-only-rootfs friendly.
FROM docker.io/library/node@sha256:7f486cabe892bff8fef04c0f7da8dba84a560be3e4e2740b7a86afc57ebec315 AS deps
WORKDIR /app
COPY package.json package-lock.json ./
COPY stubs ./stubs
RUN npm ci

FROM docker.io/library/node@sha256:7f486cabe892bff8fef04c0f7da8dba84a560be3e4e2740b7a86afc57ebec315 AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM docker.io/library/node@sha256:7f486cabe892bff8fef04c0f7da8dba84a560be3e4e2740b7a86afc57ebec315
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000 HOSTNAME=0.0.0.0
# npm, npx and corepack are not needed at run time (and carry their own vulnerable bundled
# packages); removing them adds nothing to the base image.
RUN rm -rf /usr/local/lib/node_modules /usr/local/bin/npm /usr/local/bin/npx /usr/local/bin/corepack
RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin aucoff
WORKDIR /app
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
USER 10001
EXPOSE 3000
CMD ["node", "server.js"]
