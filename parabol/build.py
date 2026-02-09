import subprocess
import tempfile
import shutil
import os
import json
import re

REPO = "https://github.com/ParabolInc/parabol.git"
ENV_PATH = "./.env"
BASE_IMAGE = "parabol:base"
IMAGE = "parabol:local"
LOCAL_DOCKERFILE = os.path.abspath("setup.dockerfile")

def replace_line(path, key, replacement):
    pattern = re.compile(rf"^\s*#?\s*{re.escape(key)}=.*$")
    replaced = False
    out_lines = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if pattern.match(line):
                out_lines.append(replacement + "\n")
                replaced = True
            else:
                out_lines.append(line)

    if not replaced:
        out_lines.append(replacement + "\n")

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)

def run(cmd, env=None):
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True, env=env)

tmp = tempfile.mkdtemp(prefix="parabol-build-", dir=os.path.expanduser("~"))
print("tmp:", tmp)

try:
    # clone repo
    run(["git", "clone", "--depth", "1", REPO, tmp])

    with open(os.path.join(tmp, "package.json")) as f:
        pkg = json.load(f)

    node_version = pkg["engines"]["node"].lstrip("^")
    print("node version:", node_version)

    sha = subprocess.check_output(
        ["git", "-C", tmp, "rev-parse", "HEAD"],
        text=True
    ).strip()

    # build JS
    run([
        "docker", "run", "--rm",
        "-v", f"{tmp}:/app",
        "-w", "/app",
        "node:22-trixie-slim",
        "bash", "-c",
        "apt-get update && apt-get install -y git && "
        "corepack enable && "
        "pnpm install --frozen-lockfile && "
        "pnpm build"
    ])

    env = os.environ.copy()
    env["DOCKER_BUILDKIT"] = "1"

    # build upstream base image
    run([
        "docker", "build",
        "--build-arg", f"_NODE_VERSION={node_version}",
        "--build-arg", f"DD_GIT_COMMIT_SHA={sha}",
        "--build-arg", f"DD_GIT_REPOSITORY_URL={REPO}",
        "-f", os.path.join(tmp, "docker/images/parabol-ubi/dockerfiles/basic.dockerfile"),
        "-t", BASE_IMAGE,
        tmp
    ], env=env)

    # build your local extension Dockerfile
    run([
        "docker", "build",
        "-f", LOCAL_DOCKERFILE,
        "-t", IMAGE,
        tmp
    ])

    print("Built image:", IMAGE)

    cid = subprocess.check_output(
        ["docker", "create", IMAGE],
        text=True
    ).strip()

    run(["docker", "cp", f"{cid}:/home/node/parabol/.env.example", "./.env"])
    run(["docker", "rm", cid])

    replace_line(ENV_PATH, "# IS_ENTERPRISE", "IS_ENTERPRISE=true")
    replace_line(ENV_PATH, "HOST=", "HOST='10.127.80.126'")
    replace_line(ENV_PATH, "PROTO=", "PROTO='http'")

finally:
    shutil.rmtree(tmp, ignore_errors=True)
