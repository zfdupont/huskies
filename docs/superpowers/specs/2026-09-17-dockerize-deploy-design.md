# Dockerize & Deploy huskies-client + huskies-server

Date: 2026-09-17
Status: design (pending review)

## Goal

Replace `run.sh` (which builds the server with maven, clones the client into
`server/static/app`, and serves it) with a container-based deploy where pushing
to `main` in either repo automatically redeploys that service on a single Linux
VPS. Keep the two repos independent — no vendoring one inside the other.

## Decisions (agreed)

- **Host:** single Linux VPS, Docker + docker compose, accessed via SSH.
- **Deploy trigger:** GitHub Actions builds each repo's image and pushes to GHCR;
  Watchtower on the host polls GHCR and auto-pulls/restarts the changed service.
  Each service redeploys on its own change (client change → client only, etc.).
- **Orchestration:** `docker-compose.yml` lives in **huskies-server** and
  references both images from GHCR (client image is pulled, not built from a
  subdirectory).
- **Routing:** the client's nginx serves the SPA and reverse-proxies `/api` to
  the backend, so the browser talks to one origin (no CORS needed).
- **TLS:** terminated at Cloudflare. Everything behind it is plain HTTP; the
  `client` container publishes port 80 on the host.
- **Registry visibility:** private GHCR packages; pulls authenticated via a
  read-only PAT in the host's `docker login` (never committed).

## Architecture

```
Cloudflare (TLS)
    │  https://huskies.zfdupont.com  ->  http
    ▼
host:80  ──►  client container (nginx, unprivileged, :8080)
                 ├─ /        -> static SPA (Vite build)
                 └─ /api/    -> proxy_pass http://server:8090/api/
                                    │
                                    ▼
                              server container (Spring Boot, :8090)
                                    │
                                    ▼
                              MongoDB Atlas (external, unchanged)

watchtower container ──► polls GHCR every 120s, pulls :latest, recreates
                         client/server when their image digest changes
```

Two images, each built by its own repo's CI:
- `ghcr.io/zfdupont/huskies-client:latest`
- `ghcr.io/zfdupont/huskies-server:latest`

## Components

### huskies-client (new files)

- **`Dockerfile`** — multi-stage:
  - Stage `build`: `node:20-alpine`, `corepack enable` (pnpm), `pnpm install
    --frozen-lockfile`, copy source, `pnpm build` → `build/`.
    - `ARG VITE_SERVER_URL=""` set as env before build so `api.js` baseURL
      resolves to relative `/api`. (Vite prefers a real env var over the value
      in `.env.production`, so the committed prod URL is overridden.)
  - Stage runtime: `nginxinc/nginx-unprivileged:alpine` (runs as non-root uid
    101, listens on 8080). Copy `build/` to the web root and copy `nginx.conf`.
    HEALTHCHECK: `wget -qO- http://localhost:8080/ || exit 1`.
- **`nginx.conf`**:
  - `listen 8080;`
  - `location /api/ { proxy_pass http://server:8090/api/; }` with
    `X-Forwarded-*` and `Host` headers; cookies pass through (supports the axios
    `withCredentials` calls).
  - `location / { try_files $uri $uri/ /index.html; }` (SPA fallback).
  - Upstream host `server` is the compose service name (documented coupling).
- **`.dockerignore`** — `.git`, `.github`, `node_modules`, `build`, `dist`,
  `.env*` (keep none), `*.md`, `.idea`, `.vscode`, `.DS_Store`.
- **`.github/workflows/docker.yml`** — on `push` to `main`:
  `docker/login-action` to GHCR with `GITHUB_TOKEN` (`packages: write`),
  `docker/build-push-action` context `.`, `build-args: VITE_SERVER_URL=`,
  tags `ghcr.io/zfdupont/huskies-client:latest` and `:${{ github.sha }}`.

### huskies-server (new files)

- **`Dockerfile`** (repo root, builds the `server/` module) — multi-stage:
  - Stage `build`: `maven:3.9-eclipse-temurin-17`; copy `server/pom.xml`, warm
    dependencies (`mvn -q dependency:go-offline`), copy `server/src`,
    `mvn -q clean package -DskipTests` → `target/*.jar`.
  - Stage runtime: `eclipse-temurin:17-jre`; create non-root user (uid 1001),
    copy the jar, `EXPOSE 8090`, `USER` non-root,
    `ENTRYPOINT ["java","-jar","/app/app.jar"]`.
    HEALTHCHECK against `/actuator/health` (see pom change below).
- **`server/pom.xml`** — add `spring-boot-starter-actuator` so the container has
  a real health endpoint (`/actuator/health`). Expose only `health`.
- **`server/src/main/resources/application.properties`** — parameterize the
  Mongo URI:
  `spring.data.mongodb.uri=${SPRING_DATA_MONGODB_URI:<current default>}`.
  Keeps local `mvn spring-boot:run` working, while compose overrides it via env
  from the host `.env` (moves the production secret out of the container).
- **`docker-compose.yml`** (repo root):
  - `server`: image `ghcr.io/zfdupont/huskies-server:latest`,
    `environment: SPRING_DATA_MONGODB_URI: ${DATABASE_URI}`, `expose: ["8090"]`,
    `restart: unless-stopped`, healthcheck.
  - `client`: image `ghcr.io/zfdupont/huskies-client:latest`,
    `ports: ["80:8080"]`, `depends_on: [server]`, `restart: unless-stopped`.
  - `watchtower`: `containrrr/watchtower`, mounts `/var/run/docker.sock` and the
    host `~/.docker/config.json` (read-only, for private GHCR auth),
    `WATCHTOWER_POLL_INTERVAL=120`, `WATCHTOWER_CLEANUP=true`,
    scoped to the compose project.
- **`.dockerignore`** — `.git`, `.github`, `target`, `log`, `*.md`, `.env`,
  `.idea`, `.DS_Store`, `scripts/` (the Python analysis pipeline is not part of
  the server image).
- **`.github/workflows/docker.yml`** — same shape as the client workflow,
  pushing `ghcr.io/zfdupont/huskies-server:latest` and `:${{ github.sha }}`.
- **`.env.example`** — `DATABASE_URI=` (the Mongo Atlas URI, filled on the host).

## Config & secrets

- Host `.env` (gitignored) holds `DATABASE_URI`. compose injects it into the
  server as `SPRING_DATA_MONGODB_URI`.
- Private GHCR pull auth: on the host, `docker login ghcr.io -u zfdupont` with a
  PAT scoped `read:packages`. Both `docker compose pull` and Watchtower reuse
  `~/.docker/config.json`. No registry creds in git.
- `GITHUB_TOKEN` (automatic) is sufficient for CI to push to GHCR under the same
  owner; no extra secret needed for the push side.

## Data flow

Browser → Cloudflare (TLS) → host:80 → client nginx. `/` served statically;
`/api/*` proxied to `server:8090`. Server queries Mongo Atlas. Same-origin, so
the existing CORS config is unused but left in place as a harmless fallback.

## Deployment runbook

First-time host setup (once):
1. Install Docker + compose plugin.
2. `git clone` huskies-server; `cp .env.example .env` and fill `DATABASE_URI`.
3. `docker login ghcr.io -u zfdupont` (PAT with `read:packages`).
4. `docker compose up -d`.

Ongoing: push to `main` → CI builds/pushes the image → Watchtower pulls and
restarts that service within the poll interval. No SSH step.

## Testing / verification

- Build both images locally (`docker build`) to confirm they compile and start.
- `docker compose up` locally with a test `DATABASE_URI`; verify:
  - `GET http://localhost/` serves the SPA.
  - `GET http://localhost/api/summary?state=NY` returns 200 through the proxy.
  - Server healthcheck reports healthy.
- Confirm the client bundle was built with relative `/api` (no absolute
  `VITE_SERVER_URL` baked in).

## Out of scope

- No TLS/Caddy in compose (Cloudflare handles it).
- No database container (Mongo Atlas stays external).
- No multi-host / orchestrator (single VPS).
- The Python analysis pipeline under `scripts/` stays a manual/local process; it
  is not containerized here.

## Open/minor choices

- Mongo URI default: parameterize **with** the current value as the fallback
  default (keeps local dev working) rather than removing it entirely. Can be
  tightened to no-default later if desired.
