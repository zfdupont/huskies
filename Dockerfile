# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
# Resolve dependencies in their own layer so a source-only change doesn't
# re-download the whole dependency tree; this layer is cached until pom.xml changes.
COPY server/pom.xml ./pom.xml
RUN mvn -q -B dependency:go-offline
COPY server/src ./src
RUN mvn -q -B clean package -DskipTests

FROM eclipse-temurin:17-jre
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -r -u 1001 appuser
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
USER appuser
EXPOSE 8090
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8090/actuator/health || exit 1
ENTRYPOINT ["java","-jar","/app/app.jar"]
