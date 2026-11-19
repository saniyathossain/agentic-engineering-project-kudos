#!/bin/sh
# Security audit: dependencies, Dockerfile/compose misconfiguration, committed secrets and image vulnerabilities.
# Needs Docker. Exits non-zero on the first failing check so CI can use it. Run: make audit
set -eu
cd "$(dirname "$0")/.."
TRIVY="docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v kudos-trivy-cache:/root/.cache -v $PWD:/repo:ro -w /repo aquasec/trivy:latest"
SEVERITY="${AUDIT_SEVERITY:-HIGH,CRITICAL}"

step() { printf '\n== %s\n' "$1"; }

step "composer audit (PHP dependencies)"
docker run --rm --entrypoint sh -v "$PWD/codes:/app" -w /app kudos-app -c "composer audit --locked"

step "npm audit (JavaScript dependencies)"
docker run --rm -v "$PWD/codes:/app" -w /app node:26-alpine sh -c "npm audit --audit-level=moderate"

step "Dockerfile and compose misconfiguration"
$TRIVY config --severity "$SEVERITY" --exit-code 1 --skip-files docker/Dockerfile.dockerignore docker

step "secrets committed to the repository"
$TRIVY fs --scanners secret --exit-code 1 --skip-dirs codes/vendor,codes/node_modules,.git,docker/.envs/secrets .

step "image vulnerabilities (build first: make prod)"
for image in kudos-app:prod kudos-edge:prod kudos-db:prod; do
  printf '\n-- %s\n' "$image"
  $TRIVY image --scanners vuln --severity "$SEVERITY" --ignore-unfixed --exit-code 1 "$image"
done

printf '\nAll audits passed.\n'
