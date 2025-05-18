import json

# Step 1: Update daemon.json
daemon_config = {
    "live-restore": True,
    "userns-remap": "default",
    "no-new-privileges": True
}

with open("daemon.json", "w") as f:
    json.dump(daemon_config, f, indent=4)

# Step 2: Inject into Dockerfile
dockerfile_path = "Dockerfile"
dockerfile_lines = []

with open(dockerfile_path, "r") as file:
    dockerfile_lines = file.readlines()

if not any("HEALTHCHECK" in line for line in dockerfile_lines):
    dockerfile_lines.append("\nHEALTHCHECK --interval=30s --timeout=5s CMD nc -z localhost 5000 || exit 1\n")

if not any("USER appuser" in line for line in dockerfile_lines):
    dockerfile_lines.append("USER appuser\n")

with open(dockerfile_path, "w") as file:
    file.writelines(dockerfile_lines)

# Step 3: Inject limits into docker-compose.yml
compose_path = "docker-compose.yml"
with open(compose_path, "r") as file:
    lines = file.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if "web:" in line:
        new_lines.append(" deploy:\n")
        new_lines.append(" resources:\n")
        new_lines.append(" limits:\n")
        new_lines.append(" memory: 512m\n")
        new_lines.append(" cpus: '0.5'\n")

with open(compose_path, "w") as file:
    file.writelines(new_lines)

print("Hardening settings injected successfully!")
