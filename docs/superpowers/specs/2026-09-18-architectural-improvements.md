# Architectural Improvements: huskies-server

Date: 2026-09-18
Status: spec (issue tracker, pending prioritization)

## Goal

Track architectural, performance, and cleanup issues found in a scan of the
server (`server/`) and the Python pipeline (`scripts/`). Each item is
independently actionable; the checkboxes track completion. Items are grouped by
impact so a first branch can pick the top of each section.

Scope note: the server is a read-only Spring Boot API over MongoDB; the pipeline
is a separate GerryChain data-generation process. The two meet only at the
`plans` and `states` Mongo collections.

## High impact

- [x] **H1. Remove unused GeoTools dependency from the server.** (done, branch `arch/cleanup-and-caching`)
  - Where: `server/pom.xml:58-62` (`gt-shapefile:28-SNAPSHOT`), plus the two
    `<repositories>` blocks (`:71-86`) and the `geotools.version` property (`:18`).
  - Why: nothing in `server/src/main/java` imports GeoTools/JTS/opengis
    (verified by grep; only Spring + Jackson are used). It drags in the entire
    OSGeo tree (EMF, JAI, EJML, referencing), slows first builds via
    `repo.osgeo.org`, and is the source of the non-reproducible `-SNAPSHOT`.
  - Do: delete the dependency, both repositories, and the version property.
    Rebuild to confirm the jar still compiles and starts. Largest cleanup.

- [x] **H2. Add response caching for the effectively-static dataset.** (done, branch `arch/cleanup-and-caching`; uses default in-memory `ConcurrentMapCacheManager`, so a pipeline reload needs a process restart to refresh)
  - Where: `EnsembleService.getSummary`, `DistrictPlanService.getDistrictPlan`.
  - Why: the data is ~3 states x 6 plans + 3 summaries and changes only on a
    manual `fill_database` run, yet every request hits Mongo and re-serializes.
  - Do: `@EnableCaching` + `@Cacheable` keyed on `(state, name)` / `state`. The
    whole dataset fits in memory; every request after the first becomes a memory
    hit, eliminating the DB round-trip and the serialization cost. Highest
    runtime win. (Provide a cache-eviction hook or accept process-restart to
    refresh after a pipeline reload.)

- [x] **H3. Avoid deserialize-then-reserialize of multi-MB GeoJSON on `/api/plan`.** (done, branch `arch/cleanup-and-caching`; service projects only `geojson` and returns `Document.toJson()` as a raw string, controller serves it as `application/json`. `DistrictPlan`/`FeatureCollectionPOJO` retained solely as schema + `@CompoundIndex` definition. Verified end-to-end against a local MongoDB: correct JSON output, `NumberLong` emitted as a plain number, and a confirmed cache hit on repeat requests.)
  - Where: `DistrictPlanController.getPlan` → loads full `DistrictPlan` into
    `FeatureCollectionPOJO` (`ArrayList<Map<String,Object>>`), then Jackson
    reserializes on the way out.
  - Why: for the multi-MB payloads described in `fill_database.py`, this is
    per-request CPU + heap churn for no transformation.
  - Do: store/serve the GeoJSON as a raw JSON string field and return it
    directly, or use a Mongo projection to fetch only the `geojson` subdocument.
    Fully subsumed by H2 for cached reads, but worth fixing independently.

## Medium impact

- [x] **M1. Remove duplicate/conflicting Mongo + Jackson dependency pins in pom.** (done, branch `arch/cleanup-and-caching`)
  - Where: `server/pom.xml` declares `spring-data-mongodb` twice with conflicting
    versions (`:36-40` = 4.0.0, `:63-67` = 4.0.1); `jackson-annotations` is pinned
    to 2.14.1 (`:52-56`).
  - Why: `starter-data-mongodb` and the Spring Boot BOM already manage these
    versions; the explicit pins invite drift.
  - Do: delete both explicit `spring-data-mongodb` declarations and the
    `jackson-annotations` pin; let the parent BOM govern.

- [x] **M2. Centralize error handling in a `@RestControllerAdvice`.** (done, branch `arch/cleanup-and-caching`; added `GlobalExceptionHandler` in `com.huskies.server` mapping `ResourceNotFoundException` → 404 and `Exception` → 500. `EnsembleController` now returns typed `ResponseEntity<Ensemble>`; `DistrictPlanController` keeps `ResponseEntity<String>` — H3 already made `/api/plan` serve raw GeoJSON, so the `FeatureCollectionPOJO` note below is stale. Both controllers shed their try-catch. Behavior preserved: `ResourceNotFoundException` carries no message, so a 404 body is still empty.)
  - Where: `EnsembleController` and `DistrictPlanController` repeat the same
    404/500 try-catch around raw untyped `ResponseEntity`.
  - Do: one handler mapping `ResourceNotFoundException` → 404 and `Exception` →
    500, so controllers return typed `ResponseEntity<Ensemble>` /
    `<FeatureCollectionPOJO>` with no per-method boilerplate.

- [x] **M3. Split Docker dependency layer from source layer.** (done, branch `arch/cleanup-and-caching`; `COPY pom.xml` → `RUN mvn -B dependency:go-offline` → `COPY src` → `RUN mvn -B clean package -DskipTests`. Deliberately did **not** add `-o` to the final package step: `dependency:go-offline` does not reliably prefetch every artifact the `package`/repackage/surefire goals need, so forcing offline mode risks a broken build. Caching still holds — the go-offline layer is cached until `pom.xml` changes. Not verified with a live `docker build`: the local Docker daemon was not running.)
  - Where: `Dockerfile:4-6` copies `pom.xml` + `src`, then runs `mvn package` in
    one step, so any source edit re-downloads all dependencies.
  - Do: `COPY pom.xml` → `RUN mvn -B dependency:go-offline` → `COPY src` → `RUN
    mvn -B clean package -DskipTests -o`. Caches deps across code changes. Gets
    much smaller once H1 lands.

- [x] **M4. De-duplicate and fix the scripts Mongo engine.** (done, branch `arch/cleanup-and-caching`; deleted `scripts/MongoEngine.py` and repointed the sole importer `scripts/tests/mongo_engine_test.py` to `from mongo_engine import MongoEngine`. Guarded `__init__` with an `_initialized` flag so the singleton connects once instead of reconnecting on every construction. Caveat: that ad-hoc test was already broken — it calls `insert_geodataframe` with 3 args where 4 are required and hardcodes an absolute geojson path — and its two db-name constructions now collapse to the first, which is the intended singleton behavior; left otherwise as-is.)
  - Where: `scripts/mongo_engine.py` (used) vs `scripts/MongoEngine.py` (stale
    near-duplicate).
  - Do: delete the capitalized copy. Also fix the singleton: `__new__` returns a
    cached instance but `__init__` re-runs on every construction, so
    `MongoEngine('huskies', ...)` reconnects each call (`fill_database.py`
    constructs it 4x). Guard `__init__` with an initialized flag or reuse one
    instance.

## Lower impact

- [x] **L1. Remove dead `@EnableMongoRepositories` (or adopt repositories).** (done, branch `arch/cleanup-and-caching`; removed the annotation and its import from `ServerApplication`. Access stays on `MongoTemplate`; did not adopt repositories.)
  - Where: `ServerApplication` — no repository interfaces exist; all access is
    via `MongoTemplate`, so the annotation is inert.
  - Do: remove it, or migrate the two services to `MongoRepository` and drop the
    hand-built `Query`/`Criteria`.

- [x] **L2. Make `ObjectMapper` a static singleton.** (done, branch `arch/cleanup-and-caching`; both `Ensemble` and `FeatureCollectionPOJO` now hold a `private static final ObjectMapper MAPPER` reused by `toString()`.)
  - Where: `Ensemble.java:75` and `FeatureCollectionPOJO.java:51` construct
    `new ObjectMapper()` per `toString()` call.
  - Do: `private static final ObjectMapper` (thread-safe, expensive to build).

- [x] **L3. Index `states.name`.** (done, branch `arch/cleanup-and-caching`; added `@Indexed` on `Ensemble.name`. `auto-index-creation=true` in `application.properties`, so the index is created on startup.)
  - Where: `EnsembleService` queries `states` by `name` only; `Ensemble` has no
    `@Indexed` (unlike `DistrictPlan`'s compound index).
  - Do: add `@Indexed` on `Ensemble.name` (auto-index-creation is on). Small
    collection, so low urgency.

- [x] **L4. Size plan generation to available cores.** (done, branch `arch/cleanup-and-caching`; `num_cores` now derives from `SLURM_CPUS_PER_TASK` when set, else `os.cpu_count()`, falling back to 4. Left the sequential per-state loop and process-per-core model as-is — the `multiprocessing.Pool` / state-overlap change was flagged "consider" and is a larger refactor.)
  - Where: `scripts/generate_plans.py:59` hardcodes `num_cores = 4`, and
    `generate_all_plans` runs the three states strictly sequentially.
  - Do: use `os.cpu_count()` (or the Slurm-allocated count from
    `seawulf_script.slurm`) and consider a `multiprocessing.Pool` for even load
    balancing; overlap states if cores allow.

- [x] **L5. Drop `allowCredentials(true)` from CORS.** (done, branch `arch/cleanup-and-caching`; removed `.allowCredentials(true)`. Kept the `allowedOriginPatterns` for localhost/zfdupont.com rather than broadening to `*` — the port-wildcard patterns need `allowedOriginPatterns`, and restricting origins is harmless without credentials.)
  - Where: `ServerApplication:27` — the API is read-only public data with no auth
    or cookies, so credentials mode (and the origin-pattern constraint it forces)
    is unnecessary.
  - Do: remove `allowCredentials(true)`; simplify allowed origins.

## Notes / cross-cutting

- [x] Docs drift (done, branch `arch/cleanup-and-caching`): rewrote the `README.md`
  API section to the two real read-only endpoints (`GET /api/summary`,
  `GET /api/plan`) and dropped the nonexistent `GET/POST /plans`; also corrected the
  "scripts POST to the database" phrasing (they write to Mongo directly via
  `fill_database.py`), the `python main.py` run step (no such file), and the
  `DATABASE_URI` description. Deleted the vestigial JPA descriptors
  `server/META-INF/persistence.xml` **and** `server/META-INF/orm.xml` (both empty, no
  JPA references anywhere in `server/src`); the now-empty `META-INF` dir was removed.
- [x] `application.properties` admin:admin fallback (done, branch
  `arch/cleanup-and-caching`): replaced the `admin:admin@cluster0…` Atlas fallback with
  a bare `mongodb://localhost:27017/huskies` default, so no credentials live in the repo
  while local `spring-boot:run` still works against a local Mongo. Deployment still
  injects `SPRING_DATA_MONGODB_URI` via compose.

## Suggested first branch

H1 + M1 (pom cleanup, verifiably safe) and H2 (caching, biggest runtime win).
