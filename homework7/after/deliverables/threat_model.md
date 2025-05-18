# Threat Model for Containerized Flask App

## STRIDE Analysis

| Threat Type | Where It Applies | Risk | Mitigation |
|-------------|------------------|------|------------|
| Spoofing | Passwords in `.env` used for login | Medium | Use secure secrets management (`.env`, avoid hardcoded creds) |
| Tampering | User input to `/ping` or `/calculate` | High | Input validation, no `eval()`, IP regex check |
| Repudiation | No access logging in Flask | Low | Add logging or reverse proxy logs |
| Information Disclosure | Exposed secrets or code in image | High | Use `.env`, do not bake credentials into Dockerfile |
| Denial of Service | No memory or PID limits on containers | High | `mem_limit`, `pids_limit` in `docker-compose.yml` |
| Elevation of Privilege | App running as root | High | Use `USER appuser`, `security_opt: no-new-privileges:true` |

## MITRE ATT&CK for Containers

| Technique ID | Technique Name | Description | Relevance |
|--------------|----------------|-------------|-----------|
| T1611 | Escape to Host | Attacker tries to break out of container to access host | Prevented with `USER appuser`, no-new-privileges |
| T1204 | User Execution | Trick user into running malicious input | Mitigated by strict input validation in `/ping` and `/calculate` |
| T1525 | Implant Internal Image | Upload or use infected image | Avoided by using official Python base image (`python:3.11-slim`) |
| T1609 | Container Administration Command | Attacker executes commands inside container | Hardened via `read_only`, PID/mem limits, and restricted user |
| T1610 | Deploy Container | Adversary deploys their own container | Controlled by Docker daemon access permissions |

## Vulnerability to Control Mapping (NIST 800-53)

| Vulnerability | Control ID | Control Description |
|---------------|------------|---------------------|
| Hardcoded passwords | AC-6, IA-5 | Enforce least privilege; use proper password handling |
| Code injection via `/ping` | SI-10, SC-39 | Input validation; restrict execution environment |
| Resource exhaustion (DoS) | SC-5, SC-6 | Limit system resources (memory, CPU, PIDs) |
| Container breakout risk | SC-30, SC-31 | Enforce least privilege and strong isolation |
| Sensitive data exposure | SC-12, SC-28 | Protect data at rest and in container files |
cd ~/seas-8405/week-7/homework7/before

ls
