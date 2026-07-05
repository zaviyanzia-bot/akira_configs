# compress_logo.py - Helper script to resize, crop, mask and encode user's large logo
import os
import sys
import base64
import subprocess

def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package])

def main():
    workspace = os.path.dirname(os.path.abspath(__file__))
    input_name = "my_new_logo.png"  # Default name for user's file
    
    # Try to find any large png file in workspace if my_new_logo.png doesn't exist
    input_path = os.path.join(workspace, input_name)
    if not os.path.exists(input_path):
        # Look for any png file larger than 1MB
        png_files = [f for f in os.listdir(workspace) if f.lower().endswith(".png") and f not in ["logo.png"]]
        for f in png_files:
            fp = os.path.join(workspace, f)
            if os.path.getsize(fp) > 500 * 1024:  # > 500KB
                input_path = fp
                print(f"[INFO] Found large logo file to process: {f}")
                break
                
    if not os.path.exists(input_path):
        print(f"[ERROR] Could not find your new logo file!")
        print(f"Please copy your 7MB logo into this folder and rename it to: '{input_name}'")
        return
        
    print("[INFO] Loading PIL (Pillow) to compress image...")
    install_and_import("pillow")
    from PIL import Image, ImageDraw
    
    try:
        # 1. Open image
        img = Image.open(input_path)
        w, h = img.size
        
        # 2. Crop to square first
        size = min(w, h)
        left = (w - size) // 2
        top = (h - size) // 2
        img_square = img.crop((left, top, left + size, top + size))
        
        # 3. Crop 10.5% from each side to remove the outer double-line border
        margin = int(size * 0.105)
        img_cropped = img_square.crop((margin, margin, size - margin, size - margin))
        c_size = img_cropped.size[0]
        
        # 4. Create a rounded square mask (squircle)
        mask = Image.new("L", (c_size, c_size), 0)
        draw = ImageDraw.Draw(mask)
        
        # Corner radius for a perfect squircle
        r = int(c_size * 0.20)
        draw.rounded_rectangle((0, 0, c_size, c_size), radius=r, fill=255)
        
        # Apply the mask to make the background outside the squircle fully transparent
        img_transparent = Image.new("RGBA", (c_size, c_size), (0, 0, 0, 0))
        img_transparent.paste(img_cropped, (0, 0), mask=mask)
        
        # 5. Resize to high-quality 256x256
        img_final = img_transparent.resize((256, 256), Image.Resampling.LANCZOS)
        
        # 6. Save compressed PNG
        dest_png = os.path.join(workspace, "logo.png")
        img_final.save(dest_png, format="PNG", optimize=True)
        print(f"[SUCCESS] Compressed and saved to: logo.png (Size: {os.path.getsize(dest_png)/1024:.1f} KB)")
        
        # 7. Save as ICO
        dest_ico = os.path.join(workspace, "logo.ico")
        img_final.save(dest_ico, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print(f"[SUCCESS] Generated app icon: logo.ico")
        
        # 8. Generate base64 for logo_data.py
        with open(dest_png, "rb") as f:
            b64_str = base64.b64encode(f.read()).decode("utf-8")
            
        logo_data_py = os.path.join(workspace, "logo_data.py")
        user_avatar_content = ""
        if os.path.exists(logo_data_py):
            with open(logo_data_py, "r", encoding="utf-8") as f:
                for line in f:
                    if "USER_AVATAR_B64 =" in line:
                        user_avatar_content = line.strip()
                        break

        with open(logo_data_py, "w", encoding="utf-8") as f:
            f.write("# logo_data.py - Embedded Base64 Images\n")
            f.write(f'LOGO_PNG_B64 = "{b64_str}"\n')
            if user_avatar_content:
                f.write(user_avatar_content + "\n")
        print(f"[SUCCESS] Embedded inside code: logo_data.py")
        
        print("\n" + "="*50)
        print(" Logo successfully updated and optimized for build!")
        print("="*50)
        
    except Exception as e:
        print(f"[ERROR] Failed to process logo: {str(e)}")

if __name__ == "__main__":
    main()
