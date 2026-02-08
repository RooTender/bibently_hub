import subprocess
import tempfile
import shutil
import os
import json

REPO = "https://github.com/ParabolInc/parabol.git"
ENV_PATH = "./.env"
IMAGE = "parabol:local"
LOCAL_DOCKERFILE = os.path.abspath("setup.dockerfile")


def replace_line(path, needle, replacement):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    out = []
    replaced = False

    for line in lines:
        if needle in line:
            out.append(replacement + "\n")
            replaced = True
        else:
            out.append(line)

    if not replaced:
        out.append(replacement + "\n")

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(out)


def run(cmd, env=None):
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True, env=env)


tmp = tempfile.mkdtemp(prefix="parabol-build-", dir=os.path.expanduser("~"))
print("tmp:", tmp)

try:
    # clone repo
    run(["git", "clone", "--depth", "1", REPO, tmp])

    # prepare .env
    env_example = os.path.join(tmp, ".env.example")
    shutil.copyfile(env_example, ENV_PATH)

    replace_line(ENV_PATH, "# IS_ENTERPRISE", "IS_ENTERPRISE=true")
    replace_line(ENV_PATH, "HOST=", "HOST='10.127.80.126'")
    replace_line(ENV_PATH, "PROTO=", "PROTO='http'")
    replace_line(ENV_PATH, "PORT=", "PORT='80'")
    replace_line(ENV_PATH, "CDN_BASE_URL=", "CDN_BASE_URL='//10.127.80.126/parabol'")

    shutil.copyfile(ENV_PATH, os.path.join(tmp, ".env"))

    with open(os.path.join(tmp, "package.json")) as f:
        pkg = json.load(f)

    node_version = pkg["engines"]["node"].lstrip("^")
    print("node version:", node_version)

    env = os.environ.copy()
    env["DOCKER_BUILDKIT"] = "1"

    # single docker build (does everything)
    run([
        "docker", "build",
        "--build-arg", f"_NODE_VERSION={node_version}",
        "--build-arg", "PUBLIC_URL=/parabol",
        "--build-arg", "CDN_BASE_URL=//10.127.80.126/parabol",
        "-f", LOCAL_DOCKERFILE,
        "-t", IMAGE,
        tmp
    ], env=env)

    print("Built image:", IMAGE)

finally:
    shutil.rmtree(tmp, ignore_errors=True)
