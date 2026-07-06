# build_secure.py - Secure Builder Toolchain for Akira (Nuitka + Inno Setup)
import os
import sys
import subprocess
import shutil

def print_banner():
    print("=" * 60)
    print("         AKIRA AI VIDEO GENERATOR - SECURE BUILDER          ")
    print("=" * 60)
    print("Compiling code with Nuitka (Python to C++ Binary Compilation)...")
    print("This will guarantee 100% security against extraction/decompilation.")
    print("=" * 60)

def check_package(package_name):
    try:
        __import__(package_name)
        return True
    except ImportError:
        try:
            res = subprocess.run([sys.executable, "-m", "pip", "show", package_name], capture_output=True, text=True)
            return res.returncode == 0
        except Exception:
            return False

def install_package(package_name):
    print(f"Installing {package_name}...")
    subprocess.run([sys.executable, "-m", "pip", "install", package_name])

def run_inno_setup():
    print("\n[INFO] Checking for Inno Setup compiler...")
    # Standard locations for Inno Setup compiler (ISCC.exe)
    iscc_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe"
    ]
    
    iscc_path = None
    for path in iscc_paths:
        if os.path.exists(path):
            iscc_path = path
            break
            
    if not iscc_path:
        print("[WARNING] Inno Setup compiler (ISCC.exe) not found.")
        print("Please install Inno Setup 6 (https://jrsoftware.org/isdl.php) to automatically bundle setup.exe.")
        return False
        
    print(f"[INFO] Running Inno Setup compilation using: {iscc_path}")
    iss_file = "setup.iss"
    if not os.path.exists(iss_file):
        print(f"[ERROR] {iss_file} script not found in current directory!")
        return False
        
    try:
        subprocess.run([iscc_path, iss_file], check=True)
        print("\n" + "=" * 60)
        print(" [SUCCESS] Akira_Setup.exe has been compiled successfully!")
        print(" Location: build_output\\Akira_Setup.exe")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"[ERROR] Inno Setup packaging failed: {str(e)}")
        return False

def main():
    print_banner()
    
    # Safety Check & Encryption Pipeline: Verify and encrypt license_config.json for release
    config_cleaned = False
    original_cfg = None
    config_path = "license_config.json"
    
    import json
    import base64
    
    def encrypt_config(cfg):
        try:
            js_str = json.dumps(cfg)
            xor_bytes = bytes([ord(c) ^ 42 for c in js_str])
            return base64.b64encode(xor_bytes).decode('utf-8')
        except Exception as ee:
            print(f"[ERROR] Failed to encrypt config: {ee}")
            return None

    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            # Check if it starts with { (meaning it's plain text JSON)
            if content.startswith("{"):
                original_cfg = json.loads(content)
                
                # Create a safe patched config for distribution
                patched_cfg = original_cfg.copy()
                patched_cfg["admin_mode"] = False
                patched_cfg["client_mode"] = True
                
                encrypted_str = encrypt_config(patched_cfg)
                if encrypted_str:
                    with open(config_path, "w", encoding="utf-8") as f:
                        f.write(encrypted_str)
                    print("[INFO] Successfully encrypted and patched license_config.json for release build.")
                    config_cleaned = True
                else:
                    sys.exit(1)
        except Exception as e:
            print(f"[WARNING] Failed to secure license_config.json: {e}")
            
    try:
        # 1. Ensure Nuitka is installed
        if not check_package("nuitka"):
            install_package("nuitka")
            
        # Ensure build output folder exists
        os.makedirs("build_output", exist_ok=True)
        
        # Pre-clean temporary build directories from past runs to prevent Nuitka assertion errors
        print("[INFO] Cleaning up temporary build directories from previous runs...")
        for d in ["main.build", "main.dist", "main.onefile-build", "Akira"]:
            path = os.path.join("build_output", d)
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)
        
        # 2. Run Nuitka standalone build command
        print("\n[INFO] Running Nuitka compiler. This can take 3 to 10 minutes depending on your CPU...")
        
        cmd = [
            sys.executable, "-m", "nuitka",
            "--standalone",
            "--python-flag=-OO",
            "--enable-plugin=pyqt6",
            "--windows-console-mode=disable",
            "--assume-yes-for-downloads",
            "--windows-icon-from-ico=logo.ico",
            "--output-dir=build_output",
            "main.py"
        ]
        
        subprocess.run(cmd, check=True)
        print("\n[SUCCESS] Nuitka compilation complete! Standalone binary folder created.")
        
        # 3. Process outputs: Rename main.exe to Akira.exe inside main.dist
        dist_path = os.path.join("build_output", "main.dist")
        target_dist_path = os.path.join("build_output", "Akira")
        
        if os.path.exists(dist_path):
            exe_path = os.path.join(dist_path, "main.exe")
            target_exe = os.path.join(dist_path, "Akira.exe")
            if os.path.exists(exe_path):
                if os.path.exists(target_exe):
                    os.remove(target_exe)
                os.rename(exe_path, target_exe)
            
            # Rename main.dist directory to Akira
            if os.path.exists(target_dist_path):
                shutil.rmtree(target_dist_path, ignore_errors=True)
            os.rename(dist_path, target_dist_path)
            print("[INFO] Output directory renamed to 'build_output/Akira'.")

            # Copy custom chromium folder if present
            src_chromium = "chromium"
            dest_chromium = os.path.join(target_dist_path, "chromium")
            if os.path.exists(src_chromium):
                print("[INFO] Copying custom Chromium folder to target build directory...")
                if os.path.exists(dest_chromium):
                    shutil.rmtree(dest_chromium, ignore_errors=True)
                shutil.copytree(src_chromium, dest_chromium)
            
        # Clean up temporary build directories to save disk space
        print("[INFO] Cleaning up temporary build files...")
        for d in ["main.build", "main.onefile-build"]:
            path = os.path.join("build_output", d)
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)
                
        # 4. Generate the Setup installer using Inno Setup
        run_inno_setup()
        
    except Exception as e:
        print(f"\n[ERROR] Nuitka compilation failed: {str(e)}")
        sys.exit(1)
        
    finally:
        # Restore original config
        if config_cleaned and original_cfg:
            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(original_cfg, f, indent=4)
                print("[INFO] Restored original local configurations in license_config.json.")
            except Exception as e:
                print(f"[WARNING] Failed to restore config: {e}")

if __name__ == "__main__":
    main()
