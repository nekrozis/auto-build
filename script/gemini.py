import os
import json
import requests
import tarfile
import tempfile
import sys
import subprocess
import shutil

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
    """Download VS Code archive and extract bundled node-pty using system 'unzip'."""
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
    zip_path = os.path.join(extract_root, "vscode.zip")

    # 1. Download ZIP file
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

    print("[-] Extracting node-pty using 'unzip' command...")

    # 2. Extract specific path using 'unzip' system command
    try:
        # Corrected prefix based on user's 'tar tf' output (no top-level folder)
        zip_member_prefix = "resources/app/node_modules/node-pty/*"
        
        subprocess.run([
            "unzip", "-q", zip_path, zip_member_prefix, "-d", extract_root
        ], check=True)

    except subprocess.CalledProcessError as e:
        raise Exception(f"Unzip command failed to extract node-pty: {e}")

    # 3. Move extracted contents to the expected location
    unzip_source_dir = os.path.join(extract_root, "resources", "app", "node_modules", "node-pty")
    
    os.makedirs(target_dir, exist_ok=True)
    
    if not os.path.exists(unzip_source_dir):
        raise Exception(f"Extracted node-pty directory not found at: {unzip_source_dir}")

    for item in os.listdir(unzip_source_dir):
        src = os.path.join(unzip_source_dir, item)
        dst = os.path.join(target_dir, item)
        shutil.move(src, dst)
        
    shutil.rmtree(os.path.join(extract_root, "resources"))
    os.remove(zip_path)

    # 4. Read node-pty version from package.json
    try:
        package_json_path = os.path.join(target_dir, "package.json")
        with open(package_json_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)
            node_pty_ver = pkg.get("version", "0.0.0")
    except Exception as e:
        print(f"[Warning] Could not read node-pty package.json: {e}")

    print(f"[√] node-pty version: {node_pty_ver}")
    return vscode_ver, node_pty_ver

def generate_package_json(output_dir, gemini_ver, pty_ver):
    print("[-] Generating package.json...")
    pkg = {
        "name": "gemini-cli",
        "version": gemini_ver,
        "bin": {"gemini": "gemini.js"},
        "dependencies": {
            # Use GitHub reference to ensure the correct native build is installed later
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
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()