# publish_release.py - Automated Release Pipeline for Akira
import os
import sys
import json
import re
import subprocess
import urllib.request
import urllib.parse

REPO_OWNER = "zaviyanzia-bot"
REPO_NAME = "akira_configs"
REPO_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

def load_github_token():
    token_file = "github_token.txt"
    if os.path.exists(token_file):
        with open(token_file, "r", encoding="utf-8") as f:
            token = f.read().strip()
            if token:
                return token
    print("=" * 60)
    print(" [ERROR] GitHub Personal Access Token (PAT) not found!")
    print(" Please create a classic token on GitHub with 'repo' scope:")
    print(" 1. Go to https://github.com/settings/tokens")
    print(" 2. Generate a new token (classic) with 'repo' checkbox checked.")
    print(" 3. Save the token value in a file named 'github_token.txt' in this directory.")
    print("=" * 60)
    return None

def update_iss_file(version):
    iss_file = "setup.iss"
    if not os.path.exists(iss_file):
        print(f"[ERROR] Inno Setup file '{iss_file}' not found.")
        return False
    
    with open(iss_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace AppVersion=X.X.X
    new_content = re.sub(r'(?m)^AppVersion=.*$', f"AppVersion={version}", content)
    
    with open(iss_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"[INFO] Updated {iss_file} to version {version}.")
    return True

def update_update_json(version, changelog):
    json_file = "update.json"
    if not os.path.exists(json_file):
        print(f"[ERROR] {json_file} file not found.")
        return False
    
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data["latest_version"] = version
    data["download_url"] = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/v{version}/Akira_Setup.exe"
    data["changelog"] = changelog
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Updated {json_file} configuration to version {version}.")
    return True

def compile_software():
    print("\n[INFO] Starting compiler toolchain (Nuitka + Inno Setup)...")
    if not os.path.exists("build_secure.py"):
        print("[ERROR] build_secure.py compile script not found.")
        return False
    
    # Run compiler script
    res = subprocess.run([sys.executable, "build_secure.py"], check=False)
    if res.returncode != 0:
        print("[ERROR] Compilation process failed.")
        return False
    
    setup_path = os.path.join("build_output", "Akira_Setup.exe")
    if not os.path.exists(setup_path):
        print(f"[ERROR] Compiled installer not found at: {setup_path}")
        return False
        
    print(f"[SUCCESS] Installer verified at: {setup_path}")
    return True

def make_github_request(url, method, token, data=None, headers=None):
    if headers is None:
        headers = {}
    headers.update({
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Akira-Publisher-Client"
    })
    
    req_data = None
    if data is not None:
        if isinstance(data, dict):
            req_data = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        else:
            req_data = data  # raw bytes for upload
            headers["Content-Type"] = "application/octet-stream"
            
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"[ERROR] API Request failed: {e.code} - {e.reason}")
        print(f"Details: {err_msg}")
        return None

def create_github_release(version, changelog, token):
    tag = f"v{version}"
    print(f"\n[INFO] Creating GitHub Release for {tag}...")
    release_data = {
        "tag_name": tag,
        "target_commitish": "main",
        "name": tag,
        "body": changelog,
        "draft": False,
        "prerelease": False
    }
    
    url = f"{REPO_API_URL}/releases"
    res = make_github_request(url, "POST", token, data=release_data)
    if res and "upload_url" in res:
        print(f"[SUCCESS] Created GitHub Release: {res.get('html_url')}")
        return res
    return None

def upload_release_asset(upload_url_template, token):
    setup_path = os.path.join("build_output", "Akira_Setup.exe")
    if not os.path.exists(setup_path):
        print("[ERROR] Setup file not found for upload.")
        return False
        
    # Clean template URL (e.g. "https://uploads.github.com/.../assets{?name,label}" -> "https://uploads.github.com/.../assets")
    upload_url = re.sub(r'\{\?.*?\}', '', upload_url_template)
    upload_url = f"{upload_url}?name=Akira_Setup.exe"
    
    print(f"[INFO] Uploading {setup_path} to GitHub Release...")
    with open(setup_path, "rb") as f:
        file_data = f.read()
        
    headers = {"Content-Length": str(len(file_data))}
    res = make_github_request(upload_url, "POST", token, data=file_data, headers=headers)
    if res and "id" in res:
        print("[SUCCESS] Akira_Setup.exe asset uploaded successfully!")
        return True
    return False

def push_configs_to_github():
    print("\n[INFO] Staging and pushing updated configs to GitHub...")
    git_exe = r"C:\Program Files\Git\cmd\git.exe"
    if not os.path.exists(git_exe):
        git_exe = "git" # Fallback to path if registered
        
    try:
        # Commit updated files
        subprocess.run([git_exe, "add", "update.json", "setup.iss", ".gitignore"], check=True)
        subprocess.run([git_exe, "commit", "-m", "Bump release configuration versions"], check=True)
        subprocess.run([git_exe, "push", "origin", "main"], check=True)
        print("[SUCCESS] Configurations successfully pushed to GitHub main branch!")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to push changes via Git: {e}")
        return False

def main():
    print("=" * 60)
    print("         AKIRA AUTOMATED COMPILE & RELEASE TOOL           ")
    print("=" * 60)
    
    # Verify GitHub PAT token exists
    token = load_github_token()
    if not token:
        sys.exit(1)
        
    # Load current configuration versions
    current_version = "1.0.0"
    if os.path.exists("update.json"):
        try:
            with open("update.json", "r", encoding="utf-8") as f:
                current_version = json.load(f).get("latest_version", "1.0.0")
        except:
            pass
            
    print(f"Current version listed in update.json: {current_version}")
    
    # Ask for target version
    v_parts = current_version.split(".")
    try:
        suggested_version = f"{v_parts[0]}.{v_parts[1]}.{int(v_parts[2]) + 1}"
    except:
        suggested_version = ""
        
    target_version = input(f"Enter target version to release (Suggested: {suggested_version}): ").strip()
    if not target_version:
        target_version = suggested_version
        
    if not re.match(r'^\d+\.\d+\.\d+$', target_version):
        print("[ERROR] Invalid version format. Must be like '1.0.4'. Aborting.")
        sys.exit(1)
        
    # Ask for changelog
    print("\nEnter release changelog (Press Ctrl+Z then Enter on Windows to save):")
    changelog_lines = []
    while True:
        try:
            line = input()
            changelog_lines.append(line)
        except EOFError:
            break
            
    changelog = "\n".join(changelog_lines).strip()
    if not changelog:
        changelog = "- Core optimizations and bug fixes."
        
    print(f"\nTarget Version: {target_version}")
    print(f"Changelog:\n{changelog}\n")
    
    confirm = input("Confirm compilation and release publish? (y/n): ").strip().lower()
    if confirm != 'y' and confirm != 'yes':
        print("[INFO] Build aborted.")
        sys.exit(0)
        
    # Update local project version configurations
    if not update_iss_file(target_version):
        sys.exit(1)
    if not update_update_json(target_version, changelog):
        sys.exit(1)
        
    # Compile the executable standalone setup binary
    if not compile_software():
        sys.exit(1)
        
    # Create the release on GitHub
    release_res = create_github_release(target_version, changelog, token)
    if not release_res:
        print("[ERROR] Failed to create GitHub Release. Aborting.")
        sys.exit(1)
        
    # Upload setup.exe asset to release
    upload_url = release_res.get("upload_url")
    if not upload_url or not upload_release_asset(upload_url, token):
        print("[ERROR] Failed to upload release asset. Aborting.")
        sys.exit(1)
        
    # Push updated config files back to GitHub main branch
    push_configs_to_github()
    
    print("\n" + "=" * 60)
    print(" [RELEASE COMPLETED] Version v%s is now live!" % target_version)
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
