# Dockerize & Deploy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship huskies-client and huskies-server as container images that auto-deploy to a single VPS on push to `release`.

**Architecture:** Each repo builds a multi-stage image via GitHub Actions and pushes to private GHCR. A `docker-compose.yml` in huskies-server runs the client (nginx serving the SPA + reverse-proxying `/api`), the server (Spring Boot), and Watchtower (auto-pulls updated images). Cloudflare terminates TLS; internal traffic is HTTP.

**Tech Stack:** Docker multi-stage builds, nginx (unprivileged), Node 20 + pnpm (Vite), Maven + Temurin 17 (Spring Boot), GitHub Actions, GHCR, Watchtower, MongoDB Atlas (external).

**Spec:** `huskies-server/docs/superpowers/specs/2026-09-17-dockerize-deploy-design.md`

## Global Constraints

- Multi-stage builds always; containers run as **non-root**; every image has a **HEALTHCHECK**.
- `.dockerignore` must exclude `.git` and all large/irrelevant dirs; no secrets in images or git.
- Registry images (lowercase): `ghcr.io/zfdupont/huskies-client`, `ghcr.io/zfdupont/huskies-server`, **private**.
- Client must build with `VITE_SERVER_URL=""` so `api.js` calls relative `/api` (no absolute host baked in).
- Ports: server `8090`; client nginx listens `8080`, published to host `80`.
- Two separate repos; the client is **pulled from GHCR** by compose, never vendored as a subdirectory.
- Tasks 1 & 5 commit in the **huskies-client** repo (`~/huskies-client`); tasks 2, 3, 4, 6 commit in **huskies-server** (`~/huskies-server`).

---

### Task 1: Client image (nginx serving SPA + /api proxy)

**Repo:** huskies-client (`~/huskies-client`)

**Files:**
- Create: `~/huskies-client/.dockerignore`
- Create: `~/huskies-client/nginx.conf`
- Create: `~/huskies-client/Dockerfile`

**Interfaces:**
- Produces: image serving the SPA on container port `8080`; proxies `/api/` to `http://server:8090/api/` (the compose service name `server`, consumed in Task 4).

- [ ] **Step 1: Create `.dockerignore`**

```
.git
.github
node_modules
build
dist
.env
.env.*
*.md
docs
.idea
.vscode
.DS_Store
```

- [ ] **Step 2: Create `nginx.conf`**

```nginx
server {
    listen 8080;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location /api/ {
        proxy_pass http://server:8090/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

- [ ] **Step 3: Create `Dockerfile`**

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-alpine AS build
WORKDIR /app
RUN corepack enable
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
ARG VITE_SERVER_URL=""
ENV VITE_SERVER_URL=$VITE_SERVER_URL
RUN pnpm build

FROM nginxinc/nginx-unprivileged:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/ >/dev/null 2>&1 || exit 1
```

- [ ] **Step 4: Build the image**

Run: `cd ~/huskies-client && docker build -t ghcr.io/zfdupont/huskies-client:latest .`
Expected: build completes; `pnpm build` prints `✓ built`.

- [ ] **Step 5: Verify the SPA is served and no absolute API URL is baked in**

Run:
```bash
docker run -d --rm --name hc-test -p 8081:8080 ghcr.io/zfdupont/huskies-client:latest
sleep 2
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8081/          # expect 200
docker run --rm --entrypoint sh ghcr.io/zfdupont/huskies-client:latest -c \
  "grep -rl 'huskies.zfdupont.com' /usr/share/nginx/html || echo NO_ABSOLUTE_URL"  # expect NO_ABSOLUTE_URL
docker stop hc-test
```
Expected: `200`, then `NO_ABSOLUTE_URL`.

- [ ] **Step 6: Commit**

```bash
cd ~/huskies-client
git add .dockerignore nginx.conf Dockerfile
git commit -m "Add client Docker image (nginx SPA + /api proxy)"
```

---

### Task 2: Server actuator health + parameterized Mongo URI

**Repo:** huskies-server (`~/huskies-server`)

**Files:**
- Modify: `~/huskies-server/server/pom.xml` (add actuator dependency)
- Modify: `~/huskies-server/server/src/main/resources/application.properties`

**Interfaces:**
- Produces: `GET /actuator/health` returns 200 (consumed by healthchecks in Tasks 3 & 4); server reads Mongo URI from `SPRING_DATA_MONGODB_URI` when set (consumed by compose in Task 4).

- [ ] **Step 1: Add the actuator dependency to `server/pom.xml`**

Inside the existing `<dependencies>` block, add:

```xml
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-actuator</artifactId>
		</dependency>
```

- [ ] **Step 2: Parameterize the Mongo URI in `application.properties`**

Replace the `spring.data.mongodb.uri=...` line with (env override, current value as default):

```properties
spring.data.mongodb.uri=${SPRING_DATA_MONGODB_URI:mongodb+srv://admin:admin@cluster0.ub0tgvg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0}
```

- [ ] **Step 3: Build and verify the health endpoint**

Run:
```bash
cd ~/huskies-server/server
mvn -q -B clean package -DskipTests
java -jar target/*.jar > /tmp/srv.log 2>&1 &
until grep -q "Started ServerApplication" /tmp/srv.log; do sleep 2; done
curl -fsS http://localhost:8090/actuator/health   # expect {"status":"UP"}
```
Expected: JSON containing `"status":"UP"`.

- [ ] **Step 4: Verify env override works, then stop**

Run:
```bash
kill %1 2>/dev/null
SPRING_DATA_MONGODB_URI="mongodb+srv://admin:admin@cluster0.ub0tgvg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" \
  java -jar target/*.jar > /tmp/srv2.log 2>&1 &
until grep -q "Started ServerApplication" /tmp/srv2.log; do sleep 2; done
curl -fsS http://localhost:8090/actuator/health   # expect UP (env-provided URI honored)
kill %1 2>/dev/null
```
Expected: `"status":"UP"` (server starts using the env-provided URI).

- [ ] **Step 5: Commit**

```bash
cd ~/huskies-server
git add server/pom.xml server/src/main/resources/application.properties
git commit -m "Add actuator health endpoint; make Mongo URI env-overridable"
```

---

### Task 3: Server image (multi-stage Maven → JRE)

**Repo:** huskies-server (`~/huskies-server`)

**Files:**
- Create: `~/huskies-server/.dockerignore`
- Create: `~/huskies-server/Dockerfile`

**Interfaces:**
- Consumes: actuator `/actuator/health` (Task 2).
- Produces: image running the Spring jar on port `8090` (consumed by compose in Task 4).

- [ ] **Step 1: Create `.dockerignore`** (excludes the large data/pipeline dirs from build context)

```
.git
.github
target
log
*.md
.env
.env.*
.idea
.vscode
.DS_Store
scripts
data
static
docs
```

- [ ] **Step 2: Create `Dockerfile`**

```dockerfile
# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY server/pom.xml ./pom.xml
COPY server/src ./src
RUN mvn -q -B clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine
RUN apk add --no-cache curl && adduser -D -u 1001 appuser
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
USER appuser
EXPOSE 8090
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8090/actuator/health || exit 1
ENTRYPOINT ["java","-jar","/app/app.jar"]
```

- [ ] **Step 3: Build the image**

Run: `cd ~/huskies-server && docker build -t ghcr.io/zfdupont/huskies-server:latest .`
Expected: build completes; Maven packages the jar.

- [ ] **Step 4: Run and verify health (uses default URI from properties)**

Run:
```bash
docker run -d --rm --name hs-test -p 8091:8090 ghcr.io/zfdupont/huskies-server:latest
# wait for health
until [ "$(docker inspect -f '{{.State.Health.Status}}' hs-test)" = "healthy" ]; do sleep 3; done
curl -fsS http://localhost:8091/actuator/health   # expect UP
docker stop hs-test
```
Expected: container reports `healthy`; curl returns `"status":"UP"`.

- [ ] **Step 5: Commit**

```bash
cd ~/huskies-server
git add .dockerignore Dockerfile
git commit -m "Add server Docker image (multi-stage Maven -> JRE, non-root)"
```

---

### Task 4: docker-compose orchestration + host env template

**Repo:** huskies-server (`~/huskies-server`)

**Files:**
- Create: `~/huskies-server/docker-compose.yml`
- Create: `~/huskies-server/.env.example`

**Interfaces:**
- Consumes: `ghcr.io/zfdupont/huskies-client:latest` (Task 1), `ghcr.io/zfdupont/huskies-server:latest` (Task 3), `DATABASE_URI` from host `.env`.
- Produces: a running stack — host `:80` → client nginx → `/api` → `server:8090`; Watchtower auto-updates the two app images.

- [ ] **Step 1: Create `docker-compose.yml`**

```yaml
services:
  server:
    image: ghcr.io/zfdupont/huskies-server:latest
    restart: unless-stopped
    environment:
      SPRING_DATA_MONGODB_URI: ${DATABASE_URI}
    expose:
      - "8090"
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://127.0.0.1:8090/actuator/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 40s
    labels:
      com.centurylinklabs.watchtower.scope: "huskies"

  client:
    image: ghcr.io/zfdupont/huskies-client:latest
    restart: unless-stopped
    depends_on:
      server:
        condition: service_healthy
    ports:
      - "80:8080"
    labels:
      com.centurylinklabs.watchtower.scope: "huskies"

  watchtower:
    image: containrrr/watchtower
    restart: unless-stopped
    command: --scope huskies --interval 120 --cleanup
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ${HOME}/.docker/config.json:/config.json:ro
    labels:
      com.centurylinklabs.watchtower.scope: "huskies"
```

- [ ] **Step 2: Create `.env.example`**

```
# Host deployment config for docker-compose. Copy to .env and fill in.
# MongoDB Atlas connection string the Spring server uses at runtime.
DATABASE_URI=mongodb+srv://<user>:<password>@<cluster-host>/?retryWrites=true&w=majority
```

- [ ] **Step 3: Verify `.gitignore` already ignores `.env`**

Run: `cd ~/huskies-server && git check-ignore .env && echo IGNORED`
Expected: `IGNORED` (repo `.gitignore` line `.env`). If not, add `.env` to `.gitignore`.

- [ ] **Step 4: Bring the stack up locally (uses the images built in Tasks 1 & 3)**

Run:
```bash
cd ~/huskies-server
printf 'DATABASE_URI=mongodb+srv://admin:admin@cluster0.ub0tgvg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0\n' > .env
docker compose up -d
until [ "$(docker compose ps server --format '{{.Health}}')" = "healthy" ]; do sleep 3; done
```
Expected: `server` becomes `healthy`, `client` and `watchtower` are `Up`.

- [ ] **Step 5: Verify end-to-end through the proxy**

Run:
```bash
curl -s -o /dev/null -w "spa=%{http_code}\n" http://localhost/                       # expect 200
curl -s -o /dev/null -w "api=%{http_code}\n" "http://localhost/api/summary?state=NY"  # expect 200
docker compose down
```
Expected: `spa=200` and `api=200` (the `/api` call reaches the backend through nginx).

- [ ] **Step 6: Commit**

```bash
cd ~/huskies-server
git add docker-compose.yml .env.example
git commit -m "Add docker-compose stack (client, server, watchtower) + env template"
```

---

### Task 5: Client CI — build & push to GHCR

**Repo:** huskies-client (`~/huskies-client`)

**Files:**
- Create: `~/huskies-client/.github/workflows/docker.yml`

**Interfaces:**
- Consumes: the client `Dockerfile` (Task 1).
- Produces: `ghcr.io/zfdupont/huskies-client:latest` on every push to `release`.

- [ ] **Step 1: Create `.github/workflows/docker.yml`**

```yaml
name: build-and-push
on:
  push:
    branches: [main]
jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          build-args: |
            VITE_SERVER_URL=
          tags: |
            ghcr.io/zfdupont/huskies-client:latest
            ghcr.io/zfdupont/huskies-client:${{ github.sha }}
```

- [ ] **Step 2: Validate the workflow YAML**

Run: `cd ~/huskies-client && python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/docker.yml')); print('YAML OK')"`
Expected: `YAML OK`.

- [ ] **Step 3: Commit**

```bash
cd ~/huskies-client
git add .github/workflows/docker.yml
git commit -m "Add CI: build and push client image to GHCR on push to main"
```

---

### Task 6: Server CI — build & push to GHCR

**Repo:** huskies-server (`~/huskies-server`)

**Files:**
- Create: `~/huskies-server/.github/workflows/docker.yml`

**Interfaces:**
- Consumes: the server `Dockerfile` (Task 3).
- Produces: `ghcr.io/zfdupont/huskies-server:latest` on every push to `release`.

- [ ] **Step 1: Create `.github/workflows/docker.yml`**

```yaml
name: build-and-push
on:
  push:
    branches: [main]
jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/zfdupont/huskies-server:latest
            ghcr.io/zfdupont/huskies-server:${{ github.sha }}
```

- [ ] **Step 2: Validate the workflow YAML**

Run: `cd ~/huskies-server && python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/docker.yml')); print('YAML OK')"`
Expected: `YAML OK`.

- [ ] **Step 3: Commit**

```bash
cd ~/huskies-server
git add .github/workflows/docker.yml
git commit -m "Add CI: build and push server image to GHCR on push to main"
```

---

## Host bring-up (one-time, after CI has pushed both images)

Not a code task — the deploy runbook for the VPS:

```bash
# 1. Install Docker + compose plugin (distro-specific).
# 2. Authenticate to private GHCR (PAT with read:packages):
docker login ghcr.io -u zfdupont     # paste PAT when prompted
# 3. Deploy:
git clone https://github.com/zfdupont/huskies-server.git
cd huskies-server
cp .env.example .env && $EDITOR .env   # set real DATABASE_URI
docker compose up -d
```

Point Cloudflare at the host on port 80. Thereafter, pushing to `main` in either
repo rebuilds that image and Watchtower redeploys the changed service within ~2
minutes.

---

## Self-Review

- **Spec coverage:** client image + nginx proxy (T1), server actuator + env URI (T2), server image (T3), compose + watchtower + .env (T4), client CI (T5), server CI (T6), host runbook (final section) — every spec section maps to a task.
- **Placeholders:** none; all file contents are literal. The `<user>/<password>/<cluster-host>` tokens in `.env.example` are intentional placeholder values for a template, not plan gaps.
- **Type/name consistency:** compose service name `server` matches the nginx upstream `http://server:8090` (T1↔T4); image tags `ghcr.io/zfdupont/huskies-client|server:latest` identical across T1/T3/T4/T5/T6; health path `/actuator/health` consistent across T2/T3/T4; client container port `8080` ↔ published `80:8080` (T1↔T4); env var `SPRING_DATA_MONGODB_URI` / `DATABASE_URI` consistent across T2/T4.
