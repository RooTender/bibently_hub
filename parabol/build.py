import subprocess
import tempfile
import shutil
import os
import json

REPO = "https://github.com/ParabolInc/parabol.git"
ENV_PATH = "./.env"
COMPOSE_PATH = "./docker-compose.yaml"

BASE_IMAGE = "parabol:base"
IMAGE = "parabol:local"
LOCAL_DOCKERFILE = os.path.abspath("injector.dockerfile")

ip = input("IP address for build: ").strip()
port = input("Port: ").strip()

def run(cmd, env=None):
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True, env=env)

def patch_env(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    def replace(key, value):
        nonlocal lines
        new = []
        for line in lines:
            if line.strip().startswith(key):
                new.append(f"{key}='{value}'\n")
            else:
                new.append(line)
        lines = new

    replace("HOST", ip)
    replace("PORT", port)
    replace("PROTO", "http")
    replace("CDN_BASE_URL", f"//{ip}:{port}")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

tmp = tempfile.mkdtemp(prefix="parabol-build-", dir=os.path.expanduser("~"))
print("tmp:", tmp)

try:
    run(["git", "clone", "--depth", "1", REPO, tmp])

    with open(os.path.join(tmp, "package.json")) as f:
        pkg = json.load(f)

    node_version = pkg["engines"]["node"].lstrip("^")
    print("node version:", node_version)

    sha = subprocess.check_output(
        ["git", "-C", tmp, "rev-parse", "HEAD"],
        text=True
    ).strip()

    env_example = os.path.join(tmp, ".env.example")
    env_real = os.path.join(tmp, ".env")
    shutil.copy(env_example, env_real)
    patch_env(env_real)

    run([
        "docker", "run", "--rm",
        "-v", f"{tmp}:/app",
        "--env-file", env_real,
        "-w", "/app",
        "node:22-trixie-slim",
        "bash", "-c",
        "apt-get update && "
        "DEBIAN_FRONTEND=noninteractive apt-get install -y git python3 build-essential && "
        "corepack enable && "
        "pnpm install --frozen-lockfile && "
        "pnpm build"
    ])


    env = os.environ.copy()
    env["DOCKER_BUILDKIT"] = "1"

    run([
        "docker", "build",
        "--build-arg", f"_NODE_VERSION={node_version}",
        "--build-arg", f"DD_GIT_COMMIT_SHA={sha}",
        "--build-arg", f"DD_GIT_REPOSITORY_URL={REPO}",
        "-f", os.path.join(tmp, "docker/images/parabol-ubi/dockerfiles/basic.dockerfile"),
        "-t", BASE_IMAGE,
        tmp
    ], env=env)

    run([
        "docker", "build",
        "-f", LOCAL_DOCKERFILE,
        "-t", IMAGE,
        tmp
    ])

    print("Built image:", IMAGE)

    shutil.copy(env_real, ENV_PATH)
    print("Saved .env to project directory")

finally:
    shutil.rmtree(tmp, ignore_errors=True)

def patch_compose(ip, port):
    with open(COMPOSE_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "ports:" in line:
            indent = len(line) - len(line.lstrip(" "))
            new_indent = " " * (indent + 2)
            lines[i + 1] = f'{new_indent}- "{ip}:{port}:{port}"\n'
            break

    with open(COMPOSE_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

patch_compose(ip, port)
print("docker-compose.yaml patched")
