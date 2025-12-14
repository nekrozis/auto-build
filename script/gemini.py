import os
import json
import requests
import zipfile
import tarfile
import tempfile
import sys

# ================= Configuration =================
GEMINI_REPO = "google-gemini/gemini-cli"
VSCODE_API_URL = "https://update.code.visualstudio.com/api/update/win32-x64-archive/stable/latest"
OUTPUT_FILENAME = "gemini-cli-dist.tgz"
# =================================================

def set_github_output(key, value):
    """Write output variables for GitHub Actions"""
    print(f"[Info] Set Action output: {key}={value}")
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"{key}={value}\n")

def get_gemini_cli(repo_slug, save_dir):
    print(f"[-] Fetching latest release of {repo_slug}...")
    api_url = f"https://api.github.com/repos/{repo_slug}/releases/latest"
    headers = {"Accept": "application/vnd.github.v3+json"}

    resp = requests.get(api_url, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    version = data["tag_name"].lstrip("v")
    print(f"[√] Gemini CLI version: {version}")

    download_url = None
    for asset in data.get("assets", []):
        if asset["name"] == "gemini.js":
            download_url = asset["browser_download_url"]
            break

    if not download_url:
        raise Exception(f"gemini.js not found in release {version}")

    print("[-] Downloading gemini.js...")
    file_resp = requests.get(download_url)
    file_resp.raise_for_status()

    dest_path = os.path.join(save_dir, "gemini.js")
    with open(dest_path, "wb") as f:
        f.write(file_resp.content)

    return version

def get_vscode_node_pty(extract_root):
    """Download VS Code archive and extract bundled node-pty"""
    print("[-] Checking latest VS Code version...")

    resp = requests.get(VSCODE_API_URL)
    resp.raise_for_status()
    ver_data = resp.json()

    vscode_ver = ver_data.get("name") or ver_data.get("productVersion")
    download_url = f"https://update.code.visualstudio.com/{vscode_ver}/win32-x64-archive/stable"

    print(f"[√] VS Code version: {vscode_ver}")
    print("[-] Downloading VS Code archive...")

    node_pty_ver = "0.0.0"
    target_dir = os.path.join(extract_root, "node_modules", "node-pty")

    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with tempfile.TemporaryFile() as tmp_file:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                tmp_file.write(chunk)

            print("[-] Extracting node-pty...")
            tmp_file.seek(0)

            with zipfile.ZipFile(tmp_file) as z:
                members = [
                    m for m in z.namelist()
                    if "resources/app/node_modules/node-pty/" in m
                ]
                if not members:
                    raise Exception("node-pty not found in VS Code archive")

                for member in members:
                    split_path = member.split("node_modules/node-pty/")
                    if len(split_path) < 2 or not split_path[1]:
                        continue

                    rel_path = split_path[1]
                    dest_file_path = os.path.join(target_dir, rel_path)
                    os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)

                    content = z.read(member)
                    with open(dest_file_path, "wb") as f:
                        f.write(content)

                    if rel_path == "package.json":
                        pkg = json.loads(content)
                        node_pty_ver = pkg.get("version", "0.0.0")

    print(f"[√] node-pty version: {node_pty_ver}")
    return vscode_ver, node_pty_ver

def generate_package_json(output_dir, gemini_ver, pty_ver):
    print("[-] Generating package.json...")
    pkg = {
        "name": "gemini-cli",
        "version": gemini_ver,
        "bin": {"gemini": "gemini.js"},
        "dependencies": {
            "node-pty": f"github:microsoft/node-pty#v{pty_ver}"
        },
    }

    with open(os.path.join(output_dir, "package.json"), "w", encoding="utf-8") as f:
        json.dump(pkg, f, indent=2)

def pack_tgz(source_dir, filename):
    print(f"[-] Packing archive: {filename}")
    with tarfile.open(filename, "w:gz") as tar:
        tar.add(source_dir, arcname=".")
    print("[√] Archive created.")

def main():
    try:
        with tempfile.TemporaryDirectory() as work_dir:
            print(f"[-] Working directory: {work_dir}")

            gemini_ver = get_gemini_cli(GEMINI_REPO, work_dir)
            vscode_ver, pty_ver = get_vscode_node_pty(work_dir)
            generate_package_json(work_dir, gemini_ver, pty_ver)

            set_github_output("GEMINI_VERSION", gemini_ver)
            set_github_output("VSCODE_VERSION", vscode_ver)
            set_github_output("NODEPTY_VERSION", pty_ver)

            output_path = os.path.join(os.getcwd(), OUTPUT_FILENAME)
            pack_tgz(work_dir, output_path)

            print("\n" + "=" * 30)
            print("Summary:")
            print(f"Gemini CLI: {gemini_ver}")
            print(f"VS Code:    {vscode_ver}")
            print(f"node-pty:   {pty_ver}")
            print(f"Artifact:   {output_path}")
            print("=" * 30)

    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
